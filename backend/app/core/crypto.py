import base64
import os
from typing import Optional

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..core.config import settings


class CredentialVault:
    def __init__(self, master_key_b64: Optional[str] = None):
        key_str = master_key_b64 or settings.ENCRYPTION_MASTER_KEY
        key_bytes = base64.b64decode(key_str)
        if len(key_bytes) != 32:
            raise ValueError(f"Master key must be exactly 32 bytes for AES-256-GCM, got {len(key_bytes)}")
        self.aesgcm = AESGCM(key_bytes)

    def encrypt(self, plaintext: str) -> str:
        nonce = os.urandom(12)  # 96-bit standard nonce
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")

    def decrypt(self, encrypted_token: str) -> str:
        raw = base64.urlsafe_b64decode(encrypted_token.encode("utf-8"))
        if len(raw) < 28:  # 12-byte nonce + 16-byte GCM auth tag
            raise InvalidTag("Ciphertext payload is truncated or invalid.")
        nonce = raw[:12]
        ciphertext = raw[12:]
        decrypted_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_bytes.decode("utf-8")
