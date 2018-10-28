"""Module containing the simulations regarding the difficulty adjustement."""
import random
import string
import Wallet,Miner,Master,Relay
import sys, os
import threading
from time import sleep

f = open(os.devnull, 'w')
oldStderr=sys.stderr
sys.stderr = f

relayPorts = [8050]
masterPort = 9764

# Starting the master
try:
    threading.Thread(target=Master.Master, args=(masterPort,)).start()
except:
    print("Error: unable to start thread")

# Starting the relays
for i in range(0, len(relayPorts)):
    port = relayPorts[i]
    try:
       threading.Thread(target=Relay.Relay, args=(masterPort, port,)).start()
    except:
        print("Error: unable to start thread " + str(i))

# Starting two wallets

password1 = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
Wallet1=Wallet.Wallet(relayPorts[0], password1)




#Starting miner
password2 = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
Miner1 = Miner.Miner(1,relayPorts[0],password2)



print("---------- Difficulty Adjustment Test ---------- ")

print("Starting difficulty: 2")
print("When mining speed / transacting speed > 16: ")
print("Let us take a break for 5 seconds ...")
sleep(5)

# difficulty is modified by master in a period of 16 new blocks
for idx in range(16):
    print("Miner1 mines a new block...")
    Miner1.do_pow()
    if idx%17==5:
        print("Miner1 transacts 10 coins to Wallet1")
        wallet1Address = Wallet1.get_address()
        Miner1.spend_money_from_wallet(wallet1Address, 10)


    diff=Miner1.get_difficulty_from_master()
    print("Current difficulty: "+str(diff))

print("Now we can see difficulty increased from 2 to 3")
print("Let us take a break for 5 seconds ...")
sleep(5)

print("When mining speed / transacting speed = 0.5")

# difficulty is modified by master in a period of 16 new blocks

for idx in range(16):

    print("Miner1 transacts two times of 5 coins to Wallet1")
    wallet1Address = Wallet1.get_address()
    Miner1.spend_money_from_wallet(wallet1Address, 5)
    Miner1.spend_money_from_wallet(wallet1Address, 5)

    print("Miner1 mines a new block")
    Miner1.do_pow()
    diff=Miner1.get_difficulty_from_master()
    walletbalance=Wallet1.determine_wallet_money()
    print("wallet balance: "+str(walletbalance))
    print("Current difficulty: "+str(diff))

print("Now we can see difficulty decreased from 3 to 2")

