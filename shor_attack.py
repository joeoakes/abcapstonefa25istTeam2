# shor_attack.py
import logging
import random
from math import gcd

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import QFT

from rsa import modinv

# Use our dedicated app logger hierarchy: "shor_app.shor_attack"
logger = logging.getLogger("shor_app.shor_attack")

def find_period_quantum(a, N, backend):
    """
    Quantum period-finding for a^x mod N using a toy circuit.
    """
    # Number of counting qubits
    n_count = 4  # Adjust for resolution
    n_target = int(np.ceil(np.log2(N)))

    qc = QuantumCircuit(n_count + n_target, n_count)

    # Apply Hadamard to counting qubits
    qc.h(range(n_count))

    # Initialize target register to |1>
    qc.x(n_count + n_target - 1)

    # Apply controlled-U^(2^j) operations – placeholder unitary
    for j in range(n_count):
        power = 2 ** j
        qc.unitary(
            np.identity(2 ** n_target),
            list(range(n_count, n_count + n_target)),
            label=f"a^{power} mod N"
        )

    # Apply inverse QFT
    qc.append(QFT(num_qubits=n_count, inverse=True), range(n_count))

    # Measure counting register
    qc.measure(range(n_count), range(n_count))

    qc = transpile(qc, backend)
    job = backend.run(qc, shots=1024)
    counts = job.result().get_counts()

    measured = max(counts, key=counts.get)
    phase = int(measured, 2) / (2 ** n_count)
    if phase == 0:
        return None

    # Estimate r
    r = round(1 / phase)
    return r

def shor_classical(N, retries=5):
    """
    Shor-style classical wrapper around quantum period finding.
    Returns (factor1, factor2) or (None, None).
    """
    if N % 2 == 0:
        return 2, None

    # Try GPU; fall back to CPU if not available
    sim_check = AerSimulator()
    gpu_ok = 'GPU' in sim_check.available_devices()

    if gpu_ok:
        logger.info("GPU available; using GPU simulator")
        print("GPU available; using GPU simulator")
    else:
        logger.info("GPU not available; using CPU simulator")
        print("GPU not available; using CPU simulator")

    backend = AerSimulator(
        method="statevector",
        device="GPU" if gpu_ok else "CPU",
        cuStateVec_enable=True
    )

    # random 'a' values
    for _ in range(retries):
        a = random.randint(2, N - 2)
        if gcd(a, N) != 1:
            return gcd(a, N), None

        r = find_period_quantum(a, N, backend)
        if r is None or r % 2 != 0:
            continue

        x = pow(a, r // 2, N)
        if x == N - 1 or x == 1:
            continue

        factor1 = gcd(x + 1, N)
        factor2 = gcd(x - 1, N)

        if factor1 * factor2 == N:
            return factor1, factor2

    return None, None

def decrypt_attack(N, e, retries=5):
    """
    Use Shor-style factoring to recover d from (N, e).
    Returns (p, q, d_factored).
    """
    factored_p, factored_q = shor_classical(N, retries=retries)

    if not factored_p:
        raise RuntimeError(
            "Shor did not return factors; try again (randomness or simulator limits)."
        )

    if not factored_q:
        factored_q = N // factored_p

    phi_factored = (factored_p - 1) * (factored_q - 1)
    d_factored = modinv(e, phi_factored)
    return factored_p, factored_q, d_factored

