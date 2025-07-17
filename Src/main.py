from PyQt6.QtWidgets import (QApplication, QWidgetAction, QMainWindow, QLabel, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QWidget, QSystemTrayIcon, QMenu, QSpinBox, 
                            QMessageBox, QStackedLayout)
from PyQt6.QtGui import QIcon, QAction, QCursor
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from datetime import datetime
import sys
from PyQt6.QtGui import QFontDatabase, QFont
from stylesheets import Styles  # Import the Styles class
from break_overlay import BreakOverlay # Import the BreakOverlay class
from settings_window import SettingsWindow  # Import SettingsWindow class
from mini_window import MiniWindow  # Add this import
import os
import auto_start  # Import the auto_start module

def get_settings_path():
    """Get the path to the settings file in user's home directory"""
    home_dir = os.path.expanduser("~")
    app_dir = os.path.join(home_dir, ".breakloop")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(app_dir):
        try:
            os.makedirs(app_dir)
        except Exception as e:
            print(f"Warning: Could not create settings directory: {e}")
            # Fall back to current directory if can't create app directory
            return "timer_app_settings.txt"
    
    return os.path.join(app_dir, "timer_app_settings.txt")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    full_path = os.path.join(base_path, relative_path)
    
    # Check if file exists and log if it doesn't
    if not os.path.exists(full_path):
        print(f"Warning: Resource file not found: {full_path}")
    
    return full_path

class TimerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Break Loop")
        self.setWindowIcon(QIcon(resource_path(r"dist\\assets\\icons\\app_icon_64px.svg")))
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(600, 600)
        self.setStyleSheet(Styles.MAIN_WINDOW)

        # Create main widget and vertical layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        
        # ========== FIRST LAYOUT: MENU BAR (FIXED) ========== 
        menu_layout = QHBoxLayout()
        menu_layout.setContentsMargins(8, 8, 8, 8)
        menu_layout.setSpacing(4)  # Set spacing between buttons

        # Home Button
        home_button = QPushButton("Home", self)
        home_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\home_24dp.svg")))
        home_button.setStyleSheet(Styles.MENU_BUTTON)
        home_button.clicked.connect(self.show_main_view)
        menu_layout.addWidget(home_button)

        # Settings Button
        settings_button = QPushButton("Settings", self)
        settings_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\settings_24dp.svg")))
        settings_button.setStyleSheet(Styles.MENU_BUTTON)
        settings_button.clicked.connect(self.open_settings)
        menu_layout.addWidget(settings_button)

        # Info Button
        info_button = QPushButton("Info", self)
        info_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\info_24dp.svg")))
        info_button.setStyleSheet(Styles.MENU_BUTTON)
        info_button.clicked.connect(self.show_info)
        menu_layout.addWidget(info_button)

        # Quit Button
        quit_button = QPushButton("Quit", self)
        quit_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\close_24dp_white.svg")))
        quit_button.setStyleSheet(Styles.QUIT_BUTTON)
        quit_button.clicked.connect(self.quit_app)
        menu_layout.addWidget(quit_button)

        # Add flexible space at the end to push buttons to the left
        menu_layout.addStretch(1)
        
        # Add Minimize to mini window button on the right side
        self.minimize_button = QPushButton("", self)
        self.minimize_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\minimize_button_24dp.svg")))
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet(Styles.MINIMIZE_BUTTON)
        self.minimize_button.clicked.connect(self.minimize_to_mini)
        menu_layout.addWidget(self.minimize_button)

        # Add the fixed menu bar to the main layout first
        main_layout.addLayout(menu_layout)
        
        # ========== CREATE STACKED LAYOUT FOR SWITCHABLE CONTENT ========== 
        self.stack_layout = QStackedLayout()
        
        # ========== CREATE MAIN VIEW CONTAINER ========== 
        self.main_container = QWidget()
        main_container_layout = QVBoxLayout(self.main_container)
        main_container_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Greeting label
        self.greeting_label = QLabel("Welcome!", self)
        self.greeting_label.setStyleSheet(Styles.GREETING_LABEL)
        self.greeting_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_container_layout.addWidget(self.greeting_label)
        main_container_layout.addSpacing(10)  # Add spacing after greeting

        # ========== SECOND LAYOUT: TIMER ========== 
        timer_layout = QVBoxLayout()
        timer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.setSpacing(10)  # Add spacing between elements

        # Load custom font from file
        font_id = QFontDatabase.addApplicationFont(resource_path(r"dist\\assets\\fonts\\Inter_28pt-Regular.ttf"))

        # Create timer label with custom font
        self.timer_label = QLabel("00:00:00", self)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Apply custom font if it loaded successfully
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            timer_font = QFont(font_family, 44)
            timer_font.setBold(True)
            self.timer_label.setFont(timer_font)
        
        self.timer_label.setStyleSheet(Styles.TIMER_LABEL)
        timer_layout.addWidget(self.timer_label)

        # Session status label - shows what session is active or notifications
        self.status_label = QLabel("Ready to start", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(Styles.STATUS_LABEL)
        timer_layout.addWidget(self.status_label)

        
        # ========== THIRD LAYOUT: INPUT FIELDS AND BUTTONS ========== 
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(20, 20, 20, 60)
        
        # Focus Session & Break Length Input Fields (Same Row)
        input_layout = QHBoxLayout()
        input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        
        # Focus Time Inputs
        focus_time_layout = QVBoxLayout()
        self.focus_label = QLabel("Focus Time (hh:mm:ss):")
        self.focus_label.setStyleSheet(Styles.INPUT_LABEL)
        self.focus_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        focus_time_layout.addWidget(self.focus_label)
        
        focus_input_layout = QHBoxLayout()
        self.focus_hours = QSpinBox()
        self.focus_hours.setRange(0, 99)
        self.focus_hours.setValue(0)
        self.focus_hours.setFixedWidth(64)
        self.focus_hours.setFixedHeight(32)
        self.focus_hours.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.focus_hours.setStyleSheet(Styles.SPINBOX)
        focus_input_layout.addWidget(self.focus_hours)

        self.focus_minutes = QSpinBox()
        self.focus_minutes.setRange(0, 59)
        self.focus_minutes.setValue(25)
        self.focus_minutes.setFixedWidth(64)
        self.focus_minutes.setFixedHeight(32)
        self.focus_minutes.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.focus_minutes.setStyleSheet(Styles.SPINBOX)
        focus_input_layout.addWidget(self.focus_minutes)

        self.focus_seconds = QSpinBox()
        self.focus_seconds.setRange(0, 59)
        self.focus_seconds.setValue(0)
        self.focus_seconds.setFixedWidth(64)
        self.focus_seconds.setFixedHeight(32)
        self.focus_seconds.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.focus_seconds.setStyleSheet(Styles.SPINBOX)
        focus_input_layout.addWidget(self.focus_seconds)
        
        # Connect validation for focus time inputs
        self.focus_hours.valueChanged.connect(self.validate_minimum_time)
        self.focus_minutes.valueChanged.connect(self.validate_minimum_time)
        self.focus_seconds.valueChanged.connect(self.validate_minimum_time)
        
        focus_time_layout.addLayout(focus_input_layout)
        input_layout.addLayout(focus_time_layout)
        
        # Spacer
        spacer = QWidget()
        spacer.setFixedWidth(20)
        input_layout.addWidget(spacer)
        
        # Break Time Inputs
        break_time_layout = QVBoxLayout()
        self.break_label = QLabel("Break Time (hh:mm:ss):")
        self.break_label.setStyleSheet(Styles.INPUT_LABEL)
        self.break_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        break_time_layout.addWidget(self.break_label)
        
        break_input_layout = QHBoxLayout()
        self.break_hours = QSpinBox()
        self.break_hours.setRange(0, 99)
        self.break_hours.setValue(0)
        self.break_hours.setFixedWidth(64)
        self.break_hours.setFixedHeight(32)
        self.break_hours.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.break_hours.setStyleSheet(Styles.SPINBOX)
        break_input_layout.addWidget(self.break_hours)

        self.break_minutes = QSpinBox()
        self.break_minutes.setRange(0, 59)
        self.break_minutes.setValue(5)
        self.break_minutes.setFixedWidth(64)
        self.break_minutes.setFixedHeight(32)
        self.break_minutes.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.break_minutes.setStyleSheet(Styles.SPINBOX)
        break_input_layout.addWidget(self.break_minutes)

        self.break_seconds = QSpinBox()
        self.break_seconds.setRange(0, 59)
        self.break_seconds.setValue(0)
        self.break_seconds.setFixedWidth(64)
        self.break_seconds.setFixedHeight(32)
        self.break_seconds.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.break_seconds.setStyleSheet(Styles.SPINBOX)
        break_input_layout.addWidget(self.break_seconds)
        
        # Connect validation for break time inputs
        self.break_hours.valueChanged.connect(self.validate_minimum_break_time)
        self.break_minutes.valueChanged.connect(self.validate_minimum_break_time)
        self.break_seconds.valueChanged.connect(self.validate_minimum_break_time)
        
        break_time_layout.addLayout(break_input_layout)
        input_layout.addLayout(break_time_layout)
        bottom_layout.addLayout(input_layout)
        
        # Buttons Layout (Single Row)
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons_layout.setContentsMargins(0, 15, 0, 0)
        buttons_layout.setSpacing(10)
        
        # Start Focus Session Button
        self.start_button = QPushButton("Start Focus Session", self)
        self.start_button.setFixedSize(150, 44)
        self.start_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\play_arrow_24dp_black.svg")))
        self.start_button.setStyleSheet(Styles.START_BUTTON)
        self.start_button.clicked.connect(self.start_focus_session)
        buttons_layout.addWidget(self.start_button)
        
        # Take Break Now Button
        self.break_button = QPushButton("Take Break Now", self)
        self.break_button.setFixedSize(150, 44)
        self.break_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\bolt_24dp_black.svg")))
        self.break_button.setStyleSheet(Styles.BREAK_BUTTON)
        self.break_button.clicked.connect(self.take_break_now)
        buttons_layout.addWidget(self.break_button)
        
        # Pause/Resume Button - initially hidden
        self.pause_button = QPushButton("Pause", self)
        self.pause_button.setFixedSize(100, 44)
        self.pause_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\pause_24dp_black.svg")))
        self.pause_button.setStyleSheet(Styles.PAUSE_BUTTON)
        self.pause_button.clicked.connect(self.pause_timer)
        buttons_layout.addWidget(self.pause_button)
        self.pause_button.hide()  # Hide by default
        
        # Stop Focus Session Button - initially hidden
        self.stop_button = QPushButton("Stop Session", self)
        self.stop_button.setFixedSize(120, 44)
        self.stop_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\stop_24dp_black.svg")))
        self.stop_button.setStyleSheet(Styles.STOP_BUTTON)
        self.stop_button.clicked.connect(self.stop_focus_session)
        buttons_layout.addWidget(self.stop_button)
        self.stop_button.hide()  # Hide by default
        
        bottom_layout.addLayout(buttons_layout)
        
        main_container_layout.addLayout(timer_layout, 1)
        main_container_layout.addLayout(bottom_layout)

        # Add containers to stack layout
        self.stack_layout.addWidget(self.main_container)
        
        # Add the stack layout to main layout
        main_layout.addLayout(self.stack_layout, 1) # Give it stretch factor
        
        # Set the central widget
        self.setCentralWidget(central_widget)
        
        # Timer Setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0
        self.is_focus_session = False  # Initialize session state
        self.is_snooze_active = False  # Track if we're in snooze mode
        self.current_snooze_count = 0  # Track snooze count for current break session
        
        # System Tray Setup
        self.tray_icon = QSystemTrayIcon(QIcon(resource_path(r"dist\\assets\\icons\\trayicon_16px_blue.svg")), self)
        self.tray_icon.setToolTip("Break Loop")
        tray_menu = QMenu()

        # Timer display in tray (disabled, faded)
        self.timer_label_menu = QLabel("Next session in 00:00:00", self)
        self.timer_label_menu.setStyleSheet(Styles.TRAY_TIMER_LABEL)
        timer_widget_action = QWidgetAction(self)
        timer_widget_action.setDefaultWidget(self.timer_label_menu)
        tray_menu.addAction(timer_widget_action)

        # Open App Action
        open_action = QAction("Open App", self)
        open_action.triggered.connect(self.show)
        tray_menu.addAction(open_action)

        # Start Focus Session Action
        start_focus_action = QAction("Start Focus Session", self)
        start_focus_action.triggered.connect(self.start_focus_session)
        tray_menu.addAction(start_focus_action)

        # Take Break Action
        take_break_action = QAction("Take Break", self)
        take_break_action.triggered.connect(self.take_break_now)
        tray_menu.addAction(take_break_action)

        # Quit Action (quits the app completely)
        tray_quit_action = QAction("Quit", self)
        tray_quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(tray_quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_icon_activated)        # Notification Sound Setup with error handling
        try:
            self.notification_sound = QSoundEffect(self)
            notification_path = resource_path(r"dist\\assets\\sounds\\notification_001.wav")
            if os.path.exists(notification_path):
                self.notification_sound.setSource(QUrl.fromLocalFile(notification_path))
                self.notification_sound.setLoopCount(1)
                self.notification_sound.setVolume(0.5)
            else:
                print("Warning: Notification sound file not found")
                self.notification_sound = None
        except Exception as e:
            print(f"Error setting up notification sound: {e}")
            self.notification_sound = None

        # Settings storage
        self.settings = {
            'username': '',
            'sound_enabled': True,  # Default to sound enabled
            'snooze_enabled': True,  # Default snooze enabled
            'snooze_time': 5,  # Default 5 minutes
            'max_snooze_count': 3,  # Default max 3 snoozes
            'auto_start': False  # Default auto-start disabled
        }
        
        # Initialize username attribute
        self.username = ''
        
        # Load settings immediately
        self.load_settings()
        self.update_greeting()  # Uncomment this line
        
        # Initialize mini window (but don't show it yet)
        self.create_mini_window()

    def validate_minimum_time(self):
        """Ensure focus time is at least 40 seconds"""
        total_seconds = (self.focus_hours.value() * 3600 + 
                        self.focus_minutes.value() * 60 + 
                        self.focus_seconds.value())
        
        if total_seconds < 40 and total_seconds > 0:
            # Set to minimum 40 seconds
            self.focus_hours.setValue(0)
            self.focus_minutes.setValue(0)
            self.focus_seconds.setValue(40)

    def validate_minimum_break_time(self):
        """Ensure break time is at least 40 seconds"""
        total_seconds = (self.break_hours.value() * 3600 + 
                        self.break_minutes.value() * 60 + 
                        self.break_seconds.value())

        if total_seconds < 40 and total_seconds > 0:
            # Set to minimum 40 seconds
            self.break_hours.setValue(0)
            self.break_minutes.setValue(0)
            self.break_seconds.setValue(40)

    def create_mini_window(self):
        # Create mini window with current focus time as default
        focus_time = self.get_focus_time()
        formatted_time = self.format_time_for_display(focus_time)
        self.mini_window = MiniWindow(default_time=formatted_time)
        
        # Connect signals
        self.mini_window.expandWindow.connect(self.show_from_mini)
        self.mini_window.closeClicked.connect(self.quit_app)

    def get_focus_time(self):
        """Returns the focus time in seconds from the input fields"""
        return (self.focus_hours.value() * 3600 + 
                self.focus_minutes.value() * 60 + 
                self.focus_seconds.value())

    def format_time_for_display(self, seconds):
        """Format seconds into HH:MM:SS string"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def show_session_notification(self, message, start_session_callback):
        # Play custom notification sound
        self.notification_sound.play()
        # Replace popup notification with system tray notification
        self.tray_icon.showMessage("Notification", message)        # Allow clicking the tray message to open the app
        self.tray_icon.messageClicked.connect(self.show)
        # Auto-start the next session after 3 seconds.
        QTimer.singleShot(3000, start_session_callback)

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            h = self.remaining_time // 3600
            m = (self.remaining_time % 3600) // 60
            s = self.remaining_time % 60
            
            # Update timer display to show just the time
            time_text = f"{h:02}:{m:02}:{s:02}"
            self.timer_label.setText(time_text)
            
            # If break overlay is active, update its timer too
            if hasattr(self, 'break_overlay') and self.break_overlay is not None and self.break_overlay.isVisible():
                self.break_overlay.updateTimer(time_text)
            
            # Update mini window if it exists and is visible
            if hasattr(self, 'mini_window') and self.mini_window is not None and self.mini_window.isVisible():
                self.mini_window.update_timer(time_text)
            
            # Update status label to show current session type - with validation
            if hasattr(self, 'is_focus_session') and self.is_focus_session:
                self.status_label.setText("Focus Session in Progress")
                self.timer_label_menu.setText(f"Next break in {time_text}")
            elif hasattr(self, 'is_snooze_active') and self.is_snooze_active:
                self.status_label.setText("Snooze in Progress")
                self.timer_label_menu.setText(f"Break resumes in {time_text}")
            else:
                self.status_label.setText("Break in Progress")
                self.timer_label_menu.setText(f"Focus starts in {time_text}")
        else:
            self.timer.stop()
            # Validate session state before proceeding
            if hasattr(self, 'is_focus_session') and self.is_focus_session:
                # Update timer display
                self.timer_label.setText("00:00:00")
                # Display notification in status label
                self.status_label.setText("Focus session is over, time to take a break.")
                
                # Show fullscreen overlay instead of message box
                self.show_break_overlay()
                
            elif hasattr(self, 'is_snooze_active') and self.is_snooze_active:
                # Snooze time is over, show break overlay again
                self.is_snooze_active = False
                self.timer_label.setText("00:00:00")
                self.status_label.setText("Snooze is over, time for your break.")
                
                # Show the break overlay again
                self.show_break_overlay()
                
            else:
                # Update timer display
                self.timer_label.setText("00:00:00")
                # Display notification in status label
                self.status_label.setText("Break is over, let's get back to focus session.")
                
                # Close the break overlay if it exists
                if hasattr(self, 'break_overlay') and self.break_overlay is not None and self.break_overlay.isVisible():
                    self.break_overlay.close()
                    self.break_overlay = None  # Set to None instead of using del
                
                # Show notification and start focus session
                self.show_session_notification("Break is over, let's get back to focus session.", self.start_focus_session)

    def pause_timer(self):
        # Validate timer state before proceeding
        if not hasattr(self, 'remaining_time'):
            return
            
        if self.timer.isActive():
            self.timer.stop()
            self.pause_button.setText("Resume")
            self.pause_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\play_arrow_24dp_black.svg")))
            self.status_label.setText("Focus Session Paused")
            self.stop_button.show()  # Show stop button when paused
        else:
            # Only resume if there is remaining time
            if self.remaining_time > 0:
                self.timer.start(1000)
                self.pause_button.setText("Pause")
                self.pause_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\pause_24dp_black.svg")))
                self.stop_button.hide()  # Hide stop button when resumed                # Update status based on current session type
                if hasattr(self, 'is_focus_session') and self.is_focus_session:
                    self.status_label.setText("Focus Session in Progress")
                else:
                    self.status_label.setText("Break in Progress")

    def start_focus_session(self):
        # Validate timer input before starting
        total_time = (self.focus_hours.value() * 3600 +
                     self.focus_minutes.value() * 60 +
                     self.focus_seconds.value())
        
        if total_time <= 0:
            QMessageBox.warning(self, "Invalid Time", "Please set a valid focus time greater than 0.")
            return
        
        self.is_focus_session = True
        self.is_snooze_active = False  # Reset snooze state
        self.current_snooze_count = 0  # Reset snooze count for new session
        self.remaining_time = total_time
        
        # Update status immediately when starting session
        h = self.remaining_time // 3600
        m = (self.remaining_time % 3600) // 60
        s = self.remaining_time % 60
        self.timer_label.setText(f"{h:02}:{m:02}:{s:02}")
        self.status_label.setText("Focus Session in Progress")
        
        # Update button visibility
        self.start_button.hide()
        self.break_button.hide()
        self.pause_button.show()
        self.stop_button.hide()
        
        self.timer.start(1000)
        self.pause_button.setText("Pause")

    def stop_focus_session(self):
        # Stop the timer
        self.timer.stop()
        
        # Reset display
        self.timer_label.setText("00:00:00")
        self.status_label.setText("Ready to start")
        
        # Reset button visibility to default state
        self.start_button.show()
        self.break_button.show()
        self.pause_button.hide()
        self.pause_button.setIcon(QIcon(resource_path(r"dist\\assets\\icons\\pause_24dp_black.svg")))
        self.stop_button.hide()

    def take_break_now(self):
        # First show the break overlay
        self.show_break_overlay()
        
    def show_break_overlay(self):
        # Validate break time before starting
        break_time = (self.break_hours.value() * 3600 +
                     self.break_minutes.value() * 60 +
                     self.break_seconds.value())
        
        if break_time <= 0:
            QMessageBox.warning(self, "Invalid Time", "Please set a valid break time greater than 0.")
            return
        
        # Play custom notification sound if enabled
        if hasattr(self, 'notification_sound') and self.notification_sound and not self.notification_sound.isMuted():
            self.notification_sound.play()
          # Prepare snooze settings
        snooze_settings = {
            'snooze_enabled': self.settings.get('snooze_enabled', True),
            'snooze_time': self.settings.get('snooze_time', 5),
            'max_snooze_count': self.settings.get('max_snooze_count', 3),
            'current_snooze_count': self.current_snooze_count  # Pass current count
        }
        
        # Create and show the fullscreen overlay
        self.break_overlay = BreakOverlay(snooze_settings=snooze_settings)
        
        # Connect signals
        self.break_overlay.end_button.clicked.connect(self.end_break_overlay)
        self.break_overlay.snoozeRequested.connect(self.handle_snooze_request)
        
        # Set initial timer text
        h = self.break_hours.value()
        m = self.break_minutes.value()
        s = self.break_seconds.value()
        self.break_overlay.updateTimer(f"{h:02}:{m:02}:{s:02}")        # Start the break in the background
        self.is_focus_session = False
        self.is_snooze_active = False  # Reset snooze state for regular break
        self.current_snooze_count = 0  # Reset snooze count for new break session
        self.remaining_time = break_time
        
        # Update app status
        self.status_label.setText("Break in Progress")
        
        # Start the timer
        self.timer.start(1000)
        self.pause_button.setText("Pause")

    def end_break_overlay(self):
        if hasattr(self, 'break_overlay') and self.break_overlay is not None:
            # First stop the timer
            self.timer.stop()
            
            # Safely close the break overlay with fade out
            self.break_overlay.fade_out()            # Return to focus mode
            self.is_focus_session = True
            self.is_snooze_active = False  # Reset snooze state
            self.current_snooze_count = 0  # Reset snooze count when ending break
            self.remaining_time = (self.focus_hours.value() * 3600 +
                                  self.focus_minutes.value() * 60 +
                                  self.focus_seconds.value())
            
            # Update the timer display
            h = self.remaining_time // 3600
            m = (self.remaining_time % 3600) // 60
            s = self.remaining_time % 60
            time_text = f"{h:02}:{m:02}:{s:02}"
            self.timer_label.setText(time_text)
            
            # Update status
            self.status_label.setText("Focus Session in Progress")

            # Update button visibility
            self.start_button.hide()
            self.break_button.hide()
            self.pause_button.show()
            self.stop_button.hide()
            
            # Start the focus timer
            self.timer.start(1000)
            self.pause_button.setText("Pause")
            
            # Make sure we don't delete the break_overlay while it's fading out
            # Just set a timer to remove the reference after fade completes
            QTimer.singleShot(self.break_overlay.fade_duration + 100, self._cleanup_break_overlay)

    def handle_snooze_request(self, snooze_minutes):
        """Handle snooze request from break overlay"""
        # Close current break overlay
        if hasattr(self, 'break_overlay') and self.break_overlay is not None:
            self.break_overlay.fade_out()        # Convert snooze minutes to seconds and set as remaining time
        snooze_seconds = snooze_minutes * 60
        self.remaining_time = snooze_seconds
        self.is_focus_session = False  # Still in break mode
        self.is_snooze_active = True  # Set snooze state
        self.current_snooze_count += 1  # Increment snooze count
        
        # Update status
        self.status_label.setText(f"Break snoozed for {snooze_minutes} minutes")
        
        # Update timer display
        h = self.remaining_time // 3600
        m = (self.remaining_time % 3600) // 60
        s = self.remaining_time % 60
        self.timer_label.setText(f"{h:02}:{m:02}:{s:02}")
        
        # Restart the timer
        self.timer.start(1000)
        
        # Clean up break overlay reference after fade completes
        QTimer.singleShot(self.break_overlay.fade_duration + 100, self._cleanup_break_overlay)

    def _cleanup_break_overlay(self):
        """Helper method to safely remove break overlay reference"""
        if hasattr(self, 'break_overlay') and self.break_overlay is not None:
            self.break_overlay = None

    def minimize_to_mini(self):
        # Update mini window timer display
        if hasattr(self, 'remaining_time'):
            h = self.remaining_time // 3600
            m = (self.remaining_time % 3600) // 60
            s = self.remaining_time % 60
            time_text = f"{h:02}:{m:02}:{s:02}"
        else:
            time_text = "00:00:00"
            
        self.mini_window.update_timer(time_text)
        
        # Apply custom font to mini window if available
        if hasattr(self, 'timer_font_id') and self.timer_font_id != -1:
            QApplication.instance().setProperty(resource_path(r"dist\\assets\\fonts\\Inter_28pt-Regular.ttf", self.timer_font_id))
            QApplication.instance().setProperty(resource_path(r"dist\\assets\\fonts\\Inter_28pt-Regular.ttf", self.timer_font_family))

        # Hide main window and show mini window
        self.hide()
        self.mini_window.show()
    
    def show_from_mini(self):
        # Hide mini window and show main window
        self.mini_window.hide()
        self.show()
        self.activateWindow()  # Bring main window to front
    
    def quit_app(self):
        if hasattr(self, 'mini_window'):
            self.mini_window.close()
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        # When closing the main window, minimize to tray
        event.ignore()
        self.hide()
        if hasattr(self, 'mini_window'):
            self.mini_window.hide()
        self.tray_icon.showMessage("Timer App", "The app is minimized to the system tray.")

    def open_settings(self):
        try:
            # Create settings window with current settings
            self.settings_window = SettingsWindow(self, self.settings)
            
            # Connect the settingsSaved signal to update settings
            self.settings_window.settingsSaved.connect(self.update_settings)
            
            # Switch to the settings window in stack layout
            self.stack_layout.addWidget(self.settings_window)
            self.stack_layout.setCurrentWidget(self.settings_window)
            
        except Exception as e:
            print(f"Error opening settings: {e}")
            # Show error message to user
            QMessageBox.critical(self, "Error", f"Failed to open settings: {str(e)}")

    def update_settings(self, new_settings):
        try:
            # Update settings dictionary
            self.settings.update(new_settings)
            
            # Apply settings
            if 'username' in new_settings:
                self.username = new_settings['username']
            if 'sound_enabled' in new_settings:
                if hasattr(self, 'notification_sound') and self.notification_sound:
                    self.notification_sound.setMuted(not new_settings['sound_enabled'])
            if 'auto_start' in new_settings:
                self.apply_auto_start_setting(new_settings['auto_start'])
            
            # Save settings to file using the dedicated settings path
            settings_file = get_settings_path()
            with open(settings_file, "w") as f:
                f.write(f"{self.settings['username']}\n")
                f.write(f"{self.settings['sound_enabled']}\n")
                f.write(f"{self.settings['snooze_enabled']}\n")
                f.write(f"{self.settings['snooze_time']}\n")
                f.write(f"{self.settings['max_snooze_count']}\n")
                f.write(f"{self.settings['auto_start']}\n")  # Add auto_start setting
            
            # Update UI
            self.update_greeting()
            
            # Return to main view
            self.show_main_view()
            
        except PermissionError:
            print(f"Permission denied when writing to settings file: {settings_file}")
            QMessageBox.critical(self, "Permission Error", 
                            f"Cannot save settings: Permission denied.\n\nTried to save to: {settings_file}")
        except Exception as e:
            print(f"Error updating settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def apply_auto_start_setting(self, enabled):
        """Apply the auto-start setting by enabling or disabling auto-start"""
        try:
            # Check for missing dependencies
            dependency_status = auto_start.get_dependency_status()
            if not dependency_status["all_available"]:
                missing_deps = ", ".join(dependency_status["missing"])
                install_cmd = dependency_status.get("install_command", "")
                
                message = (f"Some dependencies required for auto-start are missing: {missing_deps}.\n\n"
                          f"To enable this feature, please install the missing dependencies:\n"
                          f"{install_cmd}")
                
                QMessageBox.warning(
                    self,
                    "Missing Dependencies",
                    message
                )
                return False
                
            if enabled:
                success = auto_start.enable_autostart()
                if not success:
                    print("Warning: Failed to enable auto-start")
                    QMessageBox.warning(
                        self, 
                        "Auto-Start Warning", 
                        "Failed to enable auto-start completely. This may require administrator privileges."
                    )
            else:
                success = auto_start.disable_autostart()
                if not success:
                    print("Warning: Failed to disable auto-start")
                    QMessageBox.warning(
                        self, 
                        "Auto-Start Warning", 
                        "Failed to disable auto-start completely. This may require administrator privileges."
                    )
            return True
        except Exception as e:
            print(f"Error applying auto-start setting: {e}")
            QMessageBox.critical(
                self,
                "Auto-Start Error",
                f"An error occurred while configuring auto-start: {str(e)}"
            )
            return False

    def load_settings(self):
        try:
            settings_file = get_settings_path()
            with open(settings_file, "r", encoding='utf-8') as f:
                settings = f.readlines()
                if len(settings) > 0:
                    username = settings[0].strip()
                    # Validate username input
                    if username and len(username) <= 50:  # Basic validation
                        self.settings['username'] = username
                        self.username = self.settings['username']
                if len(settings) > 1:
                    sound_setting = settings[1].strip().lower()
                    if sound_setting in ['true', 'false']:
                        self.settings['sound_enabled'] = sound_setting == 'true'
                        if hasattr(self, 'notification_sound') and self.notification_sound:
                            self.notification_sound.setMuted(not self.settings['sound_enabled'])
                if len(settings) > 2:
                    snooze_enabled = settings[2].strip().lower()
                    if snooze_enabled in ['true', 'false']:
                        self.settings['snooze_enabled'] = snooze_enabled == 'true'
                if len(settings) > 3:
                    try:
                        snooze_time = int(settings[3].strip())
                        if 1 <= snooze_time <= 5:
                            self.settings['snooze_time'] = snooze_time
                    except ValueError:
                        pass
                if len(settings) > 4:
                    try:
                        max_snooze_count = int(settings[4].strip())
                        if 1 <= max_snooze_count <= 3:
                            self.settings['max_snooze_count'] = max_snooze_count
                    except ValueError:
                        pass
                if len(settings) > 5:
                    auto_start_setting = settings[5].strip().lower()
                    if auto_start_setting in ['true', 'false']:
                        self.settings['auto_start'] = auto_start_setting == 'true'
                        # Only apply auto-start if dependencies are available
                        dependency_status = auto_start.get_dependency_status()
                        if dependency_status["all_available"]:
                            # Check if actual auto-start status matches setting
                            actual_status = auto_start.is_autostart_enabled()
                            if self.settings['auto_start'] != actual_status:
                                self.apply_auto_start_setting(self.settings['auto_start'])
        except FileNotFoundError:
            # No settings file yet - use defaults
            print(f"Settings file not found at {settings_file}, using defaults")
        except PermissionError:
            print(f"Permission denied when reading settings file: {settings_file}")
            # Continue with default settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Continue with default settings

    def update_greeting(self):
        current_hour = datetime.now().hour
        
        # Determine greeting based on time of day
        if 5 <= current_hour < 12:
            greeting = "Good morning"
        elif 12 <= current_hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        # Add name if available
        if self.username:
            greeting += f", {self.username}"
        greeting += "!"
        
        # Update label
        self.greeting_label.setText(greeting)

    def on_tray_icon_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Context, QSystemTrayIcon.ActivationReason.Trigger):
            self.tray_icon.contextMenu().popup(QCursor.pos())

    def show_info(self):
        info_text = (
            "<html>"
            "<h3>Break Loop</h3>"
            "- Contact: <a href='mailto:iamabineshme@gmail.com'>iamabineshme@gmail.com</a><br>"
            "- Website: <a href='https://iamabineshme.notion.site/breakloop'>https://iamabineshme.notion.site/breakloop</a><br>"
            "- Leave your feedbacks and check updates on website<br><br>"
            "Break Loop is a productivity-focused timer application designed to help users manage work sessions and breaks effectively. The app employs a structured approach to time management with customizable focus and break intervals. Vibe coded by Abinesh and licensed as open-source under the MIT / GPL v3 license.</p></br>"
            "</html>"
        )
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About Timer App")
        msg_box.setText(info_text)
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.exec()

    def show_main_view(self):
        """Switch to the main view in the stacked layout"""
        try:
            # Switch to main view and remove any other temporary widgets
            if hasattr(self, 'settings_window') and self.settings_window is not None:
                # Only try to remove and clean up if it exists in the stack
                if self.stack_layout.indexOf(self.settings_window) != -1:
                    self.stack_layout.removeWidget(self.settings_window)
                    self.settings_window.deleteLater()
                    self.settings_window = None
                    
            # Make sure main container is in the stack layout
            if self.stack_layout.indexOf(self.main_container) == -1:
                self.stack_layout.addWidget(self.main_container)
                
            # Switch to main container
            self.stack_layout.setCurrentWidget(self.main_container)
        except Exception as e:
            print(f"Error showing main view: {e}")
            # Show error message to user
            QMessageBox.critical(self, "Error", f"Failed to switch to main view: {str(e)}")
        
# Entry point to launch the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimerApp()
    window.show()
    sys.exit(app.exec())