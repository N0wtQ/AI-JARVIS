"""
Telegram Bot for JARVIS
Conecta JARVIS con Telegram para recibir y responder mensajes
"""

import os
import asyncio
import logging
import threading
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from .channel_manager import get_channel_manager

# Importar winsdk para notificaciones de Windows
try:
    from winsdk.windows.ui.notifications.management import UserNotificationListener
    from winsdk.windows.ui.notifications import NotificationKinds
    WINSDK_AVAILABLE = True
except ImportError:
    WINSDK_AVAILABLE = False
    print("⚠️ winsdk no disponible. Instala con: pip install winsdk")

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


class WindowsNotificationWatcher:
    """Observa las notificaciones de Windows y las envía a Telegram."""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.seen_notifications = set()
        self.running = False
        self._task = None
    
    async def get_notifications(self):
        """Obtiene las notificaciones actuales."""
        if not WINSDK_AVAILABLE:
            return []
        
        try:
            listener = UserNotificationListener.current
            access = await listener.request_access_async()
            
            if access.value != 0:  # 0 = Allowed
                return []
            
            notifications = await listener.get_notifications_async(NotificationKinds.TOAST)
            return notifications
        except Exception as e:
            logger.error(f"Error obteniendo notificaciones: {e}")
            return []
    
    def format_notification(self, notification) -> str:
        """Formatea una notificación para Telegram."""
        try:
            app_info = notification.app_info
            app_name = app_info.display_info.display_name if app_info else "Sistema"
            
            toast = notification.notification
            visual = toast.visual
            binding = visual.get_binding("ToastGeneric") if visual else None
            
            title = ""
            body = ""
            
            if binding:
                text_elements = binding.get_text_elements()
                texts = [t.text for t in text_elements if t.text]
                if texts:
                    title = texts[0] if len(texts) > 0 else ""
                    body = "\n".join(texts[1:]) if len(texts) > 1 else ""
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            message = f"🔔 <b>{app_name}</b>\n"
            if title:
                message += f"<b>{title}</b>\n"
            if body:
                message += f"{body}\n"
            message += f"\n🕐 {timestamp}"
            
            return message
        except Exception as e:
            return f"🔔 Nueva notificación (error al parsear: {e})"
    
    async def send_to_telegram(self, message: str):
        """Envía mensaje a los usuarios permitidos de Telegram."""
        if not self.bot.application:
            return
        
        for user_id in self.bot.allowed_users:
            try:
                await self.bot.application.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Error enviando notificación a {user_id}: {e}")
    
    async def watch_loop(self):
        """Loop principal de observación."""
        logger.info("👀 Monitor de notificaciones de Windows iniciado")
        
        # Esperar a que el bot esté listo
        await asyncio.sleep(5)
        
        while self.running:
            try:
                notifications = await self.get_notifications()
                
                for notif in notifications:
                    notif_id = notif.id
                    
                    if notif_id not in self.seen_notifications:
                        self.seen_notifications.add(notif_id)
                        message = self.format_notification(notif)
                        await self.send_to_telegram(message)
                        logger.info(f"📤 Notificación enviada a Telegram")
                
                # Limpiar notificaciones antiguas
                if len(self.seen_notifications) > 100:
                    self.seen_notifications = set(list(self.seen_notifications)[-50:])
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error en watch_loop: {e}")
                await asyncio.sleep(5)
    
    def start(self, loop):
        """Inicia el observador en el loop dado."""
        if not WINSDK_AVAILABLE:
            logger.warning("Monitor de notificaciones no disponible (winsdk no instalado)")
            return
        
        if not self.bot.allowed_users:
            logger.warning("Monitor de notificaciones: No hay usuarios configurados en TELEGRAM_ALLOWED_USERS")
            return
        
        self.running = True
        self._task = loop.create_task(self.watch_loop())
        logger.info("✅ Monitor de notificaciones de Windows activo")
    
    def stop(self):
        """Detiene el observador."""
        self.running = False
        if self._task:
            self._task.cancel()


class TelegramBot:
    """Bot de Telegram para JARVIS"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("TELEGRAM_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN no encontrado. Configúralo en .env")
        
        self.channel_manager = get_channel_manager()
        self.application: Optional[Application] = None
        self.allowed_users: list = self._load_allowed_users()
        self.notification_watcher: Optional[WindowsNotificationWatcher] = None
        
    def _load_allowed_users(self) -> list:
        """Carga lista de usuarios permitidos (si existe)"""
        allowed = os.getenv("TELEGRAM_ALLOWED_USERS", "")
        if allowed:
            return [int(uid.strip()) for uid in allowed.split(",") if uid.strip()]
        return []  # Lista vacía = todos permitidos
    
    def _is_user_allowed(self, user_id: int) -> bool:
        """Verifica si un usuario está permitido"""
        if not self.allowed_users:
            return True  # Si no hay lista, todos permitidos
        return user_id in self.allowed_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /start"""
        user = update.effective_user
        
        if not self._is_user_allowed(user.id):
            await update.message.reply_text(
                "🚫 *ACCESO DENEGADO*\n\n"
                "No tienes permiso para utilizar este BOT.",
                parse_mode='Markdown'
            )
            logger.warning(f"Acceso denegado a usuario: {user.first_name} ({user.id})")
            return
        
        welcome_message = (
            f"👋 ¡Hola {user.first_name}!\n\n"
            "Soy **JARVIS**, tu asistente personal de IA.\n\n"
            "Puedo ayudarte con:\n"
            "• 💬 Conversación general\n"
            "• 🌤️ Consultar el clima\n"
            "• 🔍 Búsquedas en internet\n"
            "• 🧮 Cálculos matemáticos\n"
            "• 📚 Consultar mi base de conocimiento\n"
            "• ℹ️ Información del sistema\n\n"
            "Simplemente escríbeme lo que necesites.\n\n"
            "Comandos disponibles:\n"
            "/start - Este mensaje\n"
            "/status - Estado del sistema\n"
            "/clear - Limpiar historial de conversación\n"
            "/help - Ayuda"
        )
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"Usuario {user.first_name} ({user.id}) inició el bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /help"""
        help_text = (
            "🤖 **Comandos de JARVIS**\n\n"
            "/start - Mensaje de bienvenida\n"
            "/status - Ver estado del sistema\n"
            "/clear - Limpiar historial de chat\n"
            "/memory - Ver memoria guardada\n"
            "/help - Esta ayuda\n\n"
            "**Ejemplos de uso:**\n"
            "• \"¿Qué tiempo hace en Madrid?\"\n"
            "• \"Busca información sobre Python\"\n"
            "• \"¿Cuánto es 25 * 37?\"\n"
            "• \"¿Cuál es mi IP?\"\n\n"
            "⚠️ Nota: Algunas acciones (abrir apps, controlar PC) "
            "solo funcionan en el PC local."
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /status"""
        user = update.effective_user
        
        if not self._is_user_allowed(user.id):
            await update.message.reply_text(
                "🚫 *ACCESO DENEGADO*\n\n"
                "No tienes permiso para utilizar este BOT.",
                parse_mode='Markdown'
            )
            return
        
        status_text = (
            "📊 **Estado de JARVIS**\n\n"
            "✅ Bot de Telegram: Activo\n"
            "✅ AI Handler: Conectado\n"
            f"📝 Canales activos: {len(self.channel_manager.channels)}\n"
        )
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /clear"""
        user = update.effective_user
        
        if not self._is_user_allowed(user.id):
            await update.message.reply_text(
                "🚫 *ACCESO DENEGADO*\n\n"
                "No tienes permiso para utilizar este BOT.",
                parse_mode='Markdown'
            )
            return
        
        self.channel_manager.clear_history()
        await update.message.reply_text("🗑️ Historial de conversación limpiado.")
        logger.info(f"Usuario {user.first_name} ({user.id}) limpió el historial")
    
    async def memory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /memory"""
        user = update.effective_user
        
        if not self._is_user_allowed(user.id):
            await update.message.reply_text(
                "🚫 *ACCESO DENEGADO*\n\n"
                "No tienes permiso para utilizar este BOT.",
                parse_mode='Markdown'
            )
            return
        
        memory = self.channel_manager.get_memory()
        
        if not memory or all(not v for v in memory.values()):
            await update.message.reply_text("📭 No hay memoria guardada.")
            return
        
        memory_text = "🧠 **Memoria de JARVIS**\n\n"
        
        if memory.get("identity"):
            memory_text += "**Identidad:**\n"
            for key, value in memory["identity"].items():
                memory_text += f"  • {key}: {value}\n"
        
        if memory.get("preferences"):
            memory_text += "\n**Preferencias:**\n"
            for key, value in memory["preferences"].items():
                memory_text += f"  • {key}: {value}\n"
        
        if memory.get("relationships"):
            memory_text += "\n**Relaciones:**\n"
            for rel in memory["relationships"]:
                memory_text += f"  • {rel.get('name', '?')}: {rel.get('relation', '?')}\n"
        
        await update.message.reply_text(memory_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja mensajes de texto normales"""
        user = update.effective_user
        message_text = update.message.text
        
        # Verificar permisos
        if not self._is_user_allowed(user.id):
            await update.message.reply_text(
                "🚫 *ACCESO DENEGADO*\n\n"
                "No tienes permiso para utilizar este BOT.",
                parse_mode='Markdown'
            )
            logger.warning(f"Acceso denegado a usuario: {user.first_name} ({user.id})")
            return
        
        # Mostrar indicador de "escribiendo..."
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Procesar mensaje a través del Channel Manager
        response = self.channel_manager.process_message(
            message=message_text,
            channel="telegram",
            user_id=str(user.id),
            user_name=user.first_name or "Usuario"
        )
        
        # Enviar respuesta (dividir si es muy larga)
        if len(response) > 4096:
            # Telegram tiene límite de 4096 caracteres
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja errores"""
        logger.error(f"Error: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Ocurrió un error procesando tu mensaje. Intenta de nuevo."
            )
    
    def run(self):
        """Inicia el bot de Telegram"""
        print("🤖 Iniciando bot de Telegram...")
        print(f"   Token: {self.token[:20]}...")
        
        if self.allowed_users:
            print(f"   Usuarios permitidos: {self.allowed_users}")
        else:
            print("   ⚠️ Todos los usuarios pueden usar el bot")
        
        # Crear aplicación
        self.application = Application.builder().token(self.token).build()
        
        # Registrar handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        self.application.add_handler(CommandHandler("memory", self.memory_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Registrar error handler
        self.application.add_error_handler(self.error_handler)
        
        # Registrar en el channel manager
        self.channel_manager.register_channel("telegram", self)
        
        print("✅ Bot de Telegram iniciado!")
        print("   Envía un mensaje a @XarCrystal_Bot para probar")
        print("   Presiona Ctrl+C para detener\n")
        
        # Iniciar monitor de notificaciones de Windows
        if WINSDK_AVAILABLE and self.allowed_users:
            self.notification_watcher = WindowsNotificationWatcher(self)
            # Obtener el loop del bot y programar el watcher
            loop = asyncio.get_event_loop()
            self.notification_watcher.start(loop)
            print("🔔 Monitor de notificaciones de Windows activo")
        
        # Iniciar polling
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def start_telegram_bot(token: Optional[str] = None):
    """Función helper para iniciar el bot"""
    bot = TelegramBot(token)
    bot.run()


if __name__ == "__main__":
    start_telegram_bot()
