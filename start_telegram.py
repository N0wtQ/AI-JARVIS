"""
Start JARVIS Telegram Bot
Script para iniciar el bot de Telegram de JARVIS
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from channels.telegram_bot import start_telegram_bot


def main():
    print("""
    ╔═══════════════════════════════════════════╗
    ║     JARVIS - Telegram Bot                 ║
    ║     Multi-Channel Assistant               ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Verificar que el token existe
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("❌ Error: TELEGRAM_TOKEN no encontrado en .env")
        print("   Añade: TELEGRAM_TOKEN=tu_token_aquí")
        sys.exit(1)
    
    print(f"📱 Bot: @XarCrystal_Bot")
    print(f"🔑 Token: {token[:20]}...")
    print()
    
    try:
        start_telegram_bot()
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
