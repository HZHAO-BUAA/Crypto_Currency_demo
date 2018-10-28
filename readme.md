### Programming Language & Dependencies: 
This program in compiled in python 3. The following dependecies are required to run this program:
1. anaconda3 -> Download and install anaconda https://www.anaconda.com/download/#macos, if not already installed
2. bottle -> use "pip install bottle" to install, if not already installed
2. pycrypto -> use "pip install pycrypto" to install, if not already installed

### Compilation and run:

Three simulations are available as a demonstation:
1. Basic simulation with one relay, two wallets and one miner.
2. A more complex simulation with a predefined number of relays, wallets and miners. This simulation saves logs in the simulation_results file.
3. A difficulty auto-adjustment simulation.

They can be run executing the following command:
1. Basic simulation: python SimpleSimul.py
2. Complex simulation: python Simulation.py
3. Difficulty simulation: python DifficultyAdjustmentSimulation.py



### Network Setup:
All the different modules in this program are simulated in single host using localhost with different ports range for each application<br/>
The following is network configuration detail for our project: 

The Master and relay nodes works as server, which response to the requests sent from Wallet and Miner. Their port configuration are given as follows.

For the basic and difficulty simulation:

1. Master IP (localhost): 127.0.0.1,  Master Listening Port:8050 <br/> 
2. Relay  IP (localhost): 127.0.0.1,  Relay Listening Port: 9764 <br/> 

For the complex simulation, the ports are allocated dynamically veryfing if the connection is made when initializing the port.



### Wallet Usage:
#### Individual wallet<br/>
In order to initialize an individal wallet, a fundamental network structure is needed, including a runing master with a listening port and (at least one) relay with a given port
> import Master <br/>
> m = Master.Master(10000) -> #Master is initialized with port 10000

> import Relay <br/>
> r = Relay.Relay(10000, 8000) -> #Relay is  initialized with master's port 10000 && self port 8000  <br/>

A Wallet can be initialized giving a corresponding relay port and an AES-128 password (at least 16 bytes).
> import Wallet  <br/>
> wallet1 = Wallet.Wallet(8000, WalletPassword) ->  #Wallet object is created and is initialized to relay port 8000<br/>

Three principal interactive functions are given by wallets:
> wallet1.determine_wallet_money() ---> #Check wallet object balance  <br/>
> wallet1.spend_money(receiverAddress, amount, password) ---> #Spend an anmout of coin to another wallet with address receiverAddress  <br/>
> wallet1.get_address() ---> #Get wallet's address  <br/>


#### Wallet associated with miner<br/> 
When a Miner is initialized, it automatically initializes a corresponding wallet, to store the bonus coins obtained by mining new blocks, this wallet can be manipulated through APIs in Miner:

> import Miner <br/>
> Miner1=Miner.Miner(MinerID,relayPort,Walletpassword2) ---> This procedure initializes a Miner and its associated Wallet with Walletpassword2 <br/>
> Miner1.get_wallet_balance() ---> Return balance in associated wallet <br/>
> Miner1.spend_money_from_wallet(receiverAddress, Amount): --->Spend an amount of coins from associated wallet to another wallet with receiverAddress <br/>

### Miner Usage:
In order to start a Miner, a fundamental network structure is needed, including a runing master with a listening port and (at least one) relay with a given port.
> import Master <br/>
> m = Master.Master(10000) -> #Master is initialized with port 10000 <br/>

> import Relay <br/>
> r = Relay.Relay(10000, 8000) -> #Relay is  initialized with master's port 10000 && self port 8000  <br/>

A Miner can be initialized giving a corresponding relay port and an AES-128 password pf it's associated wallet.

> Miner1 = Miner.Miner(1,relayPort,WalletPassword)

Two principal interactive functions are given by Miner:
> Miner1.do_pow() -> # Do Proof-of-Work in order to create new block and obtain 10 bonus coins
> Miner1.get_difficulty_from_master() # Get PoW difficulty from Master, In our system dificulty is maintained by Master and auto-adjusted [1]


#### Wallet's Full commands list
<p> * DSA.generate() -> Generate DSA private Key <p/> 
<p> * DSA.generate().publickey -> Generate DSA public Key
<p> * determine_wallet_money() - > Get wallet balance
<p> * create_transaction() -> Create a new transaction
<p> * spend_money() -> Create and send a tx of a certain amount to a receiver, if the wallet has enough money
<p> * get_my_address() -> Return wallet's self address
<p> * update_unspent_txs() -> Update the list of unspent txs from master to calculate the money available
<p> * send_tx_to_relay() -> Send new transaction to the linked relay
<p> * request_block_chain() -> Get the whole blockchain from the relay
<p> * miner_transaction() -> Create an initial transaction that is a reward for a miner, in case there is a miner linked with the wallet


#### Miner's Full commands list
<p> * send_block -> Send block to the linked relay
<p> * request_tx() -> Get a transaction waiting to be validated from the relay
<p> * request_block_chain() -> Get the blockchain from the linked relay
<p> * get_wallet_balance() -> Determine the balance of the linked wallet
<p> * get_initial_transaction(self) -> Get an inital tx from the linked wallet, as a reward for the mining
<p> * get_main_transaction(self) -> Get a regular transaction (not a reward and not a change) from the linked relay
<p> * validate_regular_tx(self, tx) -> Validate a regular tx by its signature and the liquidity of its sender. One parameter is required.
<p> * spend_money_from_wallet(self, receiverAddress, Amount) -> Spend wallet's money. Two parameters  are required.
<p> * def do_pow(self) -> Do the proof of work algorithm
<p> * def is_tx_pool_empty(self) -> check if the tx pool of the linked relay is empty


#### [1]. Difficulty auto-adjustment:
The difficulty is adjusted by master as follows:

> ReceivedEmptyBlock=0, ReceivedFullBlock=0 <br/>
> While ReceivedEmptyBlock+ReceivedFullBlock <= 16: <br/>
>  NewBlock=NewValidedBlockFromMiner br/>
>  If no main Transaction (only bonus Transaction) in NewBlock: <br/>
>   ReceivedEmptyBlock+=1 <br/>
>  else: br/>
>     ReceivedFullBlock += 1 <br/>
> If ReceivedEmptyBlock<=1: <br/>
>       Difficulty+=1 <br/>
> IF ReceivedFullBlock == 16 && Difficulty>1: <br/>
>       Difficulty-=1 <br/>



The proof of auto adjustment method is as follows:

Difficulty n = first n blocks of block header.

Assuming that PoW mining is a Bernoulli experiment，where probability of success: 

P=1/(16^n)
(Because hash value is hexadecimal)

Let X is the random variable of fist success of this Bernoulli experiment, it subjects to a Geometric distribution:

Distribution: P(X=k)=(1-P)^(k-1)*P
Expected Value: E(X)=1/P

So 1/P is the expected iteration for miner to mine a new block

When we +1 to difficulty,  Difficulty n’=n+1, the expected PoW iteration will becomes 1/P’=(1/P) *16 times larger.

So the speed of new block generation at n’ will slowdown to 1/16 than before.

As a result, when we detects in a certain time period, where: 

numFullBlock/(numFullBlock+numEmptyBlock) <=1/16, 

which means the speed of newBlock generation is 16 times larger than transaction generation speed.

In this case, we let difficulty n+1, to let new block generating speed become 1/16.


