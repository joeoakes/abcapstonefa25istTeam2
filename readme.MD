IST 440W Capstone Team 2
Group Members: Thomas Koltes, Christine Kwarteng, George Sun, Brian Myers, Sierra Matthews
Our goal is to use the simulated Quantum X computer available to us to try and "break" RSA by factoring the largest integers possible using Shor's Algorithm primarily for factoring.



quantum_project/
│
├── quantum_project/
│   ├── __init__.py                # Unified initialization logic
│   ├── circuits/
│   │   ├── __init__.py
│   │   ├── h_gate_simulation.py   # Builds and simulates 6-qubit H-gate circuit
│   │   ├── noise_model.py         # Adds bit-flip noise to qubits
│   │   ├── benchmarking.py        # Measures circuit performance over time
│   └── factoring/
│       ├── __init__.py
│       ├── classical_factor.py    # Implements a step-by-step factorization algorithm
│
├── pyproject.toml
├── poetry.lock
└── README.md
