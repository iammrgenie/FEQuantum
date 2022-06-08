import pandas as pd
import numpy as np
import hashlib
import main
import os
import timeit

from timeit import default_timer as timer
from main import *
#from main import precomputedValues
#from main import KeyGen
#from main import homomorphicEncrypt
#from main import addCiphers
#from main import decryption


# Hardocded Values (1024 bit security)
p = 141103728801468755249503291901801300339454489134873273269161807133184957725631203791969744406992490029017308434294093310271973777802513443575042969796895750747614660497411432558300476234836462151925376765365205539666438199705555483194413832902302373511490858360959114097755447464088887287145428704637498873563
g = 105861658449903670398842707812938888531601091401355008230876634024010937268870331311638117904636173888707058855182778532622385692236892785716421644114344195029162371175818169381366740838052666046929986716700970629216177653754852315554730008499152818656193522542478412787555437975470969140718764372166206582283
q = 783294875021436409578654247252215361374348380322356315904524998417053527857380
r = 5

print("==================== Welcome to the PLM Demonstration Script ========================== \n")

# Precompute the values for the final decryption
# IMPORTANT: THE LENGTH OF THE LIST "VALUES" NEEDS TO BE BIGGER THAN THE SUM THAT WILL BE DECRYPTED!!
print("Check for Pre-computed values\n")
result = os.path.exists('./precomputed.xlsx')

if result:
    print("Pre-Computed Excel already Exists \n ===================== Uploading Values!! ========================= \n")
    values = precomputedValues(g, p, 500)
    #readCmp = pd.read_excel("precomputed.xlsx")
    #values = readCmp['PreComputed Value'].tolist()
    #print(values)
   
else:
    print("================ Pre-Computed Excel does not exit \n ====================== Generating Computed Values ====================== \n")
    values = precomputedValues(g, p, 100)
    exponents = list(range(len(values)))
    precomp = pd.DataFrame(list(zip(exponents, values)),
                columns =['Exponent', 'PreComputed Value'])
    precomp.to_excel("precomputed.xlsx")



# Read the dataset in form of a pandas dataframe (pandas are cool!)
print("================= Reading Data from Excel file ======================= \n")
df = pd.read_excel('CasesCovid.xlsx')
dates = df['Date'].tolist()
cases = df['Cases'].tolist()
tests = df['Tests'].tolist()
deaths = df['Deaths'].tolist()


# Generate a public,private key pair (pk_i, sk_i) for each entry on the dataset
caseLen = len(deaths)
print("Generating Secret and Public key pairs for ", caseLen, "dates\n")
secretKeys, publickeys = KeyGen(caseLen, p, g)


# Encrypt the numerical values (in our case these are the deaths)
print("Encrypting each numerical value of the dataset with a the generated PK")
start = timer()
for i in range(caseLen):
    deaths[i] = homomorphicEncrypt(deaths[i], publickeys[i], g, p, r)

end = timer()
print("Time taken to homomorphically encrypt ", caseLen, " objects is: ", end - start, " seconds") # Time in seconds, e.g. 5.38091952400282

# Hash the categorical entries of the dataset (just for the shake of it). Normally we would use AES to encrypt these, but why bother now? This is an FE project after all...
for i in range(len(dates)):
    hashedName = hashlib.sha256()
    dates[i] = str.encode(dates[i])
    hashedName.update(dates[i])
    dates[i] = hashedName.digest()
flat_list_deaths = list(np.concatenate(deaths).flat)


# Remove the randomness component (we use the fact that Elgamal has been proven secure under randomness reuse, so we will just add it at the end again)
flat_list_deaths = list(np.concatenate(deaths).flat)
del flat_list_deaths[::2]

# Compute the cipher to be decrypted
print("Add all ciphertexts to create the master ciphertext (C_T)\n")
finalCipher = addCiphers(flat_list_deaths, g, p, r)
#print("C_T: ", finalCipher, "\n")

# Output the encrypted dataset as an excel file
encrypteddf = pd.DataFrame(list(zip(dates, flat_list_deaths)),
               columns =['Dates', 'Deaths'])
encrypteddf.to_excel("encrypted.xlsx")

fnKeys = sum(secretKeys)

# ElGamal Decryption using the functional decryption key
print("ElGamal Decryption with the functional decryption key\n")
start1 = timer()
first_decryption = decryption(finalCipher, fnKeys, p)
end1 = timer()
print("Time taken to decrypt is: ", end1 - start1, " seconds") # Time in seconds, e.g. 5.38091952400282
#print("The first decryption is:", first_decryption)


# Entertain the user
print("=============== All values in the dataset are encrypted =================\n")
question = input("Which function would you like to run?\n")
if question == 'sum':
    if (first_decryption) in values:
        file1 = open("Plaintext result.txt", "w+")
        file1.write("The sum of the deaths is:")
        file1.write(str(values.index(first_decryption)))
        sumData = values.index(first_decryption)
        #print("the functional decryption key is:", fnKeys)
        print("The sum of all deaths in the Dataset is: ", sumData)
    
    #print("You have received the result in plaintext")
    else:
        print("Result out of Scope of our pre-computed values !!! \n")
        quit()
    
elif question == 'average':
    if (first_decryption) in values:
        sumData = values.index(first_decryption)
        fnAverage = sumData / caseLen
        print("The average of all deaths in the Dataset is: ", fnAverage)
    
    #print("You have received the result in plaintext")
    else:
        print("Result out of Scope of our pre-computed values !!! \n")
        quit()
      
else:
    print("We do not support more functions YET!")



# Since the normal decryption returns g^{result}, we need to check our precomputed values to find the value of the result
# Write the result on a txt for a fancier solution
