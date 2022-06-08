import pandas as pd
import numpy as np
import hashlib
import main

from main import *


# Hardocded Values (1024 bit security)
p = 141103728801468755249503291901801300339454489134873273269161807133184957725631203791969744406992490029017308434294093310271973777802513443575042969796895750747614660497411432558300476234836462151925376765365205539666438199705555483194413832902302373511490858360959114097755447464088887287145428704637498873563
g = 105861658449903670398842707812938888531601091401355008230876634024010937268870331311638117904636173888707058855182778532622385692236892785716421644114344195029162371175818169381366740838052666046929986716700970629216177653754852315554730008499152818656193522542478412787555437975470969140718764372166206582283
q = 783294875021436409578654247252215361374348380322356315904524998417053527857380
r = 5

# Precompute the values for the final decryption
# IMPORTANT: THE LENGTH OF THE LIST "VALUES" NEEDS TO BE BIGGER THAN THE SUM THAT WILL BE DECRYPTED!!
values = precomputedValues(g, p, 200)
exponents = list(range(len(values)))
precomp = pd.DataFrame(list(zip(exponents, values)),
               columns =['Exponent', 'PreComputed Value'])
precomp.to_excel("precomputed.xlsx")



# Read the dataset in form of a pandas dataframe (pandas are cool!)
df = pd.read_excel('Data.xlsx')
names = df['Students'].tolist()
grades = df['Grades'].tolist()



# Generate a public,private key pair (pk_i, sk_i) for each entry on the dataset
secretKeys, publickeys = KeyGen(len(grades), p, g)


# Encrypt the numerical values (in our case these are the grades)
for i in range(len(grades)):
    grades[i] = homomorphicEncrypt(grades[i], publickeys[i], g, p, r)


# Remove the randomness component (we use the fact that Elgamal has been proven secure under randomness reuse, so we will just add it at the end again)
flat_list_grades = list(np.concatenate(grades).flat)
del flat_list_grades[::2]

# Compute the cipher to be decrypted
finalCipher = addCiphers(flat_list_grades, g, p, r)

# Hash the categorical entries of the dataset (just for the shake of it). Normally we would use AES to encrypt these, but why bother now? This is an FE project after all...
for i in range(len(names)):
    hashedName = hashlib.sha256()
    names[i] = str.encode(names[i])
    hashedName.update(names[i])
    names[i] = hashedName.digest()
flat_list_grades = list(np.concatenate(grades).flat)

# Output the encrypted dataset as an excel file
encrypteddf = pd.DataFrame(list(zip(names, flat_list_grades)),
               columns =['Students', 'Grades'])
encrypteddf.to_excel("encrypted.xlsx")

# Entertain the user
print("Your files are encrypted")
question = input("Which function would you like to run? ")
if question == 'sum':
    print("the functional decryption key is:", sum(secretKeys))
else:
    print("We do not support more functions YET!")

# ElGamal Decryption using the functional decryption key
first_decryption = decryption(finalCipher, sum(secretKeys), p)
print("The first decryption is:", first_decryption)

# Since the normal decryption returns g^{result}, we need to check our precomputed values to find the value of the result
# Write the result on a txt for a fancier solution
for i in values[0:3]:
    print(i)

if (first_decryption) in values:
    file1 = open("Plaintext result.txt", "w+")
    file1.write("The sum of the grades is:")
    file1.write(str(values.index(first_decryption)))
    print("You have received the result in plaintext")
else:
    print("You cant expect us to actually solve the DLP, right?")
