#!/usr/bin/python3
#simple substitution cipher

import sys
import random

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
key = 'LFWOAYUISVKMNXPBDCRJTQEGHZ'

# mode is either encrypt or decrypt (depends on the provided arguments)

def main():
    if len(sys.argv) != 3:
        sys.exit("<Error> Invalid arguments number while encrypt/decrypt")
        
    mode = sys.argv[1]
    message = sys.argv[2]
    print(mode)
    print(message)
    
    if mode == '--encrypt':
        translated_message = encrypt(key, message)
    elif mode == '--decrypt':
        translated_message = decrypt(key, message)
    else:
        sys.exit('<Error> Invalid mode!')
    print(translated_message)
    return translated_message

def checkValidKey(key):
    keyList = list(key)
    lettersList = list(LETTERS)
    keyList.sort()
    lettersList.sort()
    if keyList != lettersList:
        sys.exit("Error in the key set!")

def encrypt(key, message):
    return translated_message(key, message, 'encrypt')

def decrypt(key, message):
    return translated_message(key, message, 'decrypt')

def translated_message(key, message, mode):
    translated = ''
    first_Set = LETTERS
    second_Set = key
    if mode == 'decrypt':
        first_Set, second_Set = second_Set, first_Set

    for symbol in message:
        if symbol.upper() in first_Set:
            index = first_Set.find(symbol.upper())
            if symbol.isupper():
                translated += second_Set[index].upper()
            else:
                translated += second_Set[index].lower()
        else:
            translated += symbol
    
    return translated

if __name__ == "__main__":
    main()