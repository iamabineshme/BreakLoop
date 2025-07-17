from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QLineEdit, QCheckBox, QSpinBox, QGroupBox, QFormLayout, QMessageBox, QStackedLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from stylesheets import Styles
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

class SettingsWindow(QWidget):
    # Define signals for communicating with main app
    settingsSaved = pyqtSignal(dict)
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.settings = current_settings or {}
        
        # Main layout
        settings_layout = QHBoxLayout(self)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== LEFT PANEL: NAVIGATION =====
        left_panel = QWidget()
        left_panel.setFixedWidth(200)
        left_panel.setStyleSheet("background-color: #272727")
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 10, 0, 0)
        left_panel_layout.setSpacing(1)

        # Settings title
        settings_title = QLabel("Settings")
        settings_title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px 15px; color: #FFFFFF;")
        settings_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_panel_layout.addWidget(settings_title)
        left_panel_layout.addSpacing(10)

        # Navigation buttons
        self.general_button = QPushButton("General")
        self.general_button.setStyleSheet(Styles.SETTINGS_ACTIVE_NAV_BUTTON)
        self.general_button.setCheckable(True)
        self.general_button.setChecked(True)
        left_panel_layout.addWidget(self.general_button)

        self.notification_button = QPushButton("Notifications")
        self.notification_button.setStyleSheet(Styles.SETTINGS_NAV_BUTTON)
        self.notification_button.setCheckable(True)
        left_panel_layout.addWidget(self.notification_button)

        self.snooze_button = QPushButton("Snooze")
        self.snooze_button.setStyleSheet(Styles.SETTINGS_NAV_BUTTON)
        self.snooze_button.setCheckable(True)
        left_panel_layout.addWidget(self.snooze_button)

        self.system_button = QPushButton("System")
        self.system_button.setStyleSheet(Styles.SETTINGS_NAV_BUTTON)
        self.system_button.setCheckable(True)
        left_panel_layout.addWidget(self.system_button)

        left_panel_layout.addStretch(1)  # Push everything to the top
        settings_layout.addWidget(left_panel)

        # ===== RIGHT PANEL: SETTINGS CONTENT =====
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(20, 20, 20, 20)

        # Create stacked widget to switch between different settings sections
        self.settings_stack = QStackedLayout()

        # 1. GENERAL SETTINGS PAGE
        general_settings_widget = QWidget()
        general_layout = QVBoxLayout(general_settings_widget)
        general_layout.setContentsMargins(0, 0, 0, 0)

        # General settings title
        general_title = QLabel("General Settings")
        general_title.setStyleSheet(Styles.SETTINGS_TITLE)
        general_layout.addWidget(general_title)        # Username settings
        username_layout = QVBoxLayout()
        username_label = QLabel("Your Name:")
        username_label.setStyleSheet(Styles.SETTINGS_SECTION)
        username_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your name")
        self.username_input.setStyleSheet(Styles.SETTINGS_INPUT)
        self.username_input.setFixedHeight(36)
        self.username_input.setFixedWidth(250)
        username_layout.addWidget(self.username_input)

        general_layout.addLayout(username_layout)
        general_layout.addStretch(1)

        # 2. NOTIFICATION SETTINGS PAGE
        notification_settings_widget = QWidget()
        notification_layout = QVBoxLayout(notification_settings_widget)
        notification_layout.setContentsMargins(0, 0, 0, 0)

        # Notification settings title
        notification_title = QLabel("Notification Settings")
        notification_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        notification_layout.addWidget(notification_title)

        # Sound toggle with horizontal layout
        sound_toggle_layout = QHBoxLayout()
        sound_enable_label = QLabel("Enable notification sound:")
        sound_enable_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        self.sound_checkbox = QCheckBox()
        self.sound_checkbox.setChecked(self.settings.get('sound_enabled', True))
        self.sound_checkbox.setStyleSheet(Styles.SETTINGS_CHECKBOX)
        sound_toggle_layout.addWidget(sound_enable_label)
        sound_toggle_layout.addWidget(self.sound_checkbox)
        sound_toggle_layout.addStretch()
        notification_layout.addLayout(sound_toggle_layout)

        notification_layout.addStretch(1)

        # 3. SNOOZE SETTINGS PAGE
        snooze_settings_widget = QWidget()
        snooze_layout = QVBoxLayout(snooze_settings_widget)
        snooze_layout.setContentsMargins(0, 0, 0, 0)

        # Snooze settings title
        snooze_title = QLabel("Snooze Settings")
        snooze_title.setStyleSheet(Styles.SETTINGS_TITLE)
        snooze_layout.addWidget(snooze_title)

        # Snooze settings content
        snooze_content_layout = QVBoxLayout()
        snooze_content_layout.setSpacing(15)

        # Snooze Enable/Disable
        snooze_enable_layout = QHBoxLayout()
        snooze_label = QLabel("Enable Snooze:")
        snooze_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        self.snooze_checkbox = QCheckBox()
        self.snooze_checkbox.setChecked(self.settings.get('snooze_enabled', True))
        self.snooze_checkbox.setStyleSheet(Styles.SETTINGS_CHECKBOX)
        snooze_enable_layout.addWidget(snooze_label)
        snooze_enable_layout.addWidget(self.snooze_checkbox)
        snooze_enable_layout.addStretch()
        snooze_content_layout.addLayout(snooze_enable_layout)
        
        # Snooze Time Setting
        snooze_time_layout = QHBoxLayout()
        snooze_time_label = QLabel("Snooze Time (minutes):")
        snooze_time_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        self.snooze_time_spinbox = QSpinBox()
        self.snooze_time_spinbox.setRange(1, 5)
        self.snooze_time_spinbox.setValue(self.settings.get('snooze_time', 5))
        self.snooze_time_spinbox.setStyleSheet(Styles.SETTINGS_SPINBOX)
        snooze_time_layout.addWidget(snooze_time_label)
        snooze_time_layout.addWidget(self.snooze_time_spinbox)
        snooze_time_layout.addStretch()
        snooze_content_layout.addLayout(snooze_time_layout)
        
        # Max Snooze Count Setting
        snooze_count_layout = QHBoxLayout()
        snooze_count_label = QLabel("Max Snooze Count:")
        snooze_count_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        self.snooze_count_spinbox = QSpinBox()
        self.snooze_count_spinbox.setRange(1, 3)
        self.snooze_count_spinbox.setValue(self.settings.get('max_snooze_count', 3))
        self.snooze_count_spinbox.setStyleSheet(Styles.SETTINGS_SPINBOX)
        snooze_count_layout.addWidget(snooze_count_label)
        snooze_count_layout.addWidget(self.snooze_count_spinbox)
        snooze_count_layout.addStretch()
        snooze_content_layout.addLayout(snooze_count_layout)
        
        snooze_layout.addLayout(snooze_content_layout)
        snooze_layout.addStretch(1)

        # 4. SYSTEM SETTINGS PAGE
        system_settings_widget = QWidget()
        system_layout = QVBoxLayout(system_settings_widget)
        system_layout.setContentsMargins(0, 0, 0, 0)

        # System settings title
        system_title = QLabel("System Settings")
        system_title.setStyleSheet(Styles.SETTINGS_TITLE)
        system_layout.addWidget(system_title)

        # System settings content
        system_content_layout = QVBoxLayout()
        system_content_layout.setSpacing(15)

        # Auto-start settings
        auto_start_layout = QHBoxLayout()
        auto_start_label = QLabel("Start at login:")
        auto_start_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        self.auto_start_checkbox = QCheckBox()
        self.auto_start_checkbox.setChecked(self.settings.get('auto_start', False))
        self.auto_start_checkbox.setStyleSheet(Styles.SETTINGS_CHECKBOX)
        auto_start_layout.addWidget(auto_start_label)
        auto_start_layout.addWidget(self.auto_start_checkbox)
        auto_start_layout.addStretch()
        system_content_layout.addLayout(auto_start_layout)
        
        system_layout.addLayout(system_content_layout)
        system_layout.addStretch(1)

        # Add all pages to the stacked widget
        self.settings_stack.addWidget(general_settings_widget)
        self.settings_stack.addWidget(notification_settings_widget)
        self.settings_stack.addWidget(snooze_settings_widget)
        self.settings_stack.addWidget(system_settings_widget)
        right_panel_layout.addLayout(self.settings_stack)

        # Save button at the bottom of right panel
        save_button = QPushButton("Save Settings")
        save_button.setFixedSize(150, 44)
        save_button.setStyleSheet(Styles.START_BUTTON)
        save_button.clicked.connect(self.save_settings)
        right_panel_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight)

        settings_layout.addWidget(right_panel, 1)  # Give the right panel stretch factor 1        # Connect navigation buttons to switch between settings pages
        self.general_button.clicked.connect(lambda: self.switch_settings_page(0))
        self.notification_button.clicked.connect(lambda: self.switch_settings_page(1))
        self.snooze_button.clicked.connect(lambda: self.switch_settings_page(2))
        self.system_button.clicked.connect(lambda: self.switch_settings_page(3))
        
        # Setup notification sound with proper error handling
        try:
            self.notification_sound = QSoundEffect(self)
            self.notification_sound.setSource(QUrl.fromLocalFile(resource_path(r"dist\\assets\\sounds\\notification_001.wav")))
            self.notification_sound.setLoopCount(1)
            self.notification_sound.setVolume(0.5)
        except Exception:
            # If sound setup fails, continue without sound
            self.notification_sound = None
        
        # Set initial values
        self.load_settings(self.settings)

    def switch_settings_page(self, index):
        # Change the page in the stacked widget
        self.settings_stack.setCurrentIndex(index)
          # Reset all button states first
        self.general_button.setChecked(False)
        self.general_button.setStyleSheet(Styles.SETTINGS_NAV_BUTTON)
        self.notification_button.setChecked(False)
        self.notification_button.setStyleSheet(Styles.SETTINGS_NAV_BUTTON)
        self.snooze_button.setChecked(False)
        self.snooze_button.setStyleSheet(Styles.SETTINGS_NAV_BUTTON)
        self.system_button.setChecked(False)
        self.system_button.setStyleSheet(Styles.SETTINGS_NAV_BUTTON)
        
        # Set active button based on index
        if index == 0:
            self.general_button.setChecked(True)
            self.general_button.setStyleSheet(Styles.SETTINGS_ACTIVE_NAV_BUTTON)
        elif index == 1:
            self.notification_button.setChecked(True)
            self.notification_button.setStyleSheet(Styles.SETTINGS_ACTIVE_NAV_BUTTON)
        elif index == 2:
            self.snooze_button.setChecked(True)
            self.snooze_button.setStyleSheet(Styles.SETTINGS_ACTIVE_NAV_BUTTON)
        elif index == 3:
            self.system_button.setChecked(True)
            self.system_button.setStyleSheet(Styles.SETTINGS_ACTIVE_NAV_BUTTON)

    def load_settings(self, settings):
        # Load values into UI elements
        if 'username' in settings:
            self.username_input.setText(settings['username'])
        
        if 'sound_enabled' in settings:
            self.sound_checkbox.setChecked(settings['sound_enabled'])

        if 'snooze_enabled' in settings:
            self.snooze_checkbox.setChecked(settings['snooze_enabled'])

        if 'snooze_time' in settings:
            self.snooze_time_spinbox.setValue(settings['snooze_time'])

        if 'max_snooze_count' in settings:
            self.snooze_count_spinbox.setValue(settings['max_snooze_count'])

        if 'auto_start' in settings:
            self.auto_start_checkbox.setChecked(settings['auto_start'])

    def save_settings(self):
        # Collect all settings
        new_settings = {
            'username': self.username_input.text().strip(),
            'sound_enabled': self.sound_checkbox.isChecked(),
            'snooze_enabled': self.snooze_checkbox.isChecked(),
            'snooze_time': self.snooze_time_spinbox.value(),
            'max_snooze_count': self.snooze_count_spinbox.value(),
            'auto_start': self.auto_start_checkbox.isChecked()
        }
        
        # Emit signal with new settings
        self.settingsSaved.emit(new_settings)

    def get_focus_time(self):
        """Returns the focus time in seconds from the main application's input fields"""
        if hasattr(self.parent(), 'focus_hours') and hasattr(self.parent(), 'focus_minutes') and hasattr(self.parent(), 'focus_seconds'):
            return (self.parent().focus_hours.value() * 3600 + 
                    self.parent().focus_minutes.value() * 60 + 
                    self.parent().focus_seconds.value())
        return 1500  # Default to 25 minutes if fields aren't available