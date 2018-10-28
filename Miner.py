"""Miners."""
import Block
import requests
import pickle
import json
import codecs
import random
import CryptoLib
from Wallet import Wallet


class Miner:
    """Class for the miners."""

    def __init__(self, minerID, relayPort, WalletPassword):
        """Init."""
        self.ID = minerID
        self.myWalletPassword=WalletPassword
        self.myWallet = Wallet(relayPort,WalletPassword)
        self.relayPort = relayPort
        self.relayIP = "http://localhost:" + str(self.relayPort)
        self.blockTemplate = ''
        self.newBlock = ''
        self.TempTx = ''
        self.tryAgainWithSameBlock = 0
        self.BlockChain = ''
        self.unspentTxs = []
        self.mainTransaction=[]


    def send_block(self, block):
        """Send block to the linked relay."""
        pickledBlock = codecs.encode(pickle.dumps(block), "base64").decode()
        jsonForm = json.dumps(pickledBlock)
        req = requests.post(self.relayIP + "/BlockToMaster", json=jsonForm)
        if req.content.decode() == "Accepted":
            self.tryAgainWithSameBlock = 0
        else:
            self.tryAgainWithSameBlock = 1

    def request_tx(self):
        """Get a transaction waiting to be validated from the relay."""
        req = requests.get(self.relayIP + "/TxRequest")
        tx = pickle.loads(req.content)
        return tx

    def request_block_chain(self):
        """Get the blockchain from the linked relay."""
        req = requests.get(self.relayIP + "/Blockchain")
        blockChain = pickle.loads(req.content)
        self.BlockChain = blockChain
        return blockChain

    def get_wallet_balance(self):
        """Determine the balance of the linked wallet"""
        walletBalance= self.myWallet.determine_wallet_money()
        return walletBalance

    def get_initial_transaction(self):
        """Get an inital tx from the linked wallet, as a reward for the mining."""
        initialTransaction = self.myWallet.miner_transaction(10, password=self.myWalletPassword)
        return initialTransaction

    def get_main_transaction(self):
        """Get a regular transaction (not a reward and not a change) from the linked relay."""
        req = requests.get(self.relayIP + "/TxRequest")
        mainTransaction = pickle.loads(req.content)
        return mainTransaction

    def validate_regular_tx(self, tx):
        """Validate a regular tx by its signature."""
        if isinstance(self.mainTransaction,str):
            return True
        else:
            sig = tx.senderSignature
            header = tx.receiver.encode() + str(tx.amount).encode()
            if tx.senderPublicKey.verify(header, sig):
                return True
            else:
                return False


    def spend_money_from_wallet(self, receiverAddress, Amount):
        """Spend wallet's money"""
        self.myWallet.spend_money(receiverAddress, Amount, self.myWalletPassword)

    def get_difficulty_from_master(self):
        """Get the current difficulty imposed by the master, through the linked relay."""
        req = requests.get(self.relayIP + "/DifficultyRequest")
        return int(req.content)

    def do_pow(self):
        """Do the proof of work algorithm."""
        wholeChain = self.request_block_chain()
        lastBlock = wholeChain[-1]
        initialTransaction = self.get_initial_transaction()
        self.mainTransaction = self.get_main_transaction()
        while self.validate_regular_tx(self.mainTransaction)==False:
            self.mainTransaction = self.get_main_transaction()
        miningDifficulty = self.get_difficulty_from_master()
        if CryptoLib.validateInitialTransaction(initialTransaction):
            NewBlock = Block.Block(transactions=[])
            NewBlock.previousBlockHash = lastBlock.hash
            compareStr = '0'
            NewBlock.nonce = 0
            for idx in range(miningDifficulty-1):
                compareStr += '0'
            if isinstance(self.mainTransaction,str):
                NewBlock.transactions = [initialTransaction]
            else:
                NewBlock.transactions = [initialTransaction, self.mainTransaction]
            while NewBlock.getHeaderHash()[:miningDifficulty] != compareStr:
                NewBlock.nonce +=1
            self.send_block(NewBlock)
        else:
            print("Initial transaction set from Wallet error")

    def is_tx_pool_empty(self):
        """check if the tx pool of the linked relay is empty."""
        req = requests.get(self.relayIP + "/TxPoolEmpty")
        return req.content.decode() == 'True'
