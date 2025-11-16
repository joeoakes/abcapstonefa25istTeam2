# main_app.py
import time
import logging

from rsa import generate_rsa_key, encrypt_message, decrypt_message
from shor_attack import decrypt_attack


def setup_logging():
    """
    Configure a dedicated app logger "shor_app" that writes only our logs
    to shor_attack.log. External libraries (qiskit, stevedore, etc.)
    will not use this handler.
    """
    # Root logger: keep it quiet and handler-free so libraries don't spam us
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Our application logger
    app_logger = logging.getLogger("shor_app")
    app_logger.setLevel(logging.DEBUG)
    app_logger.propagate = False  # don't bubble up to root

    # Clear old handlers (if re-running in a notebook, etc.)
    if app_logger.hasHandlers():
        app_logger.handlers.clear()

    # File handler for our app logs
    file_handler = logging.FileHandler("shor_attack.log", mode="a")
    file_handler.setLevel(logging.INFO)

    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    app_logger.addHandler(file_handler)

    # Optional: keep qiskit itself quieter in case it ever configures handlers
    logging.getLogger("qiskit").setLevel(logging.WARNING)
    logging.getLogger("stevedore").setLevel(logging.WARNING)


def run_app(message: str, retries: int = 5):
    """
    Run RSA, encrypt/decrypt, then perform Shor-style attack and measure time.
    """
    # Use our app logger hierarchy for main
    logger = logging.getLogger("shor_app.main")
    start_time = time.time()

    # RSA key generation
    n, e, d = generate_rsa_key()
    c = encrypt_message(message, n, e)
    decrypted = decrypt_message(c, n, d)

    logger.info(f"Message: {message}")
    print(f"Message: {message}")

    logger.info(f"Encrypted: {c}")
    print(f"Encrypted: {c}")

    logger.info(f"Decrypted: {decrypted}")
    print(f"Decrypted: {decrypted}")

    # Shor attack
    factored_p, factored_q, d_factored = decrypt_attack(n, e, retries=retries)

    logger.info(f"Factored p = {factored_p}, q = {factored_q}")
    print(f"Factored p = {factored_p}, q = {factored_q}")

    logger.info(f"Recovered d = {d_factored}")
    print(f"Recovered d = {d_factored}")

    decrypted_attack = decrypt_message(c, n, d_factored)
    logger.info(f"Decrypted (via attack): {decrypted_attack}")
    print(f"Decrypted (via attack): {decrypted_attack}")

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Elapsed time: {elapsed:.4f} seconds")


if __name__ == "__main__":
    setup_logging()
    run_app("Very good how are you today sir yes haha", retries=50)

