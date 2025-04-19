# utils/__init__.py
from matplotlib.colors import to_rgb, to_hex
import numpy as np
import ctypes
import ctypes.wintypes
import darkdetect
from time import sleep
from winreg import HKEY_CURRENT_USER, QueryValueEx, OpenKey

advapi32 = ctypes.windll.advapi32

colorValues = {
    "dark": 0.9,
    "light": 0.7,
    "dark_alt": 0.2,
    "light_alt": 0.1
}

def hex_to_rgba(hex_color, alpha):
    """Convert a HEX color to RGBA format with the given alpha."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def darken_color(hex_color, factor):
    """Generate a darker variation of the given HEX color."""
    rgb = to_rgb(hex_color)
    rgb_array = np.array(rgb)
    darkened_rgb = np.clip(rgb_array * (1 - factor), 0, 1)
    darkened_hex = to_hex(darkened_rgb)
    return darkened_hex

def lighten_color(hex_color, factor):
    """Generate a lighter variation of the given HEX color."""
    rgb = to_rgb(hex_color)
    rgb_array = np.array(rgb)
    white_rgb = np.array([1.0, 1.0, 1.0])
    lightened_rgb = np.clip(rgb_array + factor * (white_rgb - rgb_array), 0, 1)
    lightened_hex = to_hex(lightened_rgb)
    return lightened_hex

def get_colorization_colors():
    """Fetch the ColorizationColor from the Windows registry and return both normal and darker colors."""
    try:
        key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
        colorization_color = QueryValueEx(key, "ColorizationColor")[0]
        key.Close()
        
        red = (colorization_color >> 16) & 0xFF
        green = (colorization_color >> 8) & 0xFF
        blue = colorization_color & 0xFF

        accent = '#{:02X}{:02X}{:02X}'.format(red, green, blue)
        
        dark = darken_color(accent, colorValues['dark'])
        dark_alt = darken_color(accent, colorValues['dark_alt'])
        light = lighten_color(accent, colorValues['light'])
        light_alt = lighten_color(accent, colorValues['light_alt'])
        
        return accent, dark, dark_alt, light, light_alt
    except Exception:
        accent = "#ff50aa"
        dark = darken_color(accent, colorValues['dark'])
        dark_alt = darken_color(accent, colorValues['dark_alt'])
        light = lighten_color(accent, colorValues['light'])
        light_alt = lighten_color(accent, colorValues['light_alt'])

        return accent, dark, dark_alt, light, light_alt

def get_system_theme():
    """Detect current system theme (light or dark)."""
    try:
        theme = darkdetect.theme().lower()
        if theme not in ['light', 'dark']:
            # Handle unexpected values
            theme = 'dark' if ctypes.windll.dwmapi.DwmGetWindowAttribute(0, 9) else 'light'
        return theme
    except Exception as e:
        print(e)
        return 'dark'

def listener(callback):
    """Listen for changes to the ColorizationColor registry key and trigger the callback."""
    hKey = ctypes.wintypes.HKEY()
    advapi32.RegOpenKeyExA(
        ctypes.wintypes.HKEY(0x80000001),  # HKEY_CURRENT_USER
        ctypes.wintypes.LPCSTR(b'Software\\Microsoft\\Windows\\DWM'),
        ctypes.wintypes.DWORD(),
        ctypes.wintypes.DWORD(0x00020019),  # KEY_READ
        ctypes.byref(hKey),
    )

    dwSize = ctypes.wintypes.DWORD(ctypes.sizeof(ctypes.wintypes.DWORD))
    queryValueLast = ctypes.wintypes.DWORD()
    queryValue = ctypes.wintypes.DWORD()
    advapi32.RegQueryValueExA(
        hKey,
        ctypes.wintypes.LPCSTR(b'ColorizationColor'),
        ctypes.wintypes.LPDWORD(),
        ctypes.wintypes.LPDWORD(),
        ctypes.cast(ctypes.byref(queryValueLast), ctypes.wintypes.LPBYTE),
        ctypes.byref(dwSize),
    )

    current_theme = get_system_theme()

    while True:
        # Always check for theme updates
        new_theme = get_system_theme()
        if new_theme != current_theme:
            current_theme = new_theme
            normal, dark, dark_alt, light, light_alt = get_colorization_colors()
            callback(normal, dark, dark_alt, light, light_alt)

        # Check for registry changes
        advapi32.RegNotifyChangeKeyValue(
            hKey,
            ctypes.wintypes.BOOL(True),
            ctypes.wintypes.DWORD(0x00000004),  # REG_NOTIFY_CHANGE_LAST_SET
            ctypes.wintypes.HANDLE(None),
            ctypes.wintypes.BOOL(False),
        )
        
        advapi32.RegQueryValueExA(
            hKey,
            ctypes.wintypes.LPCSTR(b'ColorizationColor'),
            ctypes.wintypes.LPDWORD(),
            ctypes.wintypes.LPDWORD(),
            ctypes.cast(ctypes.byref(queryValue), ctypes.wintypes.LPBYTE),
            ctypes.byref(dwSize),
        )

        if queryValueLast.value != queryValue.value:
            queryValueLast.value = queryValue.value

            # Convert the color from ABGR to RGB
            red = (queryValue.value >> 16) & 0xFF
            green = (queryValue.value >> 8) & 0xFF
            blue = queryValue.value & 0xFF

            accent = '#{:02X}{:02X}{:02X}'.format(red, green, blue)
            
            # Apply darken and lighten functions with appropriate factors
            dark = darken_color(accent, colorValues['dark'])
            dark_alt = darken_color(accent, colorValues['dark_alt'])
            light = lighten_color(accent, colorValues['light'])
            light_alt = lighten_color(accent, colorValues['light_alt'])

            # Call the callback with the system theme and colors
            callback(accent, dark, dark_alt, light, light_alt)
        sleep(5)