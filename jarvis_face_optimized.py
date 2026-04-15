"""
Versión optimizada del widget JARVIS Face
Reduce significativamente el consumo de CPU/RAM
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap, QImage, QPainter, QRadialGradient, QColor, QPen
from PIL import Image
import os
import time
import random


class JarvisFaceOptimized(QLabel):
    """Widget optimizado de la cara de JARVIS - Consume menos recursos"""
    
    def __init__(self, performance_mode="balanced"):
        """
        Args:
            performance_mode: "low" (máximo ahorro), "balanced" (balanceado), "high" (máxima calidad)
        """
        super().__init__()
        
        # Configuración de rendimiento
        self.performance_mode = performance_mode
        self._setup_performance_settings()
        
        # Tamaño más pequeño = menos procesamiento
        self.setFixedSize(self.widget_size, self.widget_size)
        self.setStyleSheet("background-color: #000000;")
        
        # Cargar imagen base una sola vez
        self._load_face_image()
        
        # Estado de animación
        self.speaking = False
        self.pulse_phase = 0
        
        # Pre-renderizar frames de animación (cache)
        self._prerender_frames()
        
        # Setup animation timer con FPS configurables
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        self.timer.start(self.frame_interval)
        
    def _setup_performance_settings(self):
        """Configura los ajustes según el modo de rendimiento"""
        if self.performance_mode == "low":
            # Modo bajo consumo
            self.widget_size = 400
            self.face_size = 150
            self.fps = 15  # 15 FPS
            self.enable_blur = False
            self.animation_steps = 8
            
        elif self.performance_mode == "balanced":
            # Modo balanceado (RECOMENDADO)
            self.widget_size = 500
            self.face_size = 180
            self.fps = 24  # 24 FPS
            self.enable_blur = True
            self.animation_steps = 12
            
        else:  # high
            # Modo alta calidad
            self.widget_size = 700
            self.face_size = 250
            self.fps = 30  # 30 FPS
            self.enable_blur = True
            self.animation_steps = 16
        
        self.frame_interval = int(1000 / self.fps)  # ms entre frames
        
    def _load_face_image(self):
        """Carga la imagen de la cara una sola vez"""
        face_path = "assets/jarvis_face.png"
        if not os.path.exists(face_path):
            face_path = "assets/face.png"
        
        try:
            # Cargar y redimensionar una sola vez
            img = Image.open(face_path).convert("RGBA")
            img = img.resize((self.face_size, self.face_size), Image.LANCZOS)
            
            # Convertir a QPixmap (más eficiente para Qt)
            img_rgb = img.convert('RGB')
            qimg = QImage(img_rgb.tobytes(), img_rgb.size[0], img_rgb.size[1], QImage.Format_RGB888)
            self.face_pixmap = QPixmap.fromImage(qimg)
            
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            # Crear cara por defecto usando Qt (más eficiente que PIL)
            self.face_pixmap = self._create_default_face_qt()
    
    def _create_default_face_qt(self):
        """Crea una cara por defecto usando Qt directamente (más eficiente)"""
        pixmap = QPixmap(self.face_size, self.face_size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Gradiente radial para el círculo
        gradient = QRadialGradient(self.face_size/2, self.face_size/2, self.face_size/3)
        gradient.setColorAt(0, QColor(0, 180, 220, 150))
        gradient.setColorAt(1, QColor(0, 150, 180, 50))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            int(self.face_size * 0.15), 
            int(self.face_size * 0.15),
            int(self.face_size * 0.7), 
            int(self.face_size * 0.7)
        )
        
        painter.end()
        return pixmap
    
    def _prerender_frames(self):
        """Pre-renderiza frames de animación para evitar procesamiento en tiempo real"""
        self.idle_frames = []
        self.speaking_frames = []
        
        # Generar frames para modo idle
        for i in range(self.animation_steps):
            intensity = 0.3 + 0.2 * (i / self.animation_steps)
            frame = self._create_frame(intensity, glow_size=1.0)
            self.idle_frames.append(frame)
        
        # Generar frames para modo hablando
        for i in range(self.animation_steps):
            intensity = 0.6 + 0.4 * (i / self.animation_steps)
            glow_size = 1.0 + 0.15 * (i / self.animation_steps)
            frame = self._create_frame(intensity, glow_size)
            self.speaking_frames.append(frame)
        
        self.current_frame = 0
    
    def _create_frame(self, intensity, glow_size=1.0):
        """Crea un frame de animación"""
        pixmap = QPixmap(self.widget_size, self.widget_size)
        pixmap.fill(QColor(0, 0, 0))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Centro del widget
        cx = self.widget_size / 2
        cy = self.widget_size / 2
        
        # Dibujar halo con gradiente
        if self.enable_blur:
            glow_radius = 180 * glow_size
            gradient = QRadialGradient(cx, cy, glow_radius)
            
            # Colores del halo basados en intensidad
            alpha = int(80 * intensity)
            gradient.setColorAt(0, QColor(0, 180, 220, alpha))
            gradient.setColorAt(0.5, QColor(0, 150, 180, alpha // 2))
            gradient.setColorAt(1, QColor(0, 100, 120, 0))
            
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(cx - glow_radius), int(cy - glow_radius), 
                              int(glow_radius * 2), int(glow_radius * 2))
        
        # Dibujar la cara en el centro
        face_x = int((self.widget_size - self.face_size) / 2)
        face_y = int((self.widget_size - self.face_size) / 2)
        
        # Aplicar escala suave
        scaled_size = int(self.face_size * (0.95 + 0.05 * intensity))
        offset = (self.face_size - scaled_size) // 2
        
        painter.drawPixmap(
            face_x + offset, 
            face_y + offset,
            scaled_size,
            scaled_size,
            self.face_pixmap
        )
        
        painter.end()
        return pixmap
    
    def _animate(self):
        """Animación optimizada - usa frames pre-renderizados"""
        # Seleccionar el conjunto de frames correcto
        frames = self.speaking_frames if self.speaking else self.idle_frames
        
        # Avanzar al siguiente frame
        self.current_frame = (self.current_frame + 1) % len(frames)
        
        # Mostrar frame
        self.setPixmap(frames[self.current_frame])
    
    def set_speaking(self, speaking):
        """Cambia el estado de habla"""
        if self.speaking != speaking:
            self.speaking = speaking
            self.current_frame = 0  # Reiniciar animación
    
    def set_performance_mode(self, mode):
        """Cambia el modo de rendimiento dinámicamente"""
        if mode != self.performance_mode:
            self.performance_mode = mode
            self.timer.stop()
            self._setup_performance_settings()
            self._load_face_image()
            self._prerender_frames()
            self.setFixedSize(self.widget_size, self.widget_size)
            self.timer.start(self.frame_interval)


class JarvisFaceMinimal(QLabel):
    """Versión ultra-minimalista - Para ordenadores muy lentos"""
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)
        self.setStyleSheet("background-color: #000000;")
        
        self.speaking = False
        self.pulse_intensity = 0.3
        
        # Renderizar solo cuando cambia el estado (no animación continua)
        self._render()
    
    def _render(self):
        """Renderiza un frame estático"""
        pixmap = QPixmap(300, 300)
        pixmap.fill(QColor(0, 0, 0))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Centro
        cx, cy = 150, 150
        
        # Halo simple
        intensity = 0.8 if self.speaking else 0.3
        gradient = QRadialGradient(cx, cy, 100)
        gradient.setColorAt(0, QColor(0, 180, 220, int(100 * intensity)))
        gradient.setColorAt(1, QColor(0, 150, 180, 0))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(50, 50, 200, 200)
        
        # Círculo central
        painter.setBrush(QColor(0, 180, 220, int(150 * intensity)))
        painter.drawEllipse(100, 100, 100, 100)
        
        painter.end()
        self.setPixmap(pixmap)
    
    def set_speaking(self, speaking):
        """Cambia el estado y re-renderiza"""
        if self.speaking != speaking:
            self.speaking = speaking
            self._render()


# Ejemplo de uso
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel
    import sys
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("JARVIS Face - Comparación de Rendimiento")
    window.setStyleSheet("background-color: #1a1a1a;")
    
    layout = QVBoxLayout()
    
    # Selector de modo
    label = QLabel("Selecciona el modo de rendimiento:")
    label.setStyleSheet("color: white; font-size: 14px; padding: 10px;")
    layout.addWidget(label)
    
    mode_selector = QComboBox()
    mode_selector.addItems(["Bajo (15 FPS)", "Balanceado (24 FPS)", "Alto (30 FPS)", "Mínimo (Estático)"])
    mode_selector.setStyleSheet("padding: 5px; font-size: 12px;")
    layout.addWidget(mode_selector)
    
    # Widget de cara inicial (balanceado)
    face = JarvisFaceOptimized("balanced")
    layout.addWidget(face, alignment=Qt.AlignCenter)
    
    def change_mode(index):
        """Cambia el modo de rendimiento"""
        modes = ["low", "balanced", "high"]
        if index < 3:
            new_face = JarvisFaceOptimized(modes[index])
        else:
            new_face = JarvisFaceMinimal()
        
        # Reemplazar widget
        layout.removeWidget(face)
        face.deleteLater()
        layout.addWidget(new_face, alignment=Qt.AlignCenter)
        globals()['face'] = new_face
    
    mode_selector.currentIndexChanged.connect(change_mode)
    
    window.setLayout(layout)
    window.resize(600, 700)
    window.show()
    
    sys.exit(app.exec())
