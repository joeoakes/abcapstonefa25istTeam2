# Project: Decrypting RSA with Quantum
# Purpose Details: Implements a simple Shor-style attack pipeline that tries to factor N using
#                  quantum period finding and then reconstruct the RSA private key.
# Course: IST 440W / IST Capstone
# Author: Thomas Koltes, Sierra Matthews, Christine Kwarteng, Brian Myers, George Sun
# Date Developed: 10/13/25
# Last Date Changed: 12/4/25
# Revision: 1.5

import logging
import random
from math import gcd

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import QFT

from rsa import modinv

# Create a logger specific to the Shor attack code. This integrates with the logging setup
# created in main_app.py and allows us to log useful information about the attack process.
logger = logging.getLogger("shor_app.shor_attack")


def find_period_quantum(a, N, backend):
    """
    Uses a small quantum circuit to estimate the period r of the function f(x) = a^x mod N.

    This function is a simplified placeholder for the period-finding part of Shor's algorithm.
    It builds a toy circuit that:
      - Uses a set of counting qubits
      - Prepares a target register
      - Applies controlled operations that conceptually represent repeated multiplication
      - Runs the inverse Quantum Fourier Transform on the counting register
      - Measures the counting register to estimate the phase, and from that, the period r

    Parameters:
        a (int): The base for the function f(x) = a^x mod N.
        N (int): The integer we are trying to factor.
        backend: A Qiskit AerSimulator backend used to run the circuit.

    Returns:
        int or None:
            The estimated period r if it can be inferred from the measurement,
            or None if the measurement does not give a usable estimate.
    """
    # Number of counting qubits controls the resolution of the phase estimation.
    n_count = 4
    # Number of qubits in the target register based on size of N.
    n_target = int(np.ceil(np.log2(N)))

    # Create a quantum circuit with counting plus target qubits, and classical bits
    # to store the measurements from the counting register.
    qc = QuantumCircuit(n_count + n_target, n_count)

    # Put the counting qubits into a uniform superposition with Hadamard gates.
    qc.h(range(n_count))

    # Initialize the target register to the |1> state. This is a typical starting state
    # for modular exponentiation in Shor's algorithm.
    qc.x(n_count + n_target - 1)

    # Apply controlled unitary operations representing powers of a.
    # In a full implementation this would encode multiplication by a^(2^j) mod N.
    # Here we use identity as a placeholder so we can focus on testing the structure.
    for j in range(n_count):
        power = 2 ** j
        qc.unitary(
            np.identity(2 ** n_target),
            list(range(n_count, n_count + n_target)),
            label=f"a^{power} mod N"
        )

    # Apply the inverse Quantum Fourier Transform to the counting register to extract
    # phase information about the periodic function.
    qc.append(QFT(num_qubits=n_count, inverse=True), range(n_count))

    # Measure the counting qubits into the classical bits.
    qc.measure(range(n_count), range(n_count))

    # Transpile the circuit for the selected backend, then run it with multiple shots
    # so we can obtain a histogram of measurement outcomes.
    qc = transpile(qc, backend)
    job = backend.run(qc, shots=1024)
    counts = job.result().get_counts()

    # Pick the most frequently measured bit string as the best phase estimate.
    measured = max(counts, key=counts.get)

    # Convert the measured bit string into a fraction that approximates the phase.
    phase = int(measured, 2) / (2 ** n_count)
    if phase == 0:
        # If the phase is zero, we cannot compute a meaningful period from it.
        return None

    # Convert the phase into a period estimate. The idea is that phase is approximately
    # equal to k / r, and here we invert that rough relationship.
    r = round(1 / phase)
    return r


def shor_classical(N, retries=5):
    """
    High-level classical wrapper for Shor's algorithm period-finding.

    This function:
      - Handles trivial even factors of N
      - Sets up a GPU or CPU simulator depending on availability
      - Repeatedly chooses random bases a
      - Calls the quantum period-finding routine
      - Uses number theory to recover non-trivial factors from the period r

    Parameters:
        N (int): The integer we are trying to factor.
        retries (int): How many random values of a to try before giving up.

    Returns:
        (factor1, factor2):
            A tuple of integers such that factor1 * factor2 = N, if successful.
            If unsuccessful, returns (None, None).
    """
    # Quick check for even numbers. If N is even, 2 is an immediate factor.
    if N % 2 == 0:
        return 2, None

    # Create a simulator object and inspect available devices.
    sim_check = AerSimulator()
    gpu_ok = 'GPU' in sim_check.available_devices()

    # Inform the user whether the simulator is using GPU or CPU.
    if gpu_ok:
        logger.info("GPU available; using GPU simulator")
        print("GPU available; using GPU simulator")
    else:
        logger.info("GPU not available; using CPU simulator")
        print("GPU not available; using CPU simulator")

    # Configure the simulator to use either a GPU or CPU statevector method.
    backend = AerSimulator(
        method="statevector",
        device="GPU" if gpu_ok else "CPU",
        cuStateVec_enable=True
    )

    # Try multiple random choices of a in the required range.
    for _ in range(retries):
        a = random.randint(2, N - 2)

        # If gcd(a, N) is not 1, we have found a non-trivial factor immediately.
        if gcd(a, N) != 1:
            return gcd(a, N), None

        # Ask the quantum routine to estimate the period r for a^x mod N.
        r = find_period_quantum(a, N, backend)
        if r is None or r % 2 != 0:
            # If r is unusable or odd, we skip this trial and try another a.
            continue

        # Compute x = a^(r/2) mod N which should give us values that help derive factors.
        x = pow(a, r // 2, N)

        # If x is congruent to -1 or 1 modulo N, it does not help produce valid factors.
        if x == N - 1 or x == 1:
            continue

        # Use the standard Shor post-processing steps to compute candidate factors.
        factor1 = gcd(x + 1, N)
        factor2 = gcd(x - 1, N)

        # If the product of the two candidates gives back N, we have successfully factored it.
        if factor1 * factor2 == N:
            return factor1, factor2

    # If we reach here, no good factors were found in the allowed number of retries.
    return None, None


def decrypt_attack(N, e, retries=5):
    """
    Uses a Shor-style factoring attempt to recover the RSA private key d.

    The steps performed are:
      - Call shor_classical to obtain factors p and q of N
      - If only one factor is returned, derive the other as N divided by that factor
      - Compute phi(n) using the discovered factors
      - Compute d as the modular inverse of e with respect to phi(n)

    Parameters:
        N (int): The RSA modulus used in the public key.
        e (int): The public exponent of the RSA key.
        retries (int): How many attempts shor_classical should make when trying to factor N.

    Returns:
        (p, q, d_factored):
            p and q are the recovered prime factors of N,
            d_factored is the private exponent reconstructed from those factors.
    """
    factored_p, factored_q = shor_classical(N, retries=retries)

    # If factored_p is falsy, the attack did not find any non-trivial factors.
    if not factored_p:
        raise RuntimeError(
            "Shor did not return factors; try again because randomness or simulator limits may have prevented success."
        )

    # If only one factor is returned, compute the other factor by dividing N.
    if not factored_q:
        factored_q = N // factored_p

    # Compute phi(n) from the recovered prime factors which is needed to reconstruct d.
    phi_factored = (factored_p - 1) * (factored_q - 1)

    # Recompute the private exponent using the standard RSA formula.
    d_factored = modinv(e, phi_factored)

    return factored_p, factored_q, d_factored
