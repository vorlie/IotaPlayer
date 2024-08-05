import ctypes
import ctypes.wintypes
from winreg import HKEY_CURRENT_USER, QueryValueEx, OpenKey

advapi32 = ctypes.windll.advapi32

def get_colorization_color():
    """Fetch the ColorizationColor from the Windows registry."""
    try:
        key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
        colorization_color = QueryValueEx(key, "ColorizationColor")[0]
        key.Close()
        
        # Convert the color from ABGR to RGB
        red = (colorization_color >> 16) & 0xFF
        green = (colorization_color >> 8) & 0xFF
        blue = colorization_color & 0xFF

        accent_color_hex = '#{:02X}{:02X}{:02X}'.format(red, green, blue)
        return accent_color_hex
    except FileNotFoundError:
        return "#ff50aa"  # Default color if the key is not found

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

    while True:
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

            accent_color_hex = '#{:02X}{:02X}{:02X}'.format(red, green, blue)
            callback(accent_color_hex)
