import base64
import base64
import sys

# Optional: install base58 via `pip install base58`
try:
    import base58
except ImportError:
    base58 = None

# Custom base62 decoder
BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def base62_decode(s):
    result = 0
    for char in s:
        result = result * 62 + BASE62_ALPHABET.index(char)
    return result.to_bytes((result.bit_length() + 7) // 8, 'big')

def try_decode(name, func):
    try:
        decoded = func()
        as_text = decoded.decode('utf-8', errors='replace')
        print(f"\n[{name}]")
        print(f"Raw Bytes: {decoded}")
        print(f"UTF-8 Text: {as_text}")
    except Exception as e:
        pass  # Silently skip

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python decode_basen.py <input_string>")
        sys.exit(1)

    s = sys.argv[1]

    try_decode("Base16 (Hex)", lambda: base64.b16decode(s.upper(), casefold=True))
    try_decode("Base32", lambda: base64.b32decode(s + "=" * ((8 - len(s) % 8) % 8)))
    try_decode("Base64", lambda: base64.b64decode(s + "=" * ((4 - len(s) % 4) % 4)))
    try_decode("Base36 (int)", lambda: int(s.lower(), 36).to_bytes((int(s, 36).bit_length() + 7) // 8, 'big'))
    if base58:
        try_decode("Base58", lambda: base58.b58decode(s))
    try_decode("Base62", lambda: base62_decode(s))
