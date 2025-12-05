# Project: Decrypting RSA with Quantum
# Purpose Details: Provides lightweight RSA key generation and basic RSA encryption/decryption
#                  used by the main application and the Shor-style attack script.
# Course: IST 440W / IST Capstone
# Author: Thomas Koltes, Sierra Matthews, Christine Kwarteng, Brian Myers, George Sun
# Date Developed: 10/13/25
# Last Date Changed: 12/4/25
# Revision: 1.5

import random
from math import gcd


def modinv(a, m):
    """
    Finds the modular inverse of a under modulus m.

    In RSA, we need to compute a number d such that:
        a * d ≡ 1 (mod m)

    In practice, this means "find a number d that, when multiplied by a,
    leaves a remainder of 1 when divided by m."

    This is required because the private key exponent d is defined as
    the modular inverse of e under φ(n).

    Here, we use a very simple brute-force approach because the RSA numbers
    in this educational project are intentionally small.
    """
    for d in range(2, m):
        # Check whether this value of d satisfies the modular inverse equation
        if (a * d) % m == 1:
            return d

    # If no inverse exists (rare with valid RSA parameters), return None.
    return None


def is_prime(n: int) -> bool:
    """
    Checks whether a number is prime.

    Because our project uses very small primes (10–50 range),
    a simple method is sufficient. For larger RSA keys, a much more
    sophisticated primality test would be required.

    The logic:
      - 0 and 1 are not prime
      - Try dividing n by every integer from 2 up to sqrt(n)
      - If none divide evenly, the number is prime
    """

    if n < 2:
        return False

    return all(n % i != 0 for i in range(2, int(n**0.5) + 1))


def generate_rsa_key(primes_lower=10, primes_upper=50):
    """
    Generates a small RSA key pair (n, e, d) for classroom and testing use.

    Steps performed:
      1. Collect all prime numbers in the specified range.
      2. Randomly pick two different primes p and q.
      3. Compute the modulus n = p * q.
      4. Compute Euler's totient φ(n) = (p − 1)(q − 1).
      5. Choose a public exponent e that is coprime with φ(n).
         We start at e = 3 and increase by 2 until gcd(e, φ(n)) = 1.
      6. Compute the private exponent d as the modular inverse of e.

    The result is a tiny RSA key—not secure—but excellent for demonstrating
    the Shor factoring attack and unit-testing.
    """

    # Build a list of primes in the allowed range
    primes = [i for i in range(primes_lower, primes_upper) if is_prime(i)]

    # Randomly pick p and q so long as they are not the same number
    p = random.choice(primes)
    q = random.choice([x for x in primes if x != p])

    # Compute the RSA modulus n
    n = p * q

    # Compute φ(n), needed for selecting e and computing d
    phi_n = (p - 1) * (q - 1)

    # We choose a small starting public exponent (traditional RSA uses 65537),
    # but for educational keys we simply need it to be coprime with φ(n).
    e = 3
    while gcd(e, phi_n) != 1:
        e += 2  # stay with odd numbers, since even e cannot be coprime unless φ(n) is odd

    # Compute the private exponent d
    d = modinv(e, phi_n)

    return n, e, d


def encrypt_message(message: str, n: int, e: int):
    """
    Encrypts a string one character at a time using RSA.

    The logic:
      - Convert each character to its Unicode code using ord(c)
      - Raise it to the power of e modulo n (the RSA_encrypt step)
      - Return the encrypted integers as a list

    This is not how real RSA encrypts full messages (real systems use padding),
    but it works well for demonstrating RSA mechanics with small integers.
    """
    return [pow(ord(c), e, n) for c in message]


def decrypt_message(cipher, n: int, d: int) -> str:
    """
    Decrypts a list of RSA-encrypted integers back into a string.

    Each encrypted integer c is processed as:
        plaintext_char = chr(pow(c, d, n))

    The function rebuilds the original string by concatenating the characters.
    """
    return ''.join(chr(pow(c, d, n)) for c in cipher)
