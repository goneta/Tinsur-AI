
import hashlib
from typing import List
import requests
from io import BytesIO
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

def get_image_hash(image_url: str) -> str:
    """
    Generate a simple perceptual hash for an image.
    If Pillow is not available, falls back to MD5 of the content.
    """
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code != 200:
            return ""
        
        content = response.content
        
        if not HAS_PILLOW:
            # Fallback to simple MD5
            return hashlib.md5(content).hexdigest()
        
        # Simple A-Hash implementation
        img = Image.open(BytesIO(content)).convert('L').resize((8, 8), Image.Resampling.LANCZOS)
        avg = sum(list(img.getdata())) / 64
        hash_val = 0
        for i, val in enumerate(img.getdata()):
            if val > avg:
                hash_val |= (1 << i)
        return hex(hash_val)
    except Exception:
        return ""

def compare_hashes(hash1: str, hash2: str) -> float:
    """
    Compare two hex hashes and return a similarity score (0.0 to 1.0).
    """
    if not hash1 or not hash2:
        return 0.0
    if hash1 == hash2:
        return 1.0
        
    try:
        # Hamming distance for hex strings
        n1 = int(hash1, 16)
        n2 = int(hash2, 16)
        # XOR to find different bits
        diff = n1 ^ n2
        # Count bits set to 1
        distance = bin(diff).count('1')
        # 64 bits total for 8x8 hash
        return 1.0 - (distance / 64.0)
    except ValueError:
        return 1.0 if hash1 == hash2 else 0.0
