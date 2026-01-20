import string
import secrets


def generate_strong_password(length: int = 12) -> str:
    if length < 12:
        length = 12
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(special_chars),
    ]
    
    alphabet = string.ascii_letters + string.digits + special_chars
    for _ in range(length - 4):
        password.append(secrets.choice(alphabet))
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


__all__ = (
    'generate_strong_password',
)

