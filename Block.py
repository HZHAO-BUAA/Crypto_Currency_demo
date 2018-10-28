"""Blocks."""
import hashlib
import time


class Transaction:
    """Transaction class"""
    def __init__(self, senderPublicKey, senderSignature, receiverWallet, amount):
        self.senderPublicKey = senderPublicKey
        self.receiver = receiverWallet
        self.senderSignature = senderSignature
        self.amount = amount
        self.inputTxs = []
        self.timestamp=str(time.time())

    def __eq__(self, comptx):
        """Compare another transaction to the current transaction object."""

        txin1 = False
        txin2 = False
        txin3 = False
        txin4 = False
        txin5 = False
        txin6 = False
        if self.amount == comptx.amount:
            txin1 = True
        if self.inputTxs == comptx.inputTxs:
            txin2 = True
        if self.receiver == comptx.receiver:
            txin3 = True
        if self.senderPublicKey == comptx.senderPublicKey:
            txin4 = True
        if self.senderSignature == comptx.senderSignature:
            txin5 = True
        if self.timestamp==comptx.timestamp:
            txin6 = True
        return txin1 and txin2 and txin3 and txin4 and txin5 and txin6

    def toString(self):
        """Give a string version of a block object."""
        outString = str(self.senderPublicKey.y)
        outString += str(self.senderPublicKey.g)
        outString += str(self.senderPublicKey.p)
        outString += str(self.senderPublicKey.q)
        outString += str(self.amount)
        outString += str(self.senderSignature[0])
        outString += str(self.senderSignature[1])
        outString += str(self.receiver)
        return outString


class Block:
    """Block class."""

    def __init__(self, transactions, nonce=0):
        self.transactions = transactions
        self.hash = ""
        self.previousBlockHash = ""
        self.nonce = nonce
        self.header = self.previousBlockHash + str(self.nonce)

    def getHeaderHash(self):
        """Return the hash of the block header."""
        self.header = self.previousBlockHash + str(self.nonce)
        for Tx in self.transactions:
            self.header += Tx.toString()
        hash = hashlib.new('ripemd160')
        hash.update(self.header.encode())
        self.hash = hash.hexdigest()
        return self.hash
