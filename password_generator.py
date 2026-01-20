"""
Secure Password Generation Module
Generates cryptographically strong random passwords using the secrets module.
"""

import secrets
import string


def generate_password(length: int = 16, 
                     use_uppercase: bool = True,
                     use_lowercase: bool = True,
                     use_digits: bool = True,
                     use_symbols: bool = True) -> str:
    """
    Generate a cryptographically secure random password.
    
    Args:
        length: Password length (12-64 characters)
        use_uppercase: Include uppercase letters (A-Z)
        use_lowercase: Include lowercase letters (a-z)
        use_digits: Include digits (0-9)
        use_symbols: Include special characters
        
    Returns:
        Generated password string
        
    Raises:
        ValueError: If no character types selected or invalid length
    """
    # Validate inputs
    if length < 12 or length > 64:
        raise ValueError("Password length must be between 12 and 64 characters")
    
    if not any([use_uppercase, use_lowercase, use_digits, use_symbols]):
        raise ValueError("At least one character type must be selected")
    
    # Build character pool
    character_pool = ""
    required_chars = []
    
    if use_uppercase:
        character_pool += string.ascii_uppercase
        required_chars.append(secrets.choice(string.ascii_uppercase))
    
    if use_lowercase:
        character_pool += string.ascii_lowercase
        required_chars.append(secrets.choice(string.ascii_lowercase))
    
    if use_digits:
        character_pool += string.digits
        required_chars.append(secrets.choice(string.digits))
    
    if use_symbols:
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        character_pool += symbols
        required_chars.append(secrets.choice(symbols))
    
    # Generate password ensuring at least one char from each selected pool
    remaining_length = length - len(required_chars)
    
    # Generate random characters for the rest
    random_chars = [secrets.choice(character_pool) for _ in range(remaining_length)]
    
    # Combine and shuffle
    password_chars = required_chars + random_chars
    
    # Cryptographically secure shuffle
    # Fisher-Yates shuffle using secrets.randbelow
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]
    
    return ''.join(password_chars)


def estimate_password_strength(password: str) -> tuple[str, float]:
    """
    Estimate password strength.
    
    Args:
        password: The password to evaluate
        
    Returns:
        Tuple of (strength_label, entropy_bits)
    """
    import math
    
    # Calculate character pool size
    pool_size = 0
    if any(c.isupper() for c in password):
        pool_size += 26
    if any(c.islower() for c in password):
        pool_size += 26
    if any(c.isdigit() for c in password):
        pool_size += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        pool_size += 21
    
    # Calculate entropy in bits
    entropy = len(password) * math.log2(pool_size) if pool_size > 0 else 0
    
    # Classify strength
    if entropy < 50:
        strength = "Weak"
    elif entropy < 70:
        strength = "Fair"
    elif entropy < 90:
        strength = "Strong"
    else:
        strength = "Very Strong"
    
    return strength, entropy


if __name__ == "__main__":
    # Test the generator
    print("Testing Password Generator:")
    print("-" * 50)
    
    for length in [12, 16, 24, 32]:
        pwd = generate_password(length)
        strength, entropy = estimate_password_strength(pwd)
        print(f"Length {length}: {pwd}")
        print(f"  Strength: {strength} ({entropy:.1f} bits of entropy)\n")
