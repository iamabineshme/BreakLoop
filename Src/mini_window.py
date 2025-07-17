from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QFrame, QSystemTrayIcon
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont, QPainter, QColor, QPainterPath, QPen
import os
import sys

from numpy import pad

from stylesheets import Styles

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MiniWindow(QWidget):
    # Signals
    expandWindow = pyqtSignal()
    closeClicked = pyqtSignal()
    
    def __init__(self, default_time="00:00:00"):
        super().__init__()
        
        # Window configuration
        self.setWindowTitle("Timer Mini")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Black background will be applied in paintEvent

        # For window dragging
        self.dragging = False
        self.offset = QPoint()
        
        # Create layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Timer display
        self.timer_label = QLabel(default_time)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("padding: 20px;")  # Add horizontal padding

        # Use custom font if available, otherwise use system font
        font_id = QApplication.instance().property("Inter_28pt-Regular.ttf")
        if font_id and font_id != -1:
            font_family = QFont(QApplication.instance().property(resource_path(r"assets/fonts/Inter_28pt-Regular.ttf")), 20)
            font_family.setBold(True)
            self.timer_label.setFont(font_family)
        else:
            self.timer_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        self.timer_label.setStyleSheet("color: white;")
        
        # Divider line (vertical)
        self.divider_line = QFrame()
        self.divider_line.setFrameShape(QFrame.Shape.VLine)
        self.divider_line.setFrameShadow(QFrame.Shadow.Sunken)
        self.divider_line.setStyleSheet("color: #B2BEB5;")
        
        # Controls layout (horizontal for buttons)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Expand Button
        self.expand_button = QPushButton()
        self.expand_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\expand_24dp_white.svg")))
        self.expand_button.setFixedSize(30, 30)
        self.expand_button.setToolTip("Expand to full window")
        self.expand_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.expand_button.setStyleSheet(Styles.MINIMIZE_BUTTON)
        self.expand_button.clicked.connect(self.expandWindow.emit)
        
        # Close Button
        self.close_button = QPushButton()
        self.close_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\close_24dp_white.svg")))
        self.close_button.setFixedSize(30, 30)
        self.close_button.setToolTip("Close mini timer")
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet(Styles.MINIMIZE_BUTTON)
        self.close_button.clicked.connect(self.on_close_clicked)
        
        # Add buttons to controls
        controls_layout.addWidget(self.expand_button)
        controls_layout.addWidget(self.close_button)
        
        # Add widgets to main layout (horizontal)
        main_layout.addWidget(self.timer_label)
        main_layout.addWidget(self.divider_line)
        main_layout.addLayout(controls_layout)
        
        # Set size to hug content (adjust to minimum required size)
        self.setSizePolicy(QLabel().sizePolicy().horizontalPolicy(), QLabel().sizePolicy().verticalPolicy())
        self.adjustSize()
        
        
        # Position in bottom left corner
        desktop = QApplication.primaryScreen().availableGeometry()
        self.move(20,  # Left margin
                  desktop.height() - self.height() - 20)  # Bottom margin
                  
        # Initialize animation for smooth hover effect
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Default opacity
        self.opacity = 1.0

        # Initialize system tray icon for notifications
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\icon.png")))
        self.tray_icon.setToolTip("Timer Mini")
    
    def paintEvent(self, event):
        # Create a simple black window with rounded corners
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create the rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)

        # Draw plain black background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawPath(path)
    
    def update_timer(self, time_text):
        self.timer_label.setText(time_text)
        
    def on_close_clicked(self):
        """Hide window, transiently show tray icon for notification, then hide it."""
        self.hide()
        self.tray_icon.show()
        self.tray_icon.showMessage("Timer Mini", "Timer is still running, Press Quit on the app to quit timer", QSystemTrayIcon.MessageIcon.Information, 3000)
        self.tray_icon.hide()
    
    def enterEvent(self, event):
        # Increase opacity when mouse enters
        self.opacity = 1.0
        self.update()
        
    def leaveEvent(self, event):
        # Decrease opacity when mouse leaves
        self.opacity = 0.9
        self.update()
            
    # Event handling for window dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            
            # Store window position to settings
            # This could be implemented by connecting to main app