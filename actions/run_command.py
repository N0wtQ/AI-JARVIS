"""
Run Command Action
Executes commands in terminal/cmd
"""

import subprocess
import os


def run_command(command: str, shell: str = "cmd") -> dict:
    """
    Execute a command in terminal
    
    Args:
        command: The command to execute
        shell: "cmd" or "powershell"
        
    Returns:
        dict with result status and output
    """
    try:
        if not command:
            return {
                "success": False,
                "message": "No se especificó ningún comando."
            }
        
        # Security check - block dangerous commands
        dangerous_patterns = [
            "format ", "del /", "rd /s", "rmdir /s", 
            "rm -rf", ":(){", "fork bomb",
            "> /dev/sda", "mkfs.", "dd if="
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return {
                    "success": False,
                    "message": f"Comando bloqueado por seguridad: contiene '{pattern}'"
                }
        
        # Execute command
        if shell == "powershell":
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='cp850',
                errors='replace'
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='cp850',
                errors='replace'
            )
        
        output = result.stdout.strip() if result.stdout else ""
        error = result.stderr.strip() if result.stderr else ""
        
        if result.returncode == 0:
            response = f"Comando ejecutado correctamente."
            if output:
                # Limit output length
                if len(output) > 500:
                    output = output[:500] + "\n... (salida truncada)"
                response += f"\n\nResultado:\n{output}"
            return {
                "success": True,
                "message": response,
                "output": output
            }
        else:
            return {
                "success": False,
                "message": f"Error ejecutando comando: {error or 'Error desconocido'}",
                "output": error
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "El comando tardó demasiado (timeout de 30 segundos)."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def open_terminal(command: str = None) -> dict:
    """
    Open a new terminal window, optionally with a command
    
    Args:
        command: Optional command to run in the new terminal
        
    Returns:
        dict with result status
    """
    try:
        if command:
            # Open cmd with command and keep it open
            subprocess.Popen(
                f'start cmd /k "{command}"',
                shell=True
            )
            return {
                "success": True,
                "message": f"Terminal abierta ejecutando: {command}"
            }
        else:
            # Just open cmd
            subprocess.Popen('start cmd', shell=True)
            return {
                "success": True,
                "message": "Terminal abierta."
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error abriendo terminal: {str(e)}"
        }
