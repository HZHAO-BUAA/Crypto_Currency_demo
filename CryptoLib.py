"""Utilities module containing useful cryptographic modules"""
import hashlib
import AES_128
from Crypto.PublicKey import DSA


def getAddressFromPublicKey(realPublicKey):
    """Return the address from a public key."""
    h = hashlib.sha256()
    h.update(str(realPublicKey).encode())
    address = h.hexdigest()
    return address


def validateInitialTransaction(transaction):
    """
    Validate an initial transaction: a transaction that is a reward for a miner
    and that serves to create money in the cryptocurrency economy.
    """
    sig = transaction.senderSignature
    h = transaction.receiver.encode() + str(transaction.amount).encode()
    if transaction.senderPublicKey.verify(h, sig):
        return True
    else:
        return False


def encryptWalletDSAKey(AESkey, myDSAKey):
    """
    Encrypt private keys using AES-128.
    """
    cipher = AES_128.AES_CRY(AESkey[:16])
    encrypted_y = cipher.encrypt(str(myDSAKey.y))
    encrypted_g = cipher.encrypt(str(myDSAKey.g))
    encrypted_p = cipher.encrypt(str(myDSAKey.p))
    encrypted_q = cipher.encrypt(str(myDSAKey.q))
    encrypted_x = cipher.encrypt(str(myDSAKey.x))
    encryptedtuple = (encrypted_y,encrypted_g,encrypted_p,encrypted_q,encrypted_x)
    return encryptedtuple


def restoreWalletDSAKey(AESKey, encryptedtuple):
    """
        Decrypt private keys using AES-128
    """
    cipher = AES_128.AES_CRY(AESKey[:16])
    try:
        decrypted_y = cipher.decrypt(encryptedtuple[0])
        decrypted_g = cipher.decrypt(encryptedtuple[1])
        decrypted_p = cipher.decrypt(encryptedtuple[2])
        decrypted_q = cipher.decrypt(encryptedtuple[3])
        decrypted_x = cipher.decrypt(encryptedtuple[4])
        decryptedtuple = (int(decrypted_y), int(decrypted_g), int(decrypted_p), int(decrypted_q), int(decrypted_x))
        allDSAKey = DSA.construct(decryptedtuple)
    except:
        allDSAKey = "Password Error"
    return allDSAKey
