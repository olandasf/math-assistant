"""
Kriptografinės utilitos - API raktų šifravimas/dešifravimas.
Naudoja Fernet simetrinį šifravimą su PBKDF2 raktu iš SECRET_KEY.
"""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from loguru import logger


def _derive_key(secret_key: str) -> bytes:
    """Išveda Fernet raktą iš SECRET_KEY naudojant SHA-256."""
    key_bytes = hashlib.sha256(secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


def get_fernet(secret_key: str) -> Fernet:
    """Gauti Fernet instanciją su išvestu raktu."""
    return Fernet(_derive_key(secret_key))


def encrypt_value(value: str, secret_key: str) -> str:
    """
    Šifruoja reikšmę su Fernet.
    Grąžina base64-encoded šifruotą tekstą su 'enc:' prefiksu.
    """
    if not value:
        return value
    # Jei jau šifruota, nešifruoti pakartotinai
    if value.startswith("enc:"):
        return value
    f = get_fernet(secret_key)
    encrypted = f.encrypt(value.encode())
    return f"enc:{encrypted.decode()}"


def decrypt_value(value: str, secret_key: str) -> str:
    """
    Dešifruoja reikšmę su Fernet.
    Jei reikšmė nešifruota (be 'enc:' prefikso), grąžina kaip yra.
    """
    if not value:
        return value
    # Jei nešifruota (legacy plaintext), grąžinti kaip yra
    if not value.startswith("enc:"):
        return value
    try:
        f = get_fernet(secret_key)
        encrypted_data = value[4:]  # Pašalinti 'enc:' prefiksą
        decrypted = f.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except InvalidToken:
        logger.error("Nepavyko dešifruoti reikšmės — netinkamas raktas arba duomenys")
        return ""
    except Exception as e:
        logger.error(f"Dešifravimo klaida: {e}")
        return ""
