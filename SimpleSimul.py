"""Module containing a simple simulation of the cryptocurrency functioning"""
import threading
import Master, Relay, Miner, Wallet
import random
import string
from time import sleep
import sys,os

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
sleep(0.5)



print('Miner1 comes in ...')
password2 = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
Miner1 = Miner.Miner(1,relayPorts[0],password2)
print('Miner1 mines a Block ...')
Miner1.do_pow()
print('Miner1 gets bonus, now Miner 1 has 10 coins: ')
print("Miner1 has: "+str(Miner1.get_wallet_balance())+" coins.")
print("Liyuan comes in ..." )
password1 = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
Liyuan=Wallet.Wallet(relayPorts[0], password1)
print('Liyuan has no money: ')
print("Liyuan has: "+str(Liyuan.determine_wallet_money())+" coins")
print('Miner1 transacts 5 coins to Liyuan...')
LiyuanAddress=Liyuan.get_address()
Miner1.spend_money_from_wallet(LiyuanAddress, 5)
print('The miner on the same relay as Liyuan mines a new block to carry the new transaction...')
Miner1.do_pow()
print('Now Miner1 has 15 coins:')
print("Miner1 has: "+str(Miner1.get_wallet_balance())+" coins.")
print('Now new transaction is valid Liyuan gets 5 coins')
print("Liyuan has: "+str(Liyuan.determine_wallet_money())+" coins")

print('Julian comes in ... ')
Julian=Wallet.Wallet(relayPorts[0], password2)
print('Liyuan transacts 3 coins to Julian...')
JulianAddress=Julian.get_address()
Liyuan.spend_money(JulianAddress,3,password1)
print("Miner1 mines a new block to carry the new transaction...")
Miner1.do_pow()
print('Now new transaction is valid and Miner1 gets a new bonus of 10 coins:')
print("Miner1 has: "+str(Miner1.get_wallet_balance())+" coins.")
print('Now new transaction is valid Liyuan has 5-3=2 coins')
print("Liyuan has: "+str(Liyuan.determine_wallet_money())+" coins")
print('Now new transaction is valid Julian gets 3 coins')
print("Julian has: "+str(Julian.determine_wallet_money())+" coins")

