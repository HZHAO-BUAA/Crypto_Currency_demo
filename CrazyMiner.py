"""Module containing the simulation regarding the crazy miner behavior"""
import Master
import Relay
import threading
import Miner


def crazy_miner_simulation():
    """Start the 'crary miner' simulation."""
    relaysPorts = [8050]
    masterPort = 9801
    start_master(masterPort)
    start_relays(relaysPorts)


def start_master(masterPort):
    """Start the master for the simulation."""
    try:
        threading.Thread(target=Master.Master, args=(masterPort,)).start()
    except:
        print("Error: unable to start thread")


def start_relays(masterPort, relaysPorts):
    """Start the relays for the simulation."""
    for i in range(0, len(relaysPorts)):
        port = relaysPorts[i]
        try:
            threading.Thread(target=Relay.Relay, args=(masterPort, port,)).start()
        except:
            print("Error: unable to start thread " + str(i))
    print('miner 1 starts ...')
    Miner1 = Miner.Miner(1, relaysPorts[0], WalletPassword='pig11111111111111')
    for idx in range(100000):
        diff = Miner1.get_difficulty_from_master()
        print('Current difficulty = ' + str(diff))
        print('Miner 1 does a POW ...')
        Miner1.do_pow()
