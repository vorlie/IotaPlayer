import platform

try:
    import darkdetect
except ImportError:
    darkdetect = None

def get_colorization_colors():
    """Fetch the accent color. Uses Windows registry if available, else defaults."""
    if platform.system() == "Windows":
        try:
            from winreg import HKEY_CURRENT_USER, QueryValueEx, OpenKey
            key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
            colorization_color = QueryValueEx(key, "ColorizationColor")[0]
            key.Close()
            red = (colorization_color >> 16) & 0xFF
            green = (colorization_color >> 8) & 0xFF
            blue = colorization_color & 0xFF
            accent = '#{:02X}{:02X}{:02X}'.format(red, green, blue)
        except Exception:
            accent = "#ff50aa"
    else:
        accent = "#ff50aa"
    return accent

def get_system_theme():
    """Detect current system theme (light or dark)."""
    try:
        if darkdetect:
            theme = darkdetect.theme().lower()
            if theme in ['light', 'dark']:
                return theme
        # Fallback: try to detect on Windows
        if platform.system() == "Windows":
            import ctypes
            return 'dark' if ctypes.windll.dwmapi.DwmGetWindowAttribute(0, 9) else 'light'
    except Exception:
        pass
    return 'dark'