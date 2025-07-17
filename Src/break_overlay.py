from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLayout
from PyQt6.QtCore import Qt, QUrl, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtMultimedia import QSoundEffect
from stylesheets import Styles  # Import the Styles class
import random
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class BreakOverlay(QWidget):
    snoozeRequested = pyqtSignal(int)  # Signal to request snooze with minutes
    
    def __init__(self, parent=None, soundtrack=None, snooze_settings=None):
        super().__init__(parent)
        
        # Initialize snooze settings and counter FIRST
        self.snooze_settings = snooze_settings or {
            'snooze_enabled': True,
            'snooze_time': 5,
            'max_snooze_count': 3,
            'current_snooze_count': 0
        }
        self.snooze_count = self.snooze_settings.get('current_snooze_count', 0)
        
        # Make sure we don't close the parent when this widget closes
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.showFullScreen()
        self.setWindowOpacity(0.0)  # start transparent for fade-in
        self.fade_duration = 500
        self.fade_in()
        
        # Initialize notification sound
        self.notification = QSoundEffect()
        self.notification.setSource(QUrl.fromLocalFile(resource_path(r"dist\\assets\\sounds\\notification_001.wav")))

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        # Create centered black rounded frame
        frame = QWidget()
        frame.setStyleSheet("background-color: #000000; border-radius: 20px;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(30)
        frame_layout.setContentsMargins(40, 40, 40, 40)
        frame_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        
        # List of motivational quotes
        self.motivational_quotes = [
            "Your brain recharges during breaks. Step away to stay sharp. 🧠 Boosts mental clarity",
            "Even 1 minute of rest improves your focus and reduces stress. 🌿 Micro-break magic",
            "Breaks help your brain organize and retain what you just learned. 📚 Supports memory",
            "Move a little. Stretch. It increases blood flow and boosts creativity. 🏃 Better blood, better ideas",
            "Short breaks = more productive work sessions. Science says so! 📈 Pomodoro power",
            "Blink. Breathe. Look away. Your eyes need this moment too. 👀 Eye strain relief",
            "Stepping away now means coming back stronger. 💪 Resilience booster",
            "Your best ideas come when you're not forcing them. Relax. 🧘‍♂️ Creativity flows in calm",
            "Breaks are not a waste of time. They're an investment in your productivity. ⏳ Time well spent",
            "The most focused minds take the most frequent breaks. 🧘‍♀️ Focused and refreshed",
            "You're not wasting time. You're investing in your energy. 🔋 Recharge mindset",
        ]
        
        # Motivational text with random quote
        random_quote = random.choice(self.motivational_quotes)
        self.motivation_label = QLabel(random_quote)
        self.motivation_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                padding: 10px;
            }
        """)
        self.motivation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.motivation_label)
        
        # Timer display
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet(Styles.BREAK_OVERLAY_TIMER)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.timer_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Snooze button (only show if snooze is enabled and count hasn't exceeded limit)
        if (self.snooze_settings['snooze_enabled'] and 
            self.snooze_count < self.snooze_settings['max_snooze_count']):
            self.snooze_button = QPushButton(f"Snooze for {self.snooze_settings['snooze_time']} min")
            self.snooze_button.setFixedSize(200, 60)
            self.snooze_button.setStyleSheet(Styles.SNOOZE_OVERLAY_BUTTON)
            self.snooze_button.clicked.connect(self.handle_snooze)
            button_layout.addWidget(self.snooze_button)
        
        # End button
        self.end_button = QPushButton("End Break")
        self.end_button.setFixedSize(200, 60)
        self.end_button.setStyleSheet(Styles.BREAK_OVERLAY_BUTTON)
        button_layout.addWidget(self.end_button)
        
        frame_layout.addLayout(button_layout)
        layout.addWidget(frame)
        self.setLayout(layout)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(255, 255, 255, 200))  # Semi-transparent white
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        
    def updateTimer(self, time_text):
        self.timer_label.setText(time_text)
    
    def fade_in(self):
        anim = QPropertyAnimation(self, b'windowOpacity')
        anim.setDuration(self.fade_duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()
        self.fade_in_animation = anim

    def fade_out(self):
        anim = QPropertyAnimation(self, b'windowOpacity')
        anim.setDuration(self.fade_duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.finished.connect(self.close)
        anim.start()
        self.fade_out_animation = anim

    def handle_snooze(self):
        """Handle snooze button click"""
        snooze_minutes = self.snooze_settings['snooze_time']
        self.snoozeRequested.emit(snooze_minutes)
        self.fade_out()
    
    # Modified method to safely close without affecting parent
    def closeEvent(self, event):
        """Clean up resources when window is closed"""
        # Ensure the event doesn't propagate beyond this widget
        event.accept()
