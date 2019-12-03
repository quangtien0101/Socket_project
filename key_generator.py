#!/usr/bin/python3
from cryptography.fernet import Fernet
key = Fernet.generate_key()

file = open('secret_key.key', 'wb')
file.write(key)
file.close()