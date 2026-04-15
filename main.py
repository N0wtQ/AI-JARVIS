"""
AI Assistant with Animated JARVIS Face
Main application file with visual interface - PySide6 version
With intent-based actions support
"""

import sys
import threading
import time
import random
import math
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QFileDialog)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, Slot, QThread
from PySide6.QtGui import QPixmap, QImage, QPainter, QFont, QIcon
from PIL import Image, ImageDraw, ImageFilter, ImageTk
from ai_handler import AIHandler
from speech_handler import SpeechHandler
from voice_player import VoicePlayer
from actions.open_app import open_app, open_url
from actions.web_search import web_search
from actions.weather_report import get_weather
from actions.spotify_control import spotify_control
from actions.wolfram_query import query_wolfram
from actions.system_info import get_system_status_text, get_public_ip, get_private_ip, get_ram_info, get_cpu_info, get_disk_info
from actions.flight_radar import open_flight_radar
from actions.volume_control import volume_control
from actions.run_command import run_command, open_terminal
from actions.system_control import system_control
from actions.file_organizer import organize_files
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WorkerSignals(QObject):
    """Signals for worker threads"""
    message_ready = Signal(str, str)
    error = Signal(str)
    voice_input_ready = Signal(str)
    state_changed = Signal(str)  # Señal para cambiar el estado visual
    rag_sources_ready = Signal(list)  # Señal para mostrar fuentes RAG
    wake_word_detected = Signal()  # Señal para wake word detectado
    finished_processing = Signal()  # Señal cuando termina de procesar


class AIWorkerThread(QThread):
    """Worker thread for AI processing with intent handling"""
    def __init__(self, ai_handler, message, use_voice_output=False):
        super().__init__()
        self.ai_handler = ai_handler
        self.message = message
        self.use_voice_output = use_voice_output
        self.signals = WorkerSignals()
        
    def run(self):
        try:
            # 🧠 Estado: PENSANDO
            self.signals.state_changed.emit(AssistantState.THINKING)
            
            # Get response with intent parsing
            result = self.ai_handler.get_response(self.message)
            
            intent = result.get("intent", "chat")
            parameters = result.get("parameters", {})
            text_response = result.get("text", "Sin respuesta")
            rag_sources = result.get("rag_sources", [])
            
            # Emit RAG sources if available
            if rag_sources:
                self.signals.rag_sources_ready.emit(rag_sources)
            
            # Process intent and execute action
            action_result = self._process_intent(intent, parameters)
            
            # Combine AI response with action result if applicable
            if action_result:
                # Si hay error, solo mostrar el error
                if "Error" in action_result or "error" in action_result.lower():
                    final_response = action_result
                else:
                    final_response = f"{text_response}\n{action_result}"
            else:
                final_response = text_response
            
            # 💬 Estado: RESPONDIENDO
            self.signals.state_changed.emit(AssistantState.RESPONDING)
            self.signals.message_ready.emit("JARVIS", final_response)
            
            if self.use_voice_output:
                voice_player = VoicePlayer()
                # Leer la respuesta completa incluyendo resultados de acciones
                voice_player.speak(final_response)
            
            # Volver a IDLE después de responder
            time.sleep(0.5)
            self.signals.state_changed.emit(AssistantState.IDLE)
            self.signals.finished_processing.emit()
                
        except Exception as e:
            self.signals.state_changed.emit(AssistantState.IDLE)
            self.signals.finished_processing.emit()
            self.signals.error.emit(f"Error: {str(e)}")
    
    # Acciones que requieren confirmación
    DANGEROUS_ACTIONS = {
        "pc_control": ["shutdown", "restart", "sleep", "hibernate", "empty_trash"],
    }
    
    def _process_intent(self, intent: str, parameters: dict) -> str:
        """Process intent and execute corresponding action"""
        try:
            # Debug logging
            print(f"🎯 Intent detectado: {intent}")
            print(f"📦 Parámetros: {parameters}")
            
            # Verificar si es una confirmación de acción pendiente
            if intent == "confirm_action":
                confirmed = parameters.get("confirmed", False)
                if confirmed and self.ai_handler.pending_action:
                    # Ejecutar la acción pendiente
                    pending = self.ai_handler.pending_action
                    self.ai_handler.pending_action = None
                    print(f"✅ Ejecutando acción confirmada: {pending}")
                    return self._execute_action(pending["intent"], pending["parameters"])
                else:
                    # Cancelar
                    self.ai_handler.pending_action = None
                    return "Acción cancelada."
            
            # Verificar si la acción requiere confirmación
            if self._requires_confirmation(intent, parameters):
                # Guardar acción pendiente
                self.ai_handler.pending_action = {
                    "intent": intent,
                    "parameters": parameters
                }
                print(f"⚠️ Acción pendiente de confirmación: {intent}")
                return ""  # El AI ya preguntó en su respuesta
            
            # Si hay una acción que ejecutar, cambiar a estado EXECUTING
            if intent != "chat":
                self.signals.state_changed.emit(AssistantState.EXECUTING)
            
            return self._execute_action(intent, parameters)
            
        except Exception as e:
            return f"Error procesando intent: {str(e)}"
            
    def _requires_confirmation(self, intent: str, parameters: dict) -> bool:
        """Verificar si una acción requiere confirmación del usuario"""
        if intent in self.DANGEROUS_ACTIONS:
            action = parameters.get("action", "")
            if action in self.DANGEROUS_ACTIONS[intent]:
                return True
        return False
    
    def _execute_action(self, intent: str, parameters: dict) -> str:
        """Ejecutar una acción"""
        try:
            if intent == "open_app":
                app_name = parameters.get("app_name", "")
                if app_name:
                    result = open_app(app_name)
                    return result.get("message", "")
                    
            elif intent == "weather_report":
                city = parameters.get("city", "")
                time_param = parameters.get("time")
                if city:
                    result = get_weather(city, time_param)
                    return result.get("message", "")
                    
            elif intent == "search":
                query = parameters.get("query", "")
                if query:
                    result = web_search(query)
                    return result.get("message", "")
            
            elif intent == "open_site":
                site = parameters.get("site", "")
                query = parameters.get("query")
                if site:
                    result = open_url(site, query)
                    return result.get("message", "")
                    
            elif intent == "play_music":
                song_query = parameters.get("song_query", "")
                action = parameters.get("action", "play")
                if song_query:
                    result = spotify_control(action, song_query)
                    return result.get("message", "")
                else:
                    # No song specified, just play/pause current
                    result = volume_control("pause")
                    return result.get("message", "")
            
            elif intent == "wolfram":
                query = parameters.get("query", "")
                if query:
                    result = query_wolfram(query)
                    return f"WolframAlpha: {result}"
            
            elif intent == "system_info":
                info_type = parameters.get("info_type", "full")
                if info_type == "ip":
                    pub_ip = get_public_ip()
                    priv_ip = get_private_ip()
                    return f"IP Pública: {pub_ip}\nIP Privada: {priv_ip}"
                elif info_type == "ram":
                    ram = get_ram_info()
                    if 'error' not in ram:
                        return f"Memoria RAM: {ram['total']} en total, {ram['disponible']} disponibles, uso actual {ram['porcentaje_uso']}."
                    return "No pude obtener la información de RAM."
                elif info_type == "cpu":
                    cpu = get_cpu_info()
                    if 'error' not in cpu:
                        return f"Procesador: uso actual {cpu['uso']}, {cpu['nucleos_fisicos']} núcleos físicos, {cpu['nucleos_logicos']} lógicos, frecuencia {cpu['frecuencia_actual']}."
                    return "No pude obtener la información del CPU."
                elif info_type == "disk":
                    disk = get_disk_info()
                    if 'error' not in disk:
                        return f"Almacenamiento: {disk['total']} en total, {disk['libre']} libres, uso {disk['porcentaje_uso']}."
                    return "No pude obtener la información del disco."
                else:
                    return get_system_status_text()
            
            elif intent == "flight_radar":
                result = open_flight_radar()
                return result.get("message", "")
            
            elif intent == "volume_control":
                action = parameters.get("action", "up")
                amount = parameters.get("amount", 2)
                result = volume_control(action, amount)
                return result.get("message", "")
            
            elif intent == "run_command":
                command = parameters.get("command", "")
                shell = parameters.get("shell", "cmd")
                if command:
                    result = run_command(command, shell)
                    return result.get("message", "")
                # If no command, the AI will ask (needs_clarification=true)
                return ""
            
            elif intent == "pc_control":
                action = parameters.get("action", "")
                if action:
                    # Pasar parámetros adicionales si existen
                    extra_params = {k: v for k, v in parameters.items() if k != "action"}
                    result = system_control(action, **extra_params)
                    return result.get("message", "")
                return ""
            
            elif intent == "organize_files":
                action = parameters.get("action", "by_type")
                folder_path = parameters.get("folder_path")  # None = detectar automáticamente
                
                # Si es "detect", mostrar la carpeta y guardar acción pendiente
                if action == "detect":
                    result = organize_files("detect", folder_path)
                    if result.get("success") and result.get("path"):
                        detected_path = result.get("path")
                        # Guardar para organizar después de confirmar
                        self.ai_handler.pending_action = {
                            "intent": "organize_files",
                            "parameters": {"action": "by_type", "folder_path": detected_path}
                        }
                        return f"Carpeta detectada: {detected_path}\n¿Quiere que la organice por tipo? Diga 'acepto' o 'cancelo'."
                    else:
                        return result.get("message", "No se pudo detectar la carpeta.")
                
                extra_params = {k: v for k, v in parameters.items() if k not in ["action", "folder_path"]}
                result = organize_files(action, folder_path, **extra_params)
                return result.get("message", "")
                    
            return ""  # No action needed for chat intent
            
        except Exception as e:
            return f"Error ejecutando acción: {str(e)}"


class VoiceWorkerThread(QThread):
    """Worker thread for voice input"""
    def __init__(self, speech_handler, continuous=False):
        super().__init__()
        self.speech_handler = speech_handler
        self.signals = WorkerSignals()
        self.is_listening = True
        self.continuous = continuous  # Modo continuo (activado por wake word)
        
    def run(self):
        try:
            # 👂 Estado: ESCUCHANDO
            self.signals.state_changed.emit(AssistantState.LISTENING)
            
            # Si es modo continuo, escucha sin timeout hasta detectar voz
            if self.continuous:
                text = self.speech_handler.listen(timeout=60, phrase_time_limit=60, continuous=True)
            else:
                text = self.speech_handler.listen()
                
            if text and self.is_listening:
                self.signals.voice_input_ready.emit(text)
            
            # Volver a IDLE si no se detectó nada
            if not text:
                self.signals.state_changed.emit(AssistantState.IDLE)
        except Exception as e:
            self.signals.state_changed.emit(AssistantState.IDLE)
            self.signals.error.emit(f"Voice error: {str(e)}")
    
    def stop_listening(self):
        self.is_listening = False
        self.signals.state_changed.emit(AssistantState.IDLE)


class AssistantState:
    """Estados explícitos del asistente"""
    IDLE = "idle"              # 💤 Esperando
    LISTENING = "listening"    # 👂 Escuchando
    THINKING = "thinking"      # 🧠 Pensando/Procesando
    EXECUTING = "executing"    # ⚙️ Ejecutando acción
    RESPONDING = "responding"  # 💬 Respondiendo (hablando)


class JarvisFaceWidget(QLabel):
    """Custom widget for JARVIS animated face with state-based animations"""
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(700, 700)
        self.setStyleSheet("background-color: #000000;")
        
        # JARVIS face settings
        self.face_size = (250, 250)
        self.canvas_size = (700, 700)
        
        # Load face image
        face_path = "assets/jarvis_face.png"
        if not os.path.exists(face_path):
            face_path = "assets/face.png"
        
        try:
            self.face_base = (
                Image.open(face_path)
                .convert("RGBA")
                .resize(self.face_size, Image.LANCZOS)
            )
        except:
            # Create a default face if image not found
            self.face_base = self._create_default_face()
        
        self.halo_base = self._create_halo(self.canvas_size, radius=300, y_offset=0)
        
        # Estado actual del asistente
        self.state = AssistantState.IDLE
        
        # Animation state
        self.scale = 1.0
        self.target_scale = 1.0
        self.halo_alpha = 70
        self.target_halo_alpha = 70
        self.halo_color = (0, 150, 180)  # Color base cyan
        self.target_halo_color = (0, 150, 180)
        self.pulse_phase = 0  # Para animaciones cíclicas
        self.last_target_time = time.time()
        
        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)  # ~60 FPS
        
    def _create_default_face(self):
        """Create a default JARVIS face if image is not found"""
        img = Image.new("RGBA", self.face_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple circular face
        center = (self.face_size[0] // 2, self.face_size[1] // 2)
        radius = min(self.face_size) // 3
        
        draw.ellipse(
            (center[0] - radius, center[1] - radius, 
             center[0] + radius, center[1] + radius),
            fill=(0, 150, 180, 100)
        )
        
        return img
        
    def _create_halo(self, size, radius, y_offset, color=(0, 150, 180)):
        """Create halo effect for JARVIS face with custom color"""
        w, h = size
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        cx = w // 2
        cy = h // 2 + y_offset
        
        for r in range(radius, 0, -8):
            alpha = int(40 * (1 - r / radius) ** 1.5)
            draw.ellipse(
                (cx - r, cy - r, cx + r, cy + r),
                fill=(*color, alpha)
            )
        
        return img.filter(ImageFilter.GaussianBlur(40))
    
    def set_state(self, state: str):
        """Cambiar estado del asistente con animación correspondiente"""
        self.state = state
        self._update_animation_params()
    
    def _update_animation_params(self):
        """Actualizar parámetros de animación según el estado"""
        if self.state == AssistantState.IDLE:
            # 💤 IDLE: Respiración suave, cyan tenue
            self.target_halo_color = (0, 150, 180)  # Cyan suave
            
        elif self.state == AssistantState.LISTENING:
            # 👂 LISTENING: Pulso lento, azul medio
            self.target_halo_color = (0, 120, 200)  # Azul medio
            
        elif self.state == AssistantState.THINKING:
            # 🧠 THINKING: Pulso rápido, azul más intenso
            self.target_halo_color = (0, 100, 255)  # Azul brillante
            
        elif self.state == AssistantState.EXECUTING:
            # ⚙️ EXECUTING: Rotación visual, azul-cyan brillante
            self.target_halo_color = (0, 180, 255)  # Cyan brillante
            
        elif self.state == AssistantState.RESPONDING:
            # 💬 RESPONDING: Animación intensa, azul eléctrico
            self.target_halo_color = (50, 150, 255)  # Azul eléctrico
    
    def set_speaking(self, speaking):
        """Legacy method - redirects to set_state"""
        if speaking:
            self.set_state(AssistantState.RESPONDING)
        else:
            self.set_state(AssistantState.IDLE)
        
    def _animate(self):
        """Animate JARVIS face based on state"""
        now = time.time()
        self.pulse_phase += 0.05
        
        # Definir parámetros de animación según el estado
        if self.state == AssistantState.IDLE:
            # 💤 Respiración suave y lenta
            update_interval = 0.7
            if now - self.last_target_time > update_interval:
                self.target_scale = random.uniform(1.004, 1.012)
                self.target_halo_alpha = random.randint(60, 80)
                self.last_target_time = now
            scale_speed = 0.25
            halo_speed = 0.25
            
        elif self.state == AssistantState.LISTENING:
            # 👂 Pulso medio, atento
            update_interval = 0.4
            if now - self.last_target_time > update_interval:
                self.target_scale = random.uniform(1.01, 1.04)
                self.target_halo_alpha = random.randint(90, 120)
                self.last_target_time = now
            scale_speed = 0.35
            halo_speed = 0.35
            
        elif self.state == AssistantState.THINKING:
            # 🧠 Pulso rápido y visible
            self.target_scale = 1.02 + 0.03 * abs(math.sin(self.pulse_phase * 2))
            self.target_halo_alpha = 100 + 40 * abs(math.sin(self.pulse_phase * 2))
            scale_speed = 0.5
            halo_speed = 0.5
            
        elif self.state == AssistantState.EXECUTING:
            # ⚙️ Rotación/pulsación intensa
            self.target_scale = 1.03 + 0.05 * abs(math.sin(self.pulse_phase * 3))
            self.target_halo_alpha = 110 + 50 * abs(math.sin(self.pulse_phase * 3))
            scale_speed = 0.6
            halo_speed = 0.6
            
        elif self.state == AssistantState.RESPONDING:
            # 💬 Animación muy intensa (hablando)
            update_interval = 0.25
            if now - self.last_target_time > update_interval:
                self.target_scale = random.uniform(1.02, 1.1)
                self.target_halo_alpha = random.randint(120, 160)
                self.last_target_time = now
            scale_speed = 0.45
            halo_speed = 0.45
        else:
            # Fallback a IDLE
            update_interval = 0.7
            if now - self.last_target_time > update_interval:
                self.target_scale = random.uniform(1.004, 1.012)
                self.target_halo_alpha = random.randint(60, 80)
                self.last_target_time = now
            scale_speed = 0.25
            halo_speed = 0.25
        
        # Interpolar escala y alpha
        self.scale += (self.target_scale - self.scale) * scale_speed
        self.halo_alpha += (self.target_halo_alpha - self.halo_alpha) * halo_speed
        
        # Interpolar color del halo suavemente
        color_speed = 0.1
        self.halo_color = tuple(
            int(self.halo_color[i] + (self.target_halo_color[i] - self.halo_color[i]) * color_speed)
            for i in range(3)
        )
        
        # Create frame
        frame = Image.new("RGBA", self.canvas_size, (0, 0, 0, 255))
        
        # Recrear halo con color actual
        halo = self._create_halo(self.canvas_size, radius=300, y_offset=0, color=self.halo_color)
        halo.putalpha(int(self.halo_alpha))
        frame.alpha_composite(halo)
        
        # Add face
        w, h = self.face_size
        face = self.face_base.resize(
            (int(w * self.scale), int(h * self.scale)),
            Image.LANCZOS
        )
        
        # Center face in the canvas
        cw, ch = self.canvas_size
        fx = (cw - face.size[0]) // 2
        fy = (ch - face.size[1]) // 2
        frame.alpha_composite(face, (fx, fy))
        
        # Convert to QPixmap
        frame_rgb = frame.convert('RGB')
        qimg = QImage(frame_rgb.tobytes(), frame_rgb.size[0], frame_rgb.size[1], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        
        self.setPixmap(pixmap)


class AIAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S - Almudena Bedoya")
        self.setGeometry(100, 100, 800, 950)
        self.setStyleSheet("background-color: #000000;")
        
        # Set custom icon if available
        icon_path = "assets/jarvis_icon.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        elif os.path.exists("assets/jarvis_face.png"):
            self.setWindowIcon(QIcon("assets/jarvis_face.png"))
        
        # Initialize handlers
        self.ai_handler = AIHandler()
        self.speech_handler = SpeechHandler()
        
        self.is_listening = False
        self.voice_thread = None
        self.attached_files = []  # Lista de archivos adjuntos
        self.show_rag_sources = False  # Toggle para mostrar fuentes RAG
        self.current_rag_sources = []  # Últimas fuentes RAG
        
        # Wake word detection
        self.wake_word_active = True
        self.wake_word_thread = None
        self.wake_word_stop_event = None
        
        # Conversation mode - 4 minutes of continuous listening
        self.conversation_mode = False
        self.conversation_end_time = 0
        self.CONVERSATION_TIMEOUT = 240  # 4 minutes in seconds
        
        self.setup_ui()
        
        # Start wake word listener after UI is ready
        self.start_wake_word_listener()
        
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # JARVIS face
        self.jarvis_face = JarvisFaceWidget()
        main_layout.addWidget(self.jarvis_face, alignment=Qt.AlignCenter)
        
        # Status label (muestra el estado actual)
        self.status_label = QLabel("💤 Esperando...")
        self.status_label.setFont(QFont("Consolas", 11, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ccff;
                padding: 8px;
                background-color: rgba(0, 51, 102, 120);
                border-radius: 8px;
                margin: 5px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 10))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 77);
                color: #8ffcff;
                border: 1px solid rgba(0, 150, 180, 80);
                border-radius: 8px;
                padding: 15px;
            }
        """)
        self.chat_display.setMaximumHeight(480)
        main_layout.addWidget(self.chat_display)
        
        # Attached files display
        self.files_display = QLabel()
        self.files_display.setFont(QFont("Consolas", 10))
        self.files_display.setStyleSheet("""
            QLabel {
                color: #00ccff;
                padding: 5px;
                background-color: rgba(0, 51, 102, 100);
                border-radius: 5px;
            }
        """)
        self.files_display.setVisible(False)
        main_layout.addWidget(self.files_display)
        
        # RAG Sources display
        self.rag_sources_display = QTextEdit()
        self.rag_sources_display.setReadOnly(True)
        self.rag_sources_display.setFont(QFont("Consolas", 9))
        self.rag_sources_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 51, 102, 100);
                color: #66d9ff;
                border: 1px solid rgba(0, 150, 180, 80);
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.rag_sources_display.setMaximumHeight(150)
        self.rag_sources_display.setVisible(False)
        main_layout.addWidget(self.rag_sources_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_entry = QLineEdit()
        self.input_entry.setFont(QFont("Consolas", 10))
        self.input_entry.setStyleSheet("""
            QLineEdit {
                background-color: #000000;
                color: #8ffcff;
                border: 1px solid #003366;
                padding: 8px;
            }
        """)
        self.input_entry.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_entry)
        
        # Buttons
        self.attach_button = QPushButton("📎")
        self.attach_button.setFont(QFont("Consolas", 10))
        self.attach_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: #8ffcff;
                border: none;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #004080;
            }
        """)
        self.attach_button.clicked.connect(self.attach_files)
        input_layout.addWidget(self.attach_button)
        
        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont("Consolas", 10))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: #8ffcff;
                border: none;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #004080;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        self.voice_button = QPushButton("Voz")
        self.voice_button.setFont(QFont("Consolas", 10))
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: #8ffcff;
                border: none;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #004080;
            }
        """)
        self.voice_button.clicked.connect(self.toggle_voice)
        input_layout.addWidget(self.voice_button)
        
        # Toggle RAG sources button
        self.sources_button = QPushButton("📚")
        self.sources_button.setFont(QFont("Consolas", 10))
        self.sources_button.setToolTip("Mostrar/Ocultar fuentes RAG")
        self.sources_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: #8ffcff;
                border: none;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #004080;
            }
        """)
        self.sources_button.clicked.connect(self.toggle_rag_sources)
        input_layout.addWidget(self.sources_button)
        
        main_layout.addLayout(input_layout)
        
    def update_status_label(self, state: str):
        """Actualiza el label de estado con emoji y texto"""
        state_info = {
            AssistantState.IDLE: ("💤 Esperando...", "#0096b4"),
            AssistantState.LISTENING: ("👂 Escuchando...", "#0078c8"),
            AssistantState.THINKING: ("🧠 Pensando...", "#0064ff"),
            AssistantState.EXECUTING: ("⚙️ Ejecutando...", "#00b4ff"),
            AssistantState.RESPONDING: ("💬 Respondiendo...", "#3296ff")
        }
        
        text, color = state_info.get(state, ("❓ Desconocido", "#00ccff"))
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                padding: 8px;
                background-color: rgba(0, 51, 102, 120);
                border-radius: 8px;
                margin: 5px;
            }}
        """)
    
    def toggle_rag_sources(self):
        """Toggle RAG sources visibility"""
        self.show_rag_sources = not self.show_rag_sources
        
        if self.show_rag_sources and self.current_rag_sources:
            self.display_rag_sources(self.current_rag_sources)
            self.rag_sources_display.setVisible(True)
        else:
            self.rag_sources_display.setVisible(False)
    
    def display_rag_sources(self, sources: list):
        """Display RAG sources in the UI"""
        self.current_rag_sources = sources
        
        if not sources:
            return
        
        # Build formatted text
        source_text = "📚 <b>Fuentes consultadas:</b><br><br>"
        
        for source in sources:
            source_id = source.get('source_id', '?')
            file_name = source.get('file', 'Desconocido')
            section = source.get('section', '')
            similarity = source.get('similarity', 0.0)
            indexed_at = source.get('indexed_at', 'Desconocido')
            
            # Parse and format date
            try:
                from datetime import datetime
                date_obj = datetime.fromisoformat(indexed_at)
                date_str = date_obj.strftime('%d/%m/%Y %H:%M')
            except:
                date_str = indexed_at
            
            similarity_percent = int(similarity * 100)
            
            source_text += f"<b>[{source_id}]</b> <span style='color: #00ccff;'>{file_name}</span><br>"
            source_text += f"   ├─ Sección: {section}<br>"
            source_text += f"   ├─ Relevancia: {similarity_percent}%<br>"
            source_text += f"   └─ Indexado: {date_str}<br><br>"
        
        self.rag_sources_display.setHtml(source_text)
        
        # Show automatically if toggle is on
        if self.show_rag_sources:
            self.rag_sources_display.setVisible(True)
    
    def attach_files(self):
        """Open file dialog to attach files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar archivos",
            "",
            "Todos los archivos (*.*);;Archivos de texto (*.txt);;Código Python (*.py);;Documentos (*.pdf *.docx *.doc)"
        )
        
        if files:
            self.attached_files.extend(files)
            self.update_files_display()
    
    def update_files_display(self):
        """Update the attached files display"""
        if self.attached_files:
            file_names = [os.path.basename(f) for f in self.attached_files]
            display_text = "📎 Adjuntos: " + ", ".join(file_names)
            if len(display_text) > 80:
                display_text = display_text[:77] + "..."
            self.files_display.setText(display_text)
            self.files_display.setVisible(True)
        else:
            self.files_display.setVisible(False)
    
    def clear_attached_files(self):
        """Clear all attached files"""
        self.attached_files = []
        self.update_files_display()
    
    def read_file_content(self, file_path):
        """Read content from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"[Error leyendo archivo: {str(e)}]"
        except Exception as e:
            return f"[Error leyendo archivo: {str(e)}]"
    
    def add_message(self, sender, message):
        """Add a message to the chat display"""
        if sender == "Almu":
            color = "#00ccff"
        elif sender == "JARVIS":
            color = "#00ff88"
        else:
            color = "#ff6666"
        
        # Format message with proper line breaks
        # Replace numbered lists and periods with line breaks
        formatted_text = message
        
        # Add line breaks after sentences (period + space + capital letter)
        import re
        formatted_text = re.sub(r'\. ([A-Z\u00C0-\u017F])', r'.\n\n\1', formatted_text)
        
        # Add line breaks after numbered items
        formatted_text = re.sub(r'(\d+\.\s)', r'\n\1', formatted_text)
        
        # Convert \n to <br> for HTML
        formatted_text = formatted_text.replace('\n', '<br>')
            
        formatted_message = f'<span style="color: {color};">[{sender}]</span> {formatted_text}<br>'
        self.chat_display.append(formatted_message)
        
    def send_message(self):
        """Send a text message"""
        message = self.input_entry.text().strip()
        if not message:
            return
            
        self.input_entry.clear()
        
        # Include attached files content if any
        full_message = message
        if self.attached_files:
            full_message += "\n\n--- Archivos adjuntos ---\n"
            for file_path in self.attached_files:
                file_name = os.path.basename(file_path)
                content = self.read_file_content(file_path)
                full_message += f"\n[{file_name}]\n{content}\n"
            
            # Show user message with file indicator
            self.add_message("Almu", f"{message} 📎 ({len(self.attached_files)} archivo(s))")
            self.clear_attached_files()
        else:
            self.add_message("Almu", message)
        
        # Process in background thread
        self.ai_thread = AIWorkerThread(self.ai_handler, full_message)
        self.ai_thread.signals.message_ready.connect(self.add_message)
        self.ai_thread.signals.error.connect(lambda msg: self.add_message("System", msg))
        self.ai_thread.signals.state_changed.connect(self.jarvis_face.set_state)
        self.ai_thread.signals.state_changed.connect(self.update_status_label)
        self.ai_thread.signals.rag_sources_ready.connect(self.display_rag_sources)
        self.ai_thread.start()
        
    def process_voice_message(self, message, use_voice_output=True):
        """Process voice message"""
        self.add_message("You", message)
            
        # Process in background thread
        self.ai_thread = AIWorkerThread(self.ai_handler, message, use_voice_output)
        self.ai_thread.signals.message_ready.connect(self.add_message)
        self.ai_thread.signals.error.connect(lambda msg: self.add_message("System", msg))
        self.ai_thread.signals.state_changed.connect(self.jarvis_face.set_state)
        self.ai_thread.signals.state_changed.connect(self.update_status_label)
        self.ai_thread.signals.rag_sources_ready.connect(self.display_rag_sources)
        # Restart wake word listener after processing completes
        self.ai_thread.signals.finished_processing.connect(self._restart_wake_word)
            
        self.ai_thread.start()
    
    @Slot()
    def _restart_wake_word(self):
        """Restart listening - conversation mode or wake word"""
        import time as t
        
        # Check if still in conversation mode
        if self.conversation_mode and t.time() < self.conversation_end_time:
            # Still in conversation mode - keep listening
            if not self.is_listening:
                self.start_listening(continuous=True)
        else:
            # Conversation ended - back to wake word mode
            if self.conversation_mode:
                self.conversation_mode = False
                self.add_message("System", "💤 Modo conversación terminado. Di 'Hola JARVIS' para continuar.")
            if self.wake_word_active and not self.is_listening:
                self.start_wake_word_listener()
        
    def toggle_voice(self):
        """Toggle voice input"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
            
    def start_listening(self, continuous=False):
        """Start listening for voice input
        
        Args:
            continuous: If True, keeps listening until speech detected (for wake word)
        """
        self.is_listening = True
        self.voice_button.setText("⏹")
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #cc0000;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
            }
        """)
        
        self.voice_thread = VoiceWorkerThread(self.speech_handler, continuous=continuous)
        self.voice_thread.signals.voice_input_ready.connect(self.on_voice_input)
        self.voice_thread.signals.error.connect(lambda msg: self.add_message("System", msg))
        self.voice_thread.signals.state_changed.connect(self.jarvis_face.set_state)
        self.voice_thread.signals.state_changed.connect(self.update_status_label)
        self.voice_thread.finished.connect(self.stop_listening)
        self.voice_thread.start()
        
    def stop_listening(self):
        """Stop listening for voice input"""
        self.is_listening = False
        self.voice_button.setText("🎤")
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: #8ffcff;
                border: none;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #004080;
            }
        """)
        
        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.stop_listening()
            
    @Slot(str)
    def on_voice_input(self, text):
        """Handle voice input"""
        self.stop_listening()
        
        # Reset conversation timeout - another 4 minutes from now
        if self.conversation_mode:
            import time as t
            self.conversation_end_time = t.time() + self.CONVERSATION_TIMEOUT
        
        self.process_voice_message(text, True)
    
    def start_wake_word_listener(self):
        """Start listening for wake word in background"""
        if self.wake_word_thread and self.wake_word_thread.is_alive():
            return  # Already running
        
        self.wake_word_stop_event = threading.Event()
        self.wake_word_thread = threading.Thread(
            target=self.speech_handler.listen_for_wake_word,
            args=(self.on_wake_word_detected, self.wake_word_stop_event),
            daemon=True
        )
        self.wake_word_thread.start()
        self.add_message("System", "🎙️ Escuchando 'Hola JARVIS'...")
    
    def stop_wake_word_listener(self):
        """Stop the wake word listener"""
        if self.wake_word_stop_event:
            self.wake_word_stop_event.set()
        # Don't join from the same thread - just mark it for cleanup
        self.wake_word_thread = None
    
    def on_wake_word_detected(self, detected_text=""):
        """Called when wake word is detected - starts voice input"""
        # Stop wake word listener temporarily
        self.stop_wake_word_listener()
        
        # Store detected text for special responses
        self._last_wake_text = detected_text
        
        # Use Qt signal to safely call from thread
        from PySide6.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(self, "_trigger_wake_response", Qt.QueuedConnection)
    
    @Slot()
    def _trigger_wake_response(self):
        """Respond to wake word and start conversation mode"""
        import time as t
        
        # Start conversation mode - 4 minutes
        self.conversation_mode = True
        self.conversation_end_time = t.time() + self.CONVERSATION_TIMEOUT
        
        # Check for special phrases
        wake_text = getattr(self, '_last_wake_text', '').lower()
        
        if 'listo' in wake_text or 'preparado' in wake_text:
            # Special response for "estás listo"
            response_text = "Para usted siempre, señora. Dime, ¿qué deseas?"
            response_voice = "Para usted siempre, señora. Dime, qué deseas?"
        else:
            # Normal response
            response_text = "¿En qué puedo ayudarla, señora?"
            response_voice = "¿En qué puedo ayudarla, señora?"
        
        # Respond with voice
        self.add_message("JARVIS", response_text)
        voice_player = VoicePlayer()
        voice_player.speak(response_voice)
        
        # Start listening for command
        if not self.is_listening:
            self.start_listening(continuous=True)
    
    def closeEvent(self, event):
        """Clean up when closing the window"""
        self.stop_wake_word_listener()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = AIAssistantGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()