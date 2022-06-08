import random
import pandas as pd
import numpy as np
import hashlib
import math
import xlrd
from random import randint

def functionalKey(list):
    functionKey = sum(list)
    return functionKey


def addCiphers(array, g, p, r):
    finalCipher = []
    first_component = pow(g, r, p)
    finalCipher.append(first_component)
    second_component = np.prod(array)
    finalCipher.append(second_component)
    return finalCipher

def homomorphicEncrypt(msg, pk, g, p, r):
    cipher = []
    #r = random.randint(2,45)
    #r = 5
    c1 = (g**r) % p
    cipher.append(c1)
    c2 = ((pk**r)*(g**msg)) % p
    cipher.append(c2)
    return cipher


def decryption(cipher, privateKey, p):
    #m = (cipher[0]**(p-privateKey-1) % p)* cipher[1] % p
    m = pow(cipher[0], p - privateKey - 1, p)*cipher[1]%p
    return m

def precomputedValues(g, p, size):
    values = []
    for i in range(size):
        values.append((g**i)%p)

    return values

def KeyGen(size, p, g):
        secretkeys = []
        publickeys = []
        for j in range(size):
                s = randint(2, p-2)
                v = pow(g,s,p)
                secretkeys.append(s)
                publickeys.append(v)
        return secretkeys, publickeys



