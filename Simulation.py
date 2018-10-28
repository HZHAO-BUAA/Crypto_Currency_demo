"""Module containing the simulations of the cryptocurrency functioning"""
import random
import string
import Wallet,Miner,Master,Relay
import sys, os
import threading
from time import sleep
import requests
import csv
import re





csvData=["Not modified"]

def working_ports(portsToTest):
    """ 
    Checks that the port in the provided list responds correctly.
    Returns list of all working ports
    """
    for relayPort in portsToTest:
        try:
            req = requests.get("http://localhost:"+str(relayPort))
           
            if(int(req.content.decode())!=relayPort):
                portsToTest.remove(relayPort)
        except:
            portsToTest.remove(relayPort)
            print("Relay "+str(relayPort)+ " not working.")
    return portsToTest


def thread_relays(numRelays,startPort,masterPort):
    """
    Threads a requested number of relays connected to the selected masterPort.
    The function iterates over successive relay port number starting at port number startPort.
    """
    port=startPort
    validatedRelays=0
    listRelays=[]
    while(validatedRelays!=numRelays):
        for i in range(numRelays-validatedRelays):
            try:
                threading.Thread(target=Relay.Relay, args=(masterPort, port,)).start()
                listRelays+=[port]
            except:
                print("Error: unable to start thread " + str(i))
            port+=1
        sleep(0.3)
        listRelays=working_ports(listRelays)
        validatedRelays=len(listRelays)
    return listRelays


def thread_master(startPort):
    """
    Threads the master port.
    Tries port startPort first. 
    If unsuccessful adds 100 to the port number and tries again until it connects successfully.
    """
    masterPort=startPort
    validatedRelays=0
    listRelays=[]
    while(validatedRelays!=1):
        
        try:
            threading.Thread(target=Master.Master, args=(masterPort,)).start()
            listRelays+=[masterPort]
        except:
            print("Error: unable to start master thread ")
        masterPort+=100
        sleep(0.3)
        listRelays=working_ports(listRelays)
        validatedRelays=len(listRelays)
    return listRelays[0]





def create_wallets(relayPorts,numWalletsPerRelay):
    """
    Create wallets for ports in relayPorts list.
    For an index of the relayPorts list, the function creates n wallets, n being the value of the numWalletsPerRelay list for this index.
    """

    passwordList=[]
    walletList=[]
    print("Creating of wallets:")
    for portIndex,numWallet in enumerate(numWalletsPerRelay): 
        for _ in range(numWallet):
            print("Wallet "+str(len(walletList))+" created.")
            password=''.join(random.choice(string.ascii_letters+string.digits) for _ in range(16))
            passwordList.append(password)            
            walletList.append(Wallet.Wallet(relayPorts[portIndex],password))
    
    print("")
    return walletList,passwordList



def create_miners(relayPorts,numMinersPerRelay):
    """
    Creates miners for ports in relayPorts list.
    For an index of the relayPorts list, the function creates n Miners, n being the value of the numMinersPerRelay list for this index.
    """
    MinerList=[]
    print("Creating miners:")
    for portIndex,numWallet in enumerate(numMinersPerRelay): 
        for _ in range(numWallet):  
            print("Miner "+str(len(MinerList))+" created.")
            password=''.join(random.choice(string.ascii_letters+string.digits) for _ in range(16))
            MinerList.append(Miner.Miner(portIndex,relayPorts[portIndex],password))
    print("")
    
    return MinerList



def miners_per_relay(numRelays,numMiners):
    """
    Returns the list of how many miners should be assigned to each port.
    Each port has at least one miner, the rest of them is assigned randomly.
    """
    listWallet=[1]*numRelays
    
    for _ in range(numMiners-numRelays):
        randPos=random.randint(0,numRelays-1)
        listWallet[randPos]+=1
    return listWallet



def wallets_per_relay(numRelays,numExtraWallets):
    """
    Returns the list of how many wallets should be assigned to each port.
    Each port has a randomly assigned number of wallets with the total equal to numExtraWallets.
    """
    listWallet=[0]*numRelays
    
    for _ in range(numExtraWallets):
        randPos=random.randint(0,numRelays-1)
        listWallet[randPos]+=1
    return listWallet


def miner_same_port(wallet,minerList):
    """
    Returns one miner on the same port as the requested wallet.
    """
    for miner in minerList:
        if(wallet.relayPort == miner.relayPort):
            return miner


def miner_send_tx(miner,wallet,indexMiner,indexWallet,relayPorts):
    """
    Sends a random amount of available money to a wallet address.
    If the miner doesn't have money it mines a block then sends the money.
    """
    global csvData
    
    receiverAddress=wallet.get_address()
    availableMoney=miner.get_wallet_balance()

    fractionMoneySent=random.random()
    if(availableMoney==0):
        miner.do_pow()
        print("Miner "+str(indexMiner)+" mined a block.")
        csvData.append(["MB: m"+str(indexMiner),10,"R"+str(relayPorts.index(miner.relayPort))])
        #moneySent= int(fractionMoneySent * 10)
    else:
        moneySent=int(fractionMoneySent * availableMoney)
        miner.spend_money_from_wallet(receiverAddress, moneySent)
        print("Miner "+str(indexMiner)+" sent "+str(moneySent)+" coins to wallet "+ str(indexWallet) +".")
        csvData.append(["Tx: m"+str(indexMiner)+"->w"+str(indexWallet),moneySent,"R"+str(relayPorts.index(miner.relayPort))])
        
    
    
    


def wallet_send_tx(senderWallet,receiverWallet,password,senderIndex,receiverIndex,relayPorts):
    """
    Sends a random amount of available money from wallet if there is money available
    """
    receiverAddress=receiverWallet.get_address()
    availableMoney=senderWallet.determine_wallet_money()
    if(availableMoney!=0):
        moneySent=int(random.random()*availableMoney)
        senderWallet.spend_money(receiverAddress,moneySent,password)
        print("Wallet "+str(senderIndex)+" sent "+str(moneySent)+" coins to wallet "+str(receiverIndex)+".")
        csvData.append(["Tx: w"+str(senderIndex)+"->w"+str(receiverIndex),moneySent,"R"+str(relayPorts.index(senderWallet.relayPort))])



def mine_blocks(minerList,relayPorts):
    """
    Random miner is chosen and mines a block.
    The action is repeated indefinitely. 
    """
    



    minerIndex=random.randint(0,len(minerList)-1)
    miner=minerList[minerIndex]
    miner.do_pow()
    print("Miner "+str(minerIndex)+" mined a block.")
    csvData.append(["MB: m"+str(minerIndex),10,"R"+str(relayPorts.index(miner.relayPort))])
        
        

            


def miner_send_txs(minerList,walletList,relayPorts):
    """
    Miner and wallet are chosen randomly and the miner sends money to this wallet.
    The action is repeated indefinitely. 
    """

    minerIndex=random.randint(0,len(minerList)-1)
    walletIndex=random.randint(0,len(walletList)-1)
    miner=minerList[minerIndex]
    wallet=walletList[walletIndex]
    miner_send_tx(miner,wallet,minerIndex,walletIndex,relayPorts)


def wallet_send_txs(minerList,walletList,passwordList,relayPorts):
    """
    Two wallets are chosen randomly, one sends money to the other.
    The action is repeated indefinitely. 
    """
    
    indexSender=random.randint(0,len(walletList)-1)
    sender=walletList[indexSender]
    passwordSender=passwordList[indexSender]
    indexReceiver=random.randint(0,len(walletList)-1)
    receiver=walletList[indexReceiver]
    wallet_send_tx(sender,receiver,passwordSender,indexSender,indexReceiver,relayPorts)

def do_action(minerList,walletList,passwordList,relayPorts):
    """
    Do randomly one of the following actions:
    - Send a transaction from a miner to a wallet(1 chance out of 5)
    - Send a transaction from a wallet to a wallet(1 chance out of 5)
    - mine a block (3 chances out of 5)
    """
    randInt=random.randint(0,5)
    if(randInt==0):
        miner_send_txs(minerList, walletList, relayPorts)
        
    elif (randInt==1):
        wallet_send_txs(minerList,walletList,passwordList,relayPorts)
    else:
        mine_blocks(minerList,relayPorts)
    
    
def initiate_csvData(relayPorts,walletList,minerList,numMinersPerRelay,numWalletsPerRelay):
    """
    Setup csvData to match the wanted format
    """
    global csvData
    csvData=([["Relay setup"]])
    relayList=[ "Relay "+str(i) for i in range(len(relayPorts))]
    csvData.append([""]+relayList)
    
    relayMinerSetup=['']*len(relayPorts)
    minerCount=0
    for i,numMiners in enumerate(numMinersPerRelay):
        for j in range(numMiners):
            strToSave=str(minerCount)
            if j!=numMiners-1:
                strToSave=strToSave+","
            relayMinerSetup[i]+=strToSave
            minerCount+=1
    csvData.append(["Miners"]+relayMinerSetup)
    
    relayWalletSetup=['']*len(relayPorts)
    walletCount=0
    for i,numWallets in enumerate(numWalletsPerRelay):
        for j in range(numWallets):
            strToSave=str(walletCount)
            if j!=numWallets-1:
                strToSave=strToSave+","
            relayWalletSetup[i]+=strToSave
            walletCount+=1
    csvData.append(["Wallets"]+relayWalletSetup)
    

    
    csvData.append(["Balances"])
    
    maxWallMiner=max(len(walletList),len(minerList))
    minersNums=[ str(i) for i in range(maxWallMiner)]
    csvData.append([""]+minersNums)
    csvData.append(["Expected Wallet Balance"]+[0]*len(walletList))
    csvData.append(["Measured Wallet Balance"]+[0]*len(walletList))
    csvData.append(["Expected Miner Balance"]+[0]*len(minerList))
    csvData.append(["Measured Miner Balance"]+[0]*len(minerList))
    csvData.append([""])
    csvData.append(["Pending transactions"])
    
    for relayInd in range(len(relayPorts)):
        csvData.append(["R"+str(relayInd)])
    csvData.append([""])
    
    csvData.append(["Transaction history"])
    csvData.append(["Transaction","Amount","Relay"])
    
def write_csv_file(data,location):
    """
    Print data to a defined location.
    """
    with open(location, "w") as f:
        writer = csv.writer(f)
        writer.writerows(data)
    f.close()

def analysecsvData(relayPorts,walletList,minerList,walletBalance,minerBalance):
    """
    Analyse the transaction history and construct the pending transactions and balnces from it.
    """
    
    global csvData
    minerBal=[0]*len(minerList)
    walletBal=[0]*len(walletList)
    relayPending=[["Empty"]]*len(relayPorts)
    
    for i in range(15+len(relayPorts),len(csvData)):
        instr=csvData[i][0]
        amount=csvData[i][1]
        relay=list(map(int, re.findall(r'\d+', csvData[i][2])))[0]
        if(instr[:3]=="MB:"):
            
            miner=list(map(int, re.findall(r'\d+', instr)))[0]
            minerBal[miner]+=amount
            
            if relayPending[relay][0]!="Empty":
                
                relInstr=relayPending[relay].pop(0)
                sender=list(map(int, re.findall(r'\d+', relInstr)))[0]
                receiver=list(map(int, re.findall(r'\d+', relInstr)))[1]
                amount=list(map(int, re.findall(r'\d+', relInstr)))[2]
                if(relInstr[0]=='m' and minerBal[sender]-amount>=0 ):
                    minerBal[sender]-=amount
                    walletBal[receiver]+=amount
                elif(relInstr[0]=='w'  and walletBal[sender]-amount>=0):
                    walletBal[sender]-=amount
                    walletBal[receiver]+=amount
                    
        elif(instr[:3]=="Tx:"):
            listTransactions=list(relayPending[relay])
            listTransactions.insert(len(relayPending[relay])-1,instr[4:]+": "+str(amount))
            relayPending[relay]=listTransactions
            sender=list(map(int, re.findall(r'\d+', instr)))[0]


    for i in range(len(walletBalance)):
        csvData[7][i+1]=walletBalance[i]

    
    for i in range(len(minerBal)):
        csvData[8][i+1]=minerBal[i]
        
    for i in range(len(minerBalance)):
        csvData[9][i+1]=minerBalance[i]
        
    for i in range(len(walletBal)):
        csvData[6][i+1]=walletBal[i]
        
    for i in range(len(walletBalance)):
        csvData[7][i+1]=walletBalance[i]
        
    for i in range(len(relayPending)):
        csvData[12+i]=["R"+str(i)]
        for j in range(len(relayPending[i])-1):
            csvData[12+i].append(relayPending[i][j])
        
       
def normal_simul(numRelays,numMiners,numExtraWallets):
    """
    Simulation of a normal case where all relays have miners. 
    numRelays is the number of relays. 
    numMiners is the number of miners.
    numExtraWallets is the number of wallets not attached to a miner.
    """
        
    if(numRelays>numMiners):
        sys.exit("The number of miners can not be smaller than the number of relays.")
    

    masterPort=thread_master(10000)
    relayPorts=thread_relays(numRelays,8000,masterPort)
    
    numWalletsPerRelay=wallets_per_relay(numRelays,numExtraWallets)
    walletList,passwordList=create_wallets(relayPorts,numWalletsPerRelay)
    
    numMinersPerRelay=miners_per_relay(numRelays,numMiners)
    minerList=create_miners(relayPorts, numMinersPerRelay)
    
    initiate_csvData(relayPorts,walletList,minerList,numMinersPerRelay,numWalletsPerRelay)
    mydir=os.getcwd()+"/simulation_results"
    filelist = [ f for f in os.listdir(mydir) if f.endswith(".csv") ]
    for f in filelist:
        os.remove(os.path.join(mydir, f))
    write_csv_file(csvData,"simulation_results/log0.csv")
    
        
    for i in range(200):
        
        for _ in range(10):
            do_action(minerList,walletList,passwordList,relayPorts)
        walletBalance=[ wallet.determine_wallet_money() for wallet in walletList]
        minerBalance=[miner.get_wallet_balance() for miner in minerList]
        analysecsvData(relayPorts,walletList,minerList,walletBalance,minerBalance)
        write_csv_file(csvData,"simulation_results/log"+str(i)+".csv")
        
        print("Wallet Balances:"+str(walletBalance))
        print("Miner Balances:"+str(minerBalance))










f = open(os.devnull, 'w')
oldStderr=sys.stderr
sys.stderr = f
    
normal_simul(2, 6, 6)

