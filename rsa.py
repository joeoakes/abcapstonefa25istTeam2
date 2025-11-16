# rsa.py
import random
from math import gcd

def modinv(a, m):
    """
    Compute d such that a * d ≡ 1 (mod m), or return None if it doesn't exist.
    """
    for d in range(2, m):
        if (a * d) % m == 1:
            return d
    return None

def is_prime(n: int) -> bool:
    """
    Simple primality test for small n.
    """
    if n < 2:
        return False
    return all(n % i != 0 for i in range(2, int(n**0.5) + 1))

def generate_rsa_key(primes_lower=10, primes_upper=50):
    """
    Generate a small RSA key (n, e, d) for demo/testing purposes.
    """
    primes = [i for i in range(primes_lower, primes_upper) if is_prime(i)]
    p = random.choice(primes)
    q = random.choice([x for x in primes if x != p])

    n = p * q
    phi_n = (p - 1) * (q - 1)

    # Choose e
    e = 3
    while gcd(e, phi_n) != 1:
        e += 2

    d = modinv(e, phi_n)
    return n, e, d

def encrypt_message(message: str, n: int, e: int):
    """
    Encrypt a string message using RSA (per-character).
    """
    return [pow(ord(c), e, n) for c in message]

def decrypt_message(cipher, n: int, d: int) -> str:
    """
    Decrypt a list of integers back into a string.
    """
    return ''.join(chr(pow(c, d, n)) for c in cipher)

