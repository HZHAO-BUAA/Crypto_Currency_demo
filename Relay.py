"""Relays"""
import Server
import requests
import pickle
from bottle import request
import json
import codecs


class Relay:
    """Class for the relays."""

    def __init__(self, masterPort, port):
        """Init."""
        self.masterPort = masterPort
        self.masterIP = "http://localhost:" + str(self.masterPort)
        self.blockChain = None
        self.receivedBlock = None
        self.txPool = []
        server = Server.Server(port, self)
        self.listenBlockToMaster(server)
        self.listenBlockchain(server)
        self.listenTxFromWallet(server)
        self.listenTxRequest(server)
        self.listenUnspentTx(server)
        self.listenBalanceRequest(server)
        self.listenDifficultyRequest(server)
        self.listenTxPoolEmpty(server)
        server.startServer()

    def listenBlockchain(self, server):
        """Listen for getting the blockchain."""
        server._app.route("/Blockchain", method="GET", callback=self.getBlockchain)

    def listenDifficultyRequest(self,server):
        server._app.route("/DifficultyRequest", method="GET",
                          callback=self.getDifficulty)

    def listenUnspentTx(self,server):
        server._app.route("/UnspentTx", method="GET",
                          callback=self.getUnspentTx)

    def listenGetInitialTransaction(self, server):
        """Listen for getting the initial transaction."""
        server._app.route("/InitialTransaction", method="GET", callback=self.getInitialTransactionFromWallet)

    def listenBlockToMaster(self, server):
        """Listen for transfering a block to the master."""
        server._app.route("/BlockToMaster", method="POST", callback=self.transferBlock)

    def listenTxFromWallet(self, server):
        """Listen for adding a transaction to the pool of txs."""
        server._app.route("/TxToRelay", method="POST", callback=self.addTxToPool)

    def listenTxRequest(self, server):
        """Listen for ???."""
        server._app.route("/TxRequest", method="GET", callback=self.returnTx)

    def listenBalanceRequest(self, server):
        """Listen for a request on the balance."""
        server._app.route("/BalanceRequest", method="POST", callback=self.getBalance)

    def getBlockchain(self):
        req = requests.get(self.masterIP + "/Blockchain")
        self.blockChain = pickle.loads(req.content)
        return req.content

    def getUnspentTx(self):
        req = requests.get(self.masterIP + "/UnspentTx")
        self.blockChain = pickle.loads(req.content)
        return req.content

    def transferBlock(self):
        req = requests.post(self.masterIP + "/BlockToMaster", json=request.json)
        return req.content

    def addTxToPool(self):
        txJSON = request.json
        txRaw = json.loads(txJSON)
        newTx = pickle.loads(codecs.decode(txRaw.encode(), "base64"))
        self.txPool.append(newTx)

    def returnTx(self):
        if len(self.txPool)==0:
            txToWallet='Empty'
            pickledTx = pickle.dumps(txToWallet)
        else:
            txToWallet = self.txPool.pop(0)
            pickledTx = pickle.dumps(txToWallet)
        return pickledTx

    def getBalance(self):
        keyJSON = request.json
        keyRaw = json.loads(keyJSON)
        key = pickle.loads(codecs.decode(keyRaw.encode(), "base64"))
        answer = self.calcBalance(key)
        return answer

    def getDifficulty(self):
        req = requests.get(self.masterIP + "/DifficultyRequest")
        return req.content

    def listenTxPoolEmpty(self,server):
        """Listen for the question 'Is the transaction pool empty?' """
        server._app.route("/TxPoolEmpty", method="GET", callback=self.isTxPoolEmpty)
        
    def isTxPoolEmpty(self):
        if len(self.txPool)==0:
            isEmpty='True'
        else:
            isEmpty='False'
        return isEmpty
