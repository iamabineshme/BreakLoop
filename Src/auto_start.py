import os
import sys
import winreg
import ctypes
import subprocess

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Check if pywin32 is available
PYWIN32_AVAILABLE = False
try:
    import pythoncom
    from win32com.client import Dispatch
    PYWIN32_AVAILABLE = True
except ImportError:
    # pythoncom module is not available
    pass

def is_admin():
    """Check if the current user has admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def get_startup_folder_path():
    """Get the path to the current user's startup folder"""
    startup_folder = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
    return startup_folder

def get_app_path():
    """Get the path to the current executable"""
    if getattr(sys, 'frozen', False):
        # Running as executable (PyInstaller)
        return sys.executable
    else:
        # Running as script
        return sys.argv[0]

def create_shortcut(target_path, shortcut_path, working_dir=None, icon_path=None):
    """Create a Windows shortcut (.lnk) file"""
    if not PYWIN32_AVAILABLE:
        # Use fallback method with PowerShell if pywin32 is not available
        return create_shortcut_powershell(target_path, shortcut_path, working_dir, icon_path)
    
    try:
        pythoncom.CoInitialize()
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        
        if working_dir:
            shortcut.WorkingDirectory = working_dir
        if icon_path:
            shortcut.IconLocation = icon_path
            
        shortcut.save()
        return True
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        # Fall back to PowerShell method
        return create_shortcut_powershell(target_path, shortcut_path, working_dir, icon_path)

def create_shortcut_powershell(target_path, shortcut_path, working_dir=None, icon_path=None):
    """Create a shortcut using PowerShell (fallback method)"""
    try:
        # Base PowerShell command
        ps_cmd = f'$WshShell = New-Object -comObject WScript.Shell; '
        ps_cmd += f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); '
        ps_cmd += f'$Shortcut.TargetPath = "{target_path}"; '
        
        if working_dir:
            ps_cmd += f'$Shortcut.WorkingDirectory = "{working_dir}"; '
        if icon_path:
            ps_cmd += f'$Shortcut.IconLocation = "{icon_path}"; '
            
        ps_cmd += '$Shortcut.Save()'
        
        # Execute PowerShell command
        subprocess.run(['powershell', '-Command', ps_cmd], 
                      capture_output=True, 
                      text=True, 
                      check=True)
        return True
    except Exception as e:
        print(f"Error creating shortcut with PowerShell: {e}")
        return False

def enable_autostart_registry():
    """Enable auto-start using Windows registry (requires admin rights)"""
    try:
        app_path = get_app_path()
        app_name = "BreakLoopTimer"
        
        if is_admin():
            # Use HKEY_LOCAL_MACHINE for all users (requires admin)
            reg_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
                0, 
                winreg.KEY_WRITE
            )
        else:
            # Use HKEY_CURRENT_USER for current user only
            reg_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
                0, 
                winreg.KEY_WRITE
            )
            
        winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, f'"{app_path}"')
        winreg.CloseKey(reg_key)
        return True
    except Exception as e:
        print(f"Error setting registry key: {e}")
        return False

def disable_autostart_registry():
    """Disable auto-start by removing registry entry"""
    try:
        app_name = "BreakLoopTimer"
        
        # Try HKEY_CURRENT_USER first
        try:
            reg_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
                0, 
                winreg.KEY_WRITE
            )
            winreg.DeleteValue(reg_key, app_name)
            winreg.CloseKey(reg_key)
            return True
        except WindowsError:
            # If not found in HKCU, try HKLM if we have admin rights
            if is_admin():
                reg_key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, 
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
                    0, 
                    winreg.KEY_WRITE
                )
                winreg.DeleteValue(reg_key, app_name)
                winreg.CloseKey(reg_key)
                return True
            return False
    except Exception as e:
        print(f"Error removing registry key: {e}")
        return False

def enable_autostart_folder():
    """Enable auto-start by creating shortcut in startup folder"""
    try:
        app_path = get_app_path()
        app_dir = os.path.dirname(os.path.abspath(app_path))
        startup_folder = get_startup_folder_path()
        shortcut_path = os.path.join(startup_folder, "BreakLoopTimer.lnk")
        
        # Try to find a suitable icon file
        icon_path = None
        
        # First try to find .ico file (preferred for shortcuts)
        ico_path = resource_path(os.path.join("Icons", "app_icon_64px.ico"))
        if os.path.exists(ico_path):
            icon_path = ico_path
        else:
            # Try relative to app directory
            ico_path_relative = os.path.join(app_dir, "Icons", "app_icon_64px.ico")
            if os.path.exists(ico_path_relative):
                icon_path = ico_path_relative
            else:
                # Fall back to using the executable itself
                icon_path = app_path
            
        return create_shortcut(
            target_path=app_path,
            shortcut_path=shortcut_path,
            working_dir=app_dir,
            icon_path=icon_path
        )
    except Exception as e:
        print(f"Error creating startup shortcut: {e}")
        return False

def disable_autostart_folder():
    """Disable auto-start by removing shortcut from startup folder"""
    try:
        startup_folder = get_startup_folder_path()
        shortcut_path = os.path.join(startup_folder, "BreakLoopTimer.lnk")
        
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
        return True
    except Exception as e:
        print(f"Error removing startup shortcut: {e}")
        return False

def enable_autostart():
    """Enable auto-start using available methods"""
    # Try registry method first (more reliable)
    if enable_autostart_registry():
        return True
    
    # Fall back to startup folder method
    return enable_autostart_folder()

def disable_autostart():
    """Disable auto-start using all methods"""
    # Disable both methods to ensure it's fully disabled
    registry_success = disable_autostart_registry()
    folder_success = disable_autostart_folder()
    
    # Return True if at least one method succeeded
    return registry_success or folder_success

def is_autostart_enabled():
    """Check if auto-start is currently enabled"""
    app_name = "BreakLoopTimer"
    
    # Check registry (HKEY_CURRENT_USER)
    try:
        reg_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
            0, 
            winreg.KEY_READ
        )
        winreg.QueryValueEx(reg_key, app_name)
        winreg.CloseKey(reg_key)
        return True
    except WindowsError:
        pass
    
    # Check registry (HKEY_LOCAL_MACHINE)
    try:
        reg_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, 
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
            0, 
            winreg.KEY_READ
        )
        winreg.QueryValueEx(reg_key, app_name)
        winreg.CloseKey(reg_key)
        return True
    except WindowsError:
        pass
    
    # Check startup folder
    startup_folder = get_startup_folder_path()
    shortcut_path = os.path.join(startup_folder, "BreakLoopTimer.lnk")
    return os.path.exists(shortcut_path)

def get_dependency_status():
    """Returns information about missing dependencies"""
    missing = []
    
    if not PYWIN32_AVAILABLE:
        missing.append("pywin32")
    
    return {
        "all_available": len(missing) == 0,
        "missing": missing,
        "install_command": "pip install pywin32" if "pywin32" in missing else None
    }