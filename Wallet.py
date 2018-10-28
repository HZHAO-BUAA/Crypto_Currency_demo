"""Module containing the class for the wallets"""
from Crypto.PublicKey import DSA
from Crypto.Random import random
import codecs
import json
import pickle
import requests
import Block
import CryptoLib


class Wallet:
    """Class for the users' wallets."""

    def __init__(self, relayPort, password):
        """Init."""
        myDSAKeys = DSA.generate(1024)
        self.myDSAPublicKey = myDSAKeys.publickey()
        self.encryptedDSAKey = CryptoLib.encryptWalletDSAKey(password, myDSAKeys)
        self.address = CryptoLib.getAddressFromPublicKey(self.myDSAPublicKey.y)
        self.unspentTxs = []
        self.relayPort = relayPort
        self.relayIP = "http://localhost:" + str(self.relayPort)
        self.BlockChain = []

    def determine_wallet_money(self):
        """Determine how much money the user associated with the wallet has."""
        self.unspentTxs=self.update_unspent_txs()
        moneyAvailable = 0
        for tx in self.unspentTxs:
            if tx.receiver == self.address:
                moneyAvailable = moneyAvailable + tx.amount
        return moneyAvailable

    def create_transaction(self, receiverAddress, amount, password):
        """Create a new transaction."""
        allDSAKey = CryptoLib.restoreWalletDSAKey(password, self.encryptedDSAKey)
        if isinstance(allDSAKey, str):
            return "Password Error"
        else:
            k = random.StrongRandom().randint(1, allDSAKey.q - 1)
            senderSignature = allDSAKey.sign(receiverAddress.encode() + str(amount).encode(), k)
            newTransaction = Block.Transaction(senderPublicKey=self.myDSAPublicKey, senderSignature=senderSignature,
                                               receiverWallet=receiverAddress, amount=amount)
            return newTransaction

    def spend_money(self, receiverAddress, amount, password):
        """Create and send a tx of a certain amount to a receiver, if the wallet has enough money."""
        balance = self.determine_wallet_money()
        if amount < balance:
            newTransaction = self.create_transaction(receiverAddress, amount, password)
            self.send_tx_to_relay(newTransaction)
        else:
            print("You are poor")

    def get_address(self):
        """Return the wallet address."""
        return self.address

    def update_unspent_txs(self):
        """Update the list of unspent txs used to calculate the money availabe."""
        req = requests.get(self.relayIP + "/UnspentTx")
        unspentTxs = pickle.loads(req.content)
        self.unspentTxs = unspentTxs
        return unspentTxs

    def send_tx_to_relay(self, tx):
        """Send new transaction to the linked relay."""
        pickledBlock = codecs.encode(pickle.dumps(tx), "base64").decode()
        jsonForm=json.dumps(pickledBlock)
        requests.post(self.relayIP + "/TxToRelay", json=jsonForm)

    def req_balance(self, publicKey):
        """Send a request to the linked relay to know the wallet's balance."""
        pickledKey = codecs.encode(pickle.dumps(publicKey), "base64").decode()
        jsonForm = json.dumps(pickledKey)
        req = requests.post(self.relayIP + "/BalanceRequest", json=jsonForm)
        return int(req.content)

    def request_block_chain(self):
        """Get the whole blockchain from the relay."""
        req = requests.get(self.relayIP + "/Blockchain")
        blockChain = pickle.loads(req.content)
        self.BlockChain = blockChain
        return blockChain

    def miner_transaction(self, amount, password):
        """Create an intial transaction that is a reward for a miner, in case the miner is linked with the wallet."""
        initialTransaction = self.create_transaction(self.address, amount, password)
        return initialTransaction
