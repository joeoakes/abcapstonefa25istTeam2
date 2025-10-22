import qiskit
from sympy import primerange
import math


p = 61
q = 53
e = 17

n = p * q
print(n)

phi = (p-1) * (q-1)
print(phi)

print(math.gcd(e,phi))

d = pow(e,-1,phi)
print(d)

print("Please input your message here: -> ",end=" ")
message = input()

print("\nENCRYPT")
asciiMessage = [ord(ch) for ch in message]
print(asciiMessage)
encryptedMessage = [pow(ch, e, n) for ch in asciiMessage]
print(encryptedMessage)

print("\nDECRYPT")
decryptedAsciiMessage = [pow(ch, d, n) for ch in encryptedMessage]
print(decryptedAsciiMessage)
decryptedMessage = ''.join([chr(ch) for ch in decryptedAsciiMessage])
print("\nMESSAGE: " + decryptedMessage)

 