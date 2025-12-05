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

    The goal is to find a number d such that:
        a * d ≡ 1 (mod m)

    This is important in RSA because the private key exponent d must be the modular
    inverse of the public exponent e relative to phi(n). This version uses a simple
    brute force loop because the numbers used in this project are intentionally small.
    """
    for d in range(2, m):
        # Check whether this value of d satisfies the modular inverse equation
        if (a * d) % m == 1:
            return d

    # If no modular inverse is found, return None
    return None


def is_prime(n: int) -> bool:
    """
    Returns True if n is a prime number.

    The function handles small prime checking by testing divisibility from 2 up to
    the square root of n. If none of these values divide n evenly, the number is prime.
    This approach is more than enough for the small integers used in this assignment.
    """
    if n < 2:
        return False

    return all(n % i != 0 for i in range(2, int(n**0.5) + 1))


def generate_rsa_key(primes_lower=10, primes_upper=50):
    """
    Creates a small RSA key (n, e, d) suitable for educational demonstrations.

    Main steps performed:
      - Build a list of primes between the specified lower and upper bounds
      - Randomly select p and q from that list
      - Compute n which becomes the modulus for both the public and private keys
      - Compute phi(n) which is used to choose e and compute d
      - Choose e starting from 3 and move upward until it is coprime with phi(n)
      - Compute d by finding the modular inverse of e

    These RSA values are intentionally small so that the Shor attack script can factor n
    and recover the private key during testing.
    """

    # List all primes within the specified range
    primes = [i for i in range(primes_lower, primes_upper) if is_prime(i)]

    # Choose p and q as two different primes from the list
    p = random.choice(primes)
    q = random.choice([x for x in primes if x != p])

    # Compute the modulus n used for RSA encryption and decryption
    n = p * q

    # Compute Euler's totient value which determines valid choices for e
    phi_n = (p - 1) * (q - 1)

    # Begin with a small odd exponent e and increase until it is coprime with phi(n)
    e = 3
    while gcd(e, phi_n) != 1:
        e += 2

    # Compute the private exponent d
    d = modinv(e, phi_n)

    return n, e, d


def encrypt_message(message: str, n: int, e: int):
    """
    Encrypts a string message one character at a time using RSA.

    For each character:
      - Convert it to an integer using ord(c)
      - Perform RSA encryption using pow(value, e, n)
      - Store the encrypted integer in the output list

    This simple approach is good for demonstration purposes because the focus is on
    understanding how RSA transforms numeric values.
    """
    return [pow(ord(c), e, n) for c in message]


def decrypt_message(cipher, n: int, d: int) -> str:
    """
    Decrypts a list of RSA encrypted integers back into a readable string.

    For each encrypted integer:
      - Apply RSA decryption using pow(c, d, n)
      - Convert the resulting integer back into a character with chr()
      - Append it to the output string
    """
    return ''.join(chr(pow(c, d, n)) for c in cipher)
