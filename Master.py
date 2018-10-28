"""Master."""
import Server
from Block import Transaction
from Block import Block
import pickle
from bottle import request
import codecs
import json
import random
import CryptoLib


class Master:
    """Master class"""

    def __init__(self, port):
        firstBlock = Block(transactions=[], nonce=random.randint(0, 10000000000000))
        firstBlock.getHeaderHash()
        self.blockchain = [firstBlock]
        self.unspentTxs = []
        self.firstBlockHash = firstBlock.getHeaderHash()
        self.server = Server.Server(port, self)
        self.listen_blockchain(self.server)
        self.listen_unspent_tx(self.server)
        self.listen_blocks(self.server)
        self.listen_difficulty(self.server)
        self.difficulty = 2
        self.numFullBlock = 0
        self.numEmptyBlock = 0
        self.server.startServer()

    def listen_blockchain(self, server):
        server._app.route("/Blockchain", method="GET", callback=self.send_block_chain_to_relay)

    def listen_difficulty(self, server):
        server._app.route("/DifficultyRequest", method="GET", callback=self.send_difficulty_to_relay)

    def listen_unspent_tx(self, server):
        server._app.route("/UnspentTx", method="GET", callback=self.send_unspent_tx_to_wallet)

    def listen_blocks(self, server):
        server._app.route("/BlockToMaster", method="POST", callback=self.accept_block)

    def send_block_chain_to_relay(self):
        return pickle.dumps(self.blockchain)

    def send_unspent_tx_to_wallet(self):
        return pickle.dumps(self.unspentTxs)

    def send_difficulty_to_relay(self):
        return str(self.difficulty)

    def validate_initial_tx(self, tx):
        """Validate an initial tx (a tx that is a reward for the miner) by its signature."""
        return CryptoLib.validateInitialTransaction(tx)

    def validate_regular_tx(self, tx):
        """Validate a regular tx by its signature and the liquidity of its sender."""
        sig = tx.senderSignature
        header = tx.receiver.encode() + str(tx.amount).encode()
        if tx.senderPublicKey.verify(header, sig):
            return True
        else:
            return False

    def validate_pow(self, block):
        """Validate the PoW of a block by looking at the hash."""
        compareStr='0'
        for idx in range(self.difficulty - 1):
            compareStr += '0'
        return block.getHeaderHash()[:self.difficulty] == compareStr and block.previousBlockHash == self.blockchain[-1].hash

    def validate_new_block(self, block):
        """
        Check PoW and hash.
        when validation a new block, the Master
        1) check initial transaction (signature only)
        2)  a) check regular transaction (signature)
            b) check regular transaction (enough liquidity)
        3) check proof of work of new block
        """
        initialTx = block.transactions[0]
        if len(block.transactions) > 1:
            mainTx = block.transactions[1]
            validity_mainTx = self.validate_regular_tx(mainTx)
        else:
            validity_mainTx = True

        return self.validate_initial_tx(initialTx) and validity_mainTx and self.validate_pow(block)

    def update_tx_inputs(self, block, change, coveringTxs):
        """Update a new tx inputTxs and create a new change transaction."""
        mainTx = block.transactions[1]
        changeTx = Transaction(mainTx.senderPublicKey, "???", CryptoLib.getAddressFromPublicKey(mainTx.senderPublicKey.y), change)
        block.transactions.append(changeTx)
        block.inputTransactions = coveringTxs

    def change_unspent_txs(self, block):
        """Change the pool of unspent txs based on a new accepted block."""
        bonusTx=block.transactions[0]
        self.unspentTxs.append(bonusTx)

        if len(block.transactions) > 1:
            mainTx = block.transactions[1]
            changeTx = block.transactions[2]
            inputTxs = block.inputTransactions
            for tx in inputTxs:
                self.unspentTxs.remove(tx)
            self.unspentTxs.append(mainTx)
            self.unspentTxs.append(changeTx)

    def validate_main_tx_funds(self, block):
        """
        Validate if the main tx of a block can be afforded.
        1) Validate if the sender of the main tx has enough fund to cover it.
        2) Update the master unspent tx pool and the block input txs.
        """
        if len(block.transactions) > 1:
            bonusTx = block.transactions[0]
            mainTx = block.transactions[1]
            coveringTxs = []
            totalAmount = 0
            enoughFunds = False
            bonusOk =  False
            if bonusTx.amount==10:
                bonusOk=True
            for tx in self.unspentTxs:
                if tx.receiver == CryptoLib.getAddressFromPublicKey(mainTx.senderPublicKey.y):
                        coveringTxs.append(tx)
                        totalAmount += tx.amount
                    
                if totalAmount >= mainTx.amount:
                    enoughFunds = True
                    break
            if enoughFunds and bonusOk:
                change = totalAmount - mainTx.amount
                self.update_tx_inputs(block, change, coveringTxs)
                self.change_unspent_txs(block)
                return True
            else:
                return False
        else:
            bonusTx = block.transactions[0]
            if bonusTx.amount==10:
                self.change_unspent_txs(block)
                return True
            else:
                return False

    def update_difficulty(self):
        """Update the current difficulty"""
        if self.numEmptyBlock + self.numFullBlock >= 16:
            if self.numFullBlock <= 1:
                self.difficulty += 1
            if self.numEmptyBlock == 0:
                if self.difficulty > 1:
                    self.difficulty -= 1
            self.numEmptyBlock = 0
            self.numFullBlock = 0
            return self.difficulty
        else:
            return self.difficulty

    def accept_block(self):
        """
        Accept and add a new block to the blockchain, or not.
        1) Check if the new block is valid, cryptographically
        2) Check if the new block is valid, financially (the main transaction can be afforded)
        """
        blockJSON = request.json
        blockRaw = json.loads(blockJSON)
        newBlock = pickle.loads(codecs.decode(blockRaw.encode(), "base64"))
        acceptBlockCrypto = self.validate_new_block(newBlock)
        acceptBlockLiquidity = self.validate_main_tx_funds(newBlock)
        if acceptBlockCrypto and acceptBlockLiquidity:
            self.blockchain.append(newBlock)
            if len(newBlock.transactions) > 1:
                self.numFullBlock+=1
            else:
                self.numEmptyBlock+=1
            self.difficulty = self.update_difficulty()
            return "Accepted"
        else:
            return "Declined"
