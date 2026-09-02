import base64

import pytest
from app.core.crypto import CredentialVault
from cryptography.exceptions import InvalidTag


def test_encryption_decryption_lifecycle():
    vault = CredentialVault()
    secret = "SecretPass123!"

    encrypted = vault.encrypt(secret)

    # Assert ciphertext is not equal to plaintext and contains no cleartext substrings
    assert encrypted != secret
    assert secret not in encrypted

    # Decrypt and assert exact match
    decrypted = vault.decrypt(encrypted)
    assert decrypted == secret


def test_ciphertext_tampering_detection():
    vault = CredentialVault()
    secret = "SecurePortalKey@2026"

    encrypted = vault.encrypt(secret)
    raw_bytes = bytearray(base64.urlsafe_b64decode(encrypted.encode("utf-8")))

    # Mutate a byte in the ciphertext portion (after the 12-byte nonce)
    raw_bytes[15] ^= 0xFF
    tampered_token = base64.urlsafe_b64encode(bytes(raw_bytes)).decode("utf-8")

    # Attempt decryption; must raise InvalidTag
    with pytest.raises(InvalidTag):
        vault.decrypt(tampered_token)
