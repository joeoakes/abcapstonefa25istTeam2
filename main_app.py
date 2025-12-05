# Project: Decrypting RSA with Quantum
# Purpose Details: Command-line app that generates RSA keys, encrypts a message, and then attempts
#                  to recover the private key using a Shor-style quantum factoring attack.
# Course: IST 440W / IST Capstone
# Author: Thomas Koltes (update team info as needed)
# Date Developed: 10/13/25
# Last Date Changed: 12/4/25
# Revision: 1.5

import time
import logging

from rsa import generate_rsa_key, encrypt_message, decrypt_message
from shor_attack import decrypt_attack


def setup_logging():
    """
    Creates and configures a dedicated logger for our application so that only the logs we
    intentionally create show up in the output file. This helps avoid a large amount of noise
    from external libraries such as qiskit. The log file stores INFO-level messages so we can
    track what happened during the program run.
    """

    # Get the main/root logger used by Python programs. Many libraries send their messages here.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # keep external library messages quieter

    # If the program was run before in the same environment, clear old handlers so log output
    # does not get duplicated.
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Create a specific logger for our application code only.
    app_logger = logging.getLogger("shor_app")
    app_logger.setLevel(logging.DEBUG)   # allow detailed logging inside our program
    app_logger.propagate = False         # do not pass messages upward to the root logger

    # Clear old file handlers if they exist. This commonly happens in notebook environments.
    if app_logger.hasHandlers():
        app_logger.handlers.clear()

    # Create the file handler that writes to shor_attack.log. Append mode allows log history.
    file_handler = logging.FileHandler("shor_attack.log", mode="a")
    file_handler.setLevel(logging.INFO)

    # Define how each log line should look inside the file.
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Attach this handler to our app logger so everything we log will be captured.
    app_logger.addHandler(file_handler)

    # Reduce noise from qiskit and stevedore even if they add their own handlers later.
    logging.getLogger("qiskit").setLevel(logging.WARNING)
    logging.getLogger("stevedore").setLevel(logging.WARNING)


def run_app(message: str, retries: int = 5):
    """
    Handles the full process of generating RSA keys, encrypting and decrypting the user's
    message, attempting a Shor-style attack to factor n, and showing how long the entire
    process takes. This function also prints and logs important information for debugging.
    """

    # Get a logger specific to this function's work.
    logger = logging.getLogger("shor_app.main")

    # Capture when the program starts running so we can compute runtime later.
    start_time = time.time()

    # Generate an RSA keypair. This gives us the modulus n, public exponent e,
    # and private exponent d. These values are returned from rsa.py.
    n, e, d = generate_rsa_key()

    # Encrypt the user's message using the public key (n, e). The result is an integer
    # ciphertext that represents the encrypted form of the string.
    c = encrypt_message(message, n, e)

    # Decrypt the ciphertext using the legitimate private key (n, d) to confirm that
    # standard RSA encryption/decryption is functioning properly.
    decrypted = decrypt_message(c, n, d)

    # Print and log the original user message.
    logger.info(f"Message: {message}")
    print(f"Message: {message}")

    # Print and log the encrypted version of the message.
    logger.info(f"Encrypted: {c}")
    print(f"Encrypted: {c}")

    # Print and log the decrypted version using the real private key.
    logger.info(f"Decrypted: {decrypted}")
    print(f"Decrypted: {decrypted}")

    # Run the Shor-style attack. This attempts to factor n. If successful, the attack
    # returns the discovered p and q values, along with the reconstructed private key d.
    factored_p, factored_q, d_factored = decrypt_attack(n, e, retries=retries)

    # Log and print the results of factoring n.
    logger.info(f"Factored p = {factored_p}, q = {factored_q}")
    print(f"Factored p = {factored_p}, q = {factored_q}")

    # Log and print the private key that was reconstructed by the attack.
    logger.info(f"Recovered d = {d_factored}")
    print(f"Recovered d = {d_factored}")

    # Attempt to decrypt the ciphertext using the private key recovered through the attack.
    # If the attack succeeded, this text should match the original user message.
    decrypted_attack = decrypt_message(c, n, d_factored)

    logger.info(f"Decrypted (via attack): {decrypted_attack}")
    print(f"Decrypted (via attack): {decrypted_attack}")

    # Compute how long the entire process took and print it for the user.
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Elapsed time: {elapsed:.4f} seconds")


if __name__ == "__main__":
    # Set up logging before doing anything else so that all activity is recorded properly.
    setup_logging()

    # Ask the user for a message. This will be turned into an integer and encrypted.
    user_message = input("Enter a message to encrypt and attack-decrypt: ")

    # Ask the user how many times the attack should retry factoring n.
    # We loop here until they either enter a valid integer or press ENTER to use 50.
    while True:
        retries_input = input("Enter number of retries for Shor attack (default 50): ").strip()

        if retries_input == "":
            retries = 50
            break

        if retries_input.isdigit():
            retries = int(retries_input)
            break

        print("Invalid input. Please enter a valid integer.")

    # Run the program using the user inputs.
    run_app(user_message, retries=retries)
