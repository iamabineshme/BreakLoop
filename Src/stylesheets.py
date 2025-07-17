class Styles:
    """Centralized class for all application styles"""
    
    # Main window styles
    MAIN_WINDOW = "background-color: #1e1e1e; color: white; border-radius: 16px;"
    
    # Menu button styles
    MENU_BUTTON = """
        QPushButton {
            color: white;
            padding: 8px 12px 8px 8px;
            border-radius: 16px;
            text-align: left;
            icon-size: 16px;
        }
        QPushButton:hover {
            background-color: #3e3e3e;
        }
    """
    
    QUIT_BUTTON = """
        QPushButton {
            color: white;
            padding: 8px 12px 8px 8px;
            border-radius: 16px;
            text-align: left;
            icon-size: 16px;
        }
        QPushButton:hover {
            background-color: #DB394C;
        }
    """
    
    # Labels
    GREETING_LABEL = "font-size: 18px; color: #ffffff; font-weight: bold; padding-left: 15px;"
    TIMER_LABEL = "padding: 20px; color: #F3FFC6;"
    STATUS_LABEL = "font-size: 16px; color: #cccccc; margin-top: 5px;"
    
    # Input field labels
    INPUT_LABEL = "color: white; height: 32px; font-size: 16px; font-weight: bold;"

    # Spinbox styles
    SPINBOX = """
        QSpinBox {
            border: 2px solid #3D3D3D;
            background-color: #2e2e2e;
            color: white;
        }
        QSpinBox:focus {
            border: 2px solid #06BCC1;
        }
    """

    SETTINGS_SPINBOX = """
        QSpinBox {
            width: 32px;
            height: 32px;
            border: 2px solid #3D3D3D;
            background-color: #2e2e2e;
            color: white;
        }
        QSpinBox:focus {
            border: 2px solid #06BCC1;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            width: 0px;
            height: 0px;
            border: none;
        }
    """
    
    # Button styles
    START_BUTTON = "border-radius: 22px; background-color: #06BCC1; font-size: 12px; font-weight: bold; color: black; icon-size: 24px;"
    BREAK_BUTTON = "border-radius: 22px; background-color: #C3EB78; font-size: 12px; font-weight: bold; color: black; icon-size: 24px;"
    PAUSE_BUTTON = "border-radius: 22px; background-color: rgb(255, 255, 255); font-size: 12px; font-weight: bold; color: black; icon-size: 24px;"
    STOP_BUTTON = "border-radius: 22px; background-color: rgb(255, 100, 100); font-size: 12px; font-weight: bold; color: black; icon-size: 24px;"
    
    # Settings styles
    SETTINGS_NAV_BUTTON = """
        QPushButton {
            text-align: left;
            padding: 10px 15px;
            border: none;
            background-color: transparent;
            color: white;
            border-radius: 0px;
        }
        QPushButton:hover {
            background-color: #3e3e3e;
        }
        QPushButton:checked {
            background-color: #06BCC1;
            color: black;
            font-weight: bold;
        }
    """
    
    SETTINGS_ACTIVE_NAV_BUTTON = """
        QPushButton {
            text-align: left;
            padding: 10px 15px;
            border: none;
            background-color: #353535;
            color: white;
            border-radius: 0px;
        }
        QPushButton:hover {
            background-color: #3e3e3e;
        }
        QPushButton:checked {
            background-color: #1C1C1C;
            color: white;
            font-weight: bold;
        }
    """
    
    SETTINGS_TITLE = "font-size: 20px; font-weight: bold; margin-bottom: 15px;"
    SETTINGS_SECTION = "font-size: 12px;"
    SETTINGS_INPUT = """
        QLineEdit {
            background-color: #2e2e2e;
            border: 2px solid #3D3D3D;
            color: white;
            padding: 8px;
            font-size: 16px;
            border-radius: 18px;
            border-color: #3D3D3D;
        }
        QLineEdit:focus {
            border: 2px solid #FFF2E0;
            border-color: #FFF2E0;
        }
    """

    SETTINGS_CHECKBOX = """
        QCheckBox {
            color: #CCCCCC;
            font-size: 14px;
            spacing: 5px;
        }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
        }
        QCheckBox::indicator:unchecked {
            border: 1px solid #D3ECCD;
            background-color: #2D2D2D;
            border-radius: 8px;
        }
        QCheckBox::indicator:checked {
            border: 1px solid #D3ECCD;
            background-color: #06923E;
            border-radius: 8px;
        }
    """
    
    SAVE_BUTTON = "border-radius: 4px; background-color: #06BCC1; font-size: 12px; font-weight: bold; color: black;"
    TEST_SOUND_BUTTON = "border-radius: 4px; background-color: #2e2e2e; padding: 5px 10px;"
    
    # Break overlay styles
    BREAK_OVERLAY_TIMER = """
        font-family: 'Inter', sans-serif; 
        font-size: 60px; 
        font-weight: bold; 
        color: #ffffff;
    """
    
    BREAK_OVERLAY_BUTTON = """
        QPushButton {
            border-radius: 30px;
            background-color: rgb(255, 100, 100);
            border: 2px solid #000000;
            font-size: 16px;
            font-weight: bold;
            color: #000000;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
    """

    SNOOZE_OVERLAY_BUTTON = """
        QPushButton {
            border-radius: 30px;
            background-color: #06BCC1;
            border: 2px solid #000000;
            font-size: 16px;
            font-weight: bold;
            color: #000000;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
    """
    
    BREAK_OVERLAY_QUOTE = """
        font-family: 'Inter', sans-serif; 
        font-size: 18px; 
        font-style: italic;
        color: #000000;
        margin: 10px 30px;
        background-color: rgba(255, 255, 255, 150);
        padding: 15px;
        border-radius: 10px;
    """
    
    # Tray menu styles
    TRAY_TIMER_LABEL = "color: rgba(255, 255, 255, 0.5); padding: 5px;"
    
    # Mini window styles
    MINI_WINDOW = """
        background: transparent;
    """
    
    MINI_TIMER_LABEL = """
        color: #ECF0F1;
        margin-bottom: 5px;
        padding: 3px;
    """
    
    MINI_BUTTON = """
        QPushButton {
            background-color: transparent;
            border: none;
            border-radius: 16px;
        }
        QPushButton:hover {
            background-color: rgba(52, 152, 219, 0.7);
        }
        QPushButton:pressed {
            background-color: rgba(41, 128, 185, 0.9);
        }
    """
    
    MINIMIZE_BUTTON = """
        QPushButton {
            
            border-radius: 15px;
            padding: 3px;
            color: white;
        }
        QPushButton:hover {
            background-color: #3e3e3e;
        }
        QPushButton:pressed {
            background-color: #3e3e3e;
        }
    """
