from math import gcd
import random


# generating e value by guessing prime number
def generate_e(phi_n):
    e = 2
    le = []
    while e < phi_n:
        m = gcd(e, phi_n)
        if m == 1:
            le.append(e)
        e = e + 1
    e = random.choice(le)
    return e


# generating d value by using e
def generate_d(e, phi_n):
    d = 1
    r = (d*e)%phi_n
    while r != 1:
        d = d+1
        r = (d*e)%phi_n
    return d


# message encryption by using public key of sender
def encryption(message, key):
    words = message.split(" ")
    encryption = ""
    words_encrypted = []
    for i in words:
        word = encryption_word(i, key)
        words_encrypted.append(word)
    for j in words_encrypted:
        encryption = encryption + str(j) + " "
    return encryption


# encrypt words in message and call it in above func
def encryption_word(word, key):
    values_encryptions = []
    values = []
    n, e = key
    encryption = ""
    for i in word:
        x = ord(i)
        values.append(x)
    for j in values:
        c = (j ** e) % n
        values_encryptions.append(c)
    for k in values_encryptions:
        encryption = encryption + str(k) + " "
    return encryption


# message decryption by using receivers private key
def decryption(message, key):
    numbers = message.split("  ")
    original = ""
    decryption = []
    for i in numbers:
        pal = decryption_number(i, key)
        decryption.append(pal)
    for j in decryption:
        original = original + str(j) + " "
    return original


# decrypt cipher text(number) into PT
def decryption_number(number, key):
    list_numbers_decryptions = []
    list_numbers = []
    n, d = key
    decryption = ""
    numbers = number.split(" ")
    for i in numbers:
        if(i != ''):
            x = int(i)
            list_numbers.append(x)
    for j in list_numbers:
        m = (j ** d) % n
        list_numbers_decryptions.append(m)
    for k in list_numbers_decryptions:
        letter = chr(k)
        decryption = decryption + str(letter)
    return decryption


# generate keys by rsa algo higher the p and q more secure
def generate_keys():
    p = 239
    q = 103
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = generate_e(phi_n)
    d = generate_d(e, phi_n)
    return (n, e), (n, d)