from time import sleep
from web3 import Web3
import yaml
from style import style
import numpy as np

class TXN():

    def __init__(self, token_address, quantity):
        self.w3 = self.connect()
        self.USDC = Web3.toChecksumAddress("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
        self.address, self.private_key = self.setup_address()
        self.token_address = Web3.toChecksumAddress(token_address)
        self.token_contract = self.setup_token()
        self.swapper_address, self.swapper = self.setup_swapper()
        self.slippage = self.setupSlippage()
        self.quantity = quantity
        self.nonce = self.w3.eth.getTransactionCount(self.address)

    def connect(self):
        with open("./config.yaml") as f:
            keys = yaml.safe_load(f)
        if keys["Provider"][:2].lower() == "ws":
            w3 = Web3(Web3.WebsocketProvider(keys["Provider"]))
        else:
            w3 = Web3(Web3.HTTPProvider(keys["Provider"]))
        return w3

    def fetchGas(self):
        with open("./config.yaml") as f:
            keys = yaml.safe_load(f)
        try: 
            int(float(keys['GWEI_GAS']))
            return int(keys['GWEI_GAS'] * (10**9))
        except:
            return self.w3.eth.gasPrice

            
    def setup_address(self):
        try:
            with open("./config.yaml") as f:
                keys = yaml.load(f, Loader=yaml.BaseLoader)
            if len(str(keys["address"])) <= 41:
                print(style.RED +"Check your Address in the config.yaml file!" + style.RESET)
                raise SystemExit
            if len(keys["private_key"]) <= 42:
                print(style.RED +"Set your PrivateKey in the config.yaml file!"+ style.RESET)
                raise SystemExit
        except Exception as e:
            print(e)
            raise SystemExit
        return Web3.toChecksumAddress(str(keys["address"])), keys["private_key"]


    def format_float(self, num):
        return np.format_float_positional(num, trim='-')


    def setupSlippage(self):
        with open("./config.yaml") as f:
            keys = yaml.safe_load(f)
        return keys['Slippage']
    

    def get_token_decimals(self):
        return self.token_contract.functions.decimals().call()


    def getBlockHigh(self):
        return self.w3.eth.block_number
    
    
    def setup_swapper(self):
        swapper_address = Web3.toChecksumAddress("0x442752d5Baa47aBBD1a36356Ce5f0Ad781577438") 
        with open("./abis/Swapper_ABI.json") as f:
            contract_abi = yaml.safe_load(f)
        swapper = self.w3.eth.contract(address=swapper_address, abi=contract_abi)
        return swapper_address, swapper


    def setup_token(self):
        with open("./abis/Token_ABI.json") as f:
            contract_abi = yaml.safe_load(f)
        token_contract = self.w3.eth.contract(address=self.token_address, abi=contract_abi)
        return token_contract


    def get_token_balance(self): 
        return self.token_contract.functions.balanceOf(self.address).call() / (10 ** self.token_contract.functions.decimals().call())

    def getSwapName(self, DEX):
        return self.swapper.functions.getDexInfo(DEX[-1]).call()[0]


    def getLiquidityInUSDC(self):
        Dex, PairToken, Liquidity = self.swapper.functions.getLiquidity(self.token_address).call()      
        if Web3.toChecksumAddress(PairToken) != self.USDC:
            Out, _, _  = self.swapper.functions.fetchOutputfromTokentoToken(PairToken, self.USDC, Liquidity).call()
            return self.format_float(float(Out/10**6))
        return self.format_float(float(Liquidity/10**6))
        

    def checkToken(self):
        tokenInfos = self.swapper.functions.getTokenInformations(self.token_address).call()
        buy_tax = round((tokenInfos[0] - tokenInfos[1]) / tokenInfos[0] * 100) 
        sell_tax = round((tokenInfos[2] - tokenInfos[3]) / tokenInfos[2] * 100)
        if tokenInfos[5] and tokenInfos[6] == True:
            honeypot = False
        else:
            honeypot = True
        return buy_tax, sell_tax, honeypot


    def isTokenBuyabled(self):
        try:
            self.quantity = round(self.quantity, 3) * (10**18)
            txn = self.swapper.functions.fromETHtoToken(
                self.token_address,
                self.slippage,
                self.address,
            ).buildTransaction(
                {'from': self.address, 
                'gas': 480000,
                'gasPrice': self.fetchGas(),
                'nonce': self.nonce, 
                'value': int(self.quantity)}
                )
            txn.update({ 'gas' : int(self.estimateGas(txn))}) 
            return True
        except Exception as e:
            print(e)
            return False

    def estimateGas(self, txn):
        gas = self.w3.eth.estimateGas({
                    "from": txn['from'],
                    "to": txn['to'],
                    "value": txn['value'],
                    "data": txn['data']})
        gas = gas + (gas / 10) # Adding 1/10 from gas to gas!
        return gas


    def getOutputfromETHtoToken(self):
        call = self.swapper.functions.fetchOutputfromETHtoToken(
            self.token_address,
            int(self.quantity * (10**18)),
            ).call()
        Amount, Way, Dex = call
        return Amount, Way, Dex


    def getOutputfromTokentoETH(self):
        call = self.swapper.functions.fetchOutputfromTokentoETH(
            self.token_address,
            int(self.token_contract.functions.balanceOf(self.address).call()),
            ).call()
        Amount, Way, Dex = call
        return Amount, Way, Dex


    def buy_token(self):
        trys = 0
        txn = self.swapper.functions.fromETHtoToken(
                    self.token_address,
                    self.slippage,
                    self.address
                ).buildTransaction(
                    {'from': self.address, 
                    'gas': 480000,
                    'gasPrice': self.fetchGas(),
                    'nonce': self.nonce, 
                    'value': int(self.quantity * (10**18))}
                    )
        txn.update({ 'gas' : int(self.estimateGas(txn))})
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )
        txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(style.GREEN + "\nBUY TX Send, Hash:",txn.hex() + style.RESET)
        print(style.GREEN + "https://polygonscan.com/tx/" + str(txn.hex()) + style.RESET)

        self.nonce += 1

        while trys < 3:
            try:
                sleep(2)
                txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                if txn_receipt["status"] == 1:
                    return True,style.GREEN +"\nBUY Transaction Successfull!" + style.RESET
                elif txn_receipt["status"] == 0:
                    return False, style.RED +"\nBUY Transaction Faild!" + style.RESET
            except:
                trys += 1
                continue
        return False, style.RED +"\nBUY Transaction Faild!" + style.RESET


    def is_approve(self):
        Approve = self.token_contract.functions.allowance(self.address ,self.swapper_address).call()
        Aproved_quantity = self.token_contract.functions.balanceOf(self.address).call()
        if int(Approve) <= int(Aproved_quantity):
            return False
        else:
            return True

    def approve(self):
        if self.is_approve() == False:
            trys = 0
            txn = self.token_contract.functions.approve(
                        self.swapper_address,
                        99999999999999999999999999999999999999
                    ).buildTransaction(
                        {'from': self.address, 
                        'gas': 100000,
                        'gasPrice': self.fetchGas(),
                        'nonce': self.nonce, 
                        'value': 0}
                        )
            txn.update({ 'gas' : int(self.estimateGas(txn))})
            signed_txn = self.w3.eth.account.sign_transaction(
                txn,
                self.private_key
            )
            txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(style.GREEN + "\nApprove TX Send, Hash:",txn.hex()+style.RESET)
            print(style.GREEN + "https://polygonscan.com/tx/" + str(txn.hex()) + style.RESET)

            self.nonce += 1

            while trys < 3:
                try:
                    sleep(2)
                    txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                    if txn_receipt["status"] == 1:
                        return True,style.GREEN +"\nApprove Successfull!"+ style.RESET
                    else:
                        return False, style.RED +"\nApprove Transaction Faild!"+ style.RESET
                except:
                    trys += 1
                    continue
            return False, style.RED +"\nApprove Transaction Faild!"+ style.RESET
        else:
            return True, style.GREEN +"\nAllready approved!"+ style.RESET


    def sell_tokens(self):
        self.approve()
        trys = 0
        txn = self.swapper.functions.fromTokentoETH(
                    int(self.token_contract.functions.balanceOf(self.address).call()),
                    self.token_address,
                    self.slippage,
                    self.address,
                ).buildTransaction({
                        'from': self.address, 
                        'gas': 550000,
                        'gasPrice': self.fetchGas(),
                        'nonce':self.nonce, 
                        'value': 0
                        })
        txn.update({ 'gas' : int(self.estimateGas(txn))})
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )
        txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(style.GREEN + "\nSELL TX Send, Hash :",txn.hex() + style.RESET)
        print(style.GREEN + "https://polygonscan.com/tx/" + str(txn.hex()) + style.RESET)
        self.nonce += 1
        while trys < 3:
            try:
                sleep(2)
                txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                if txn_receipt["status"] == 1:
                    return True,style.GREEN +"\nSELL Transaction Successfull!" + style.RESET
                elif txn_receipt["status"] == 0:
                    return False, style.RED +"\nSELL Transaction Faild!" + style.RESET
            except Exception as e:
                print(e)
                trys += 1
                continue
        return False, style.RED +"\nSELL Transaction Faild!" + style.RESET
        

#TXN = TXN("0x61f95bd637e3034133335C1baA0148E518D438ad", 1)
#
#print(TXN.fetchGas())
#print(TXN.getLiquidityInUSDC())
#print(TXN.isTokenBuyabled())