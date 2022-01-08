from time import sleep
from web3 import Web3
import yaml, sys
from style import style

class TXN():
    def __init__(self, token_address, quantity):
        self.w3 = self.connect()
        self.address, self.private_key = self.setup_address()
        self.token_address = Web3.toChecksumAddress(token_address)
        self.token_contract = self.setup_token()
        self.swapper_address, self.swapper = self.setup_swapper()
        self.slippage = self.setupSlippage()
        self.quantity = quantity 
        self.gas_price = self.setupGas()

    def connect(self):
        with open("./config.yaml") as f:
            keys = yaml.safe_load(f)
        if keys["Provider"][:2].lower() == "ws":
            w3 = Web3(Web3.WebsocketProvider(keys["Provider"]))
        else:
            w3 = Web3(Web3.HTTPProvider(keys["Provider"]))
        return w3

    def setupGas(self):
        with open("./config.yaml") as f:
            keys = yaml.safe_load(f)
        return int(keys['GWEI_GAS'] * (10**9))

    def setup_address(self):
        try:
            with open("./config.yaml") as f:
                keys = yaml.load(f, Loader=yaml.BaseLoader)
            if len(str(keys["address"])) <= 41:
                print(style.RED +"Check your Address in the config.yaml file!" + style.RESET)
                sys.exit()
            if len(keys["private_key"]) <= 42:
                print(style.RED +"Set your PrivateKey in the config.yaml file!"+ style.RESET)
                sys.exit()
        except Exception as e:
            print(e)
            sys.exit()
        return str(keys["address"]), keys["private_key"]


    def setupSlippage(self):
        with open("./config.yaml") as f:
            keys = yaml.safe_load(f)
        return keys['Slippage']


    def get_token_decimals(self):
        return self.token_contract.functions.decimals().call()


    def getBlockHigh(self):
        return self.w3.eth.block_number


    def setup_swapper(self):
        swapper_address = Web3.toChecksumAddress("0xDE4146a54dd3c270f31d7129f92792BAA504A2cf") 
        with open("./abis/MATIC_Swapper.json") as f:
            contract_abi = yaml.safe_load(f)
        swapper = self.w3.eth.contract(address=swapper_address, abi=contract_abi)
        return swapper_address, swapper


    def setup_token(self):
        with open("./abis/tokenabi.json") as f:
            contract_abi = yaml.safe_load(f)
        token_contract = self.w3.eth.contract(address=self.token_address, abi=contract_abi)
        return token_contract

    def get_token_balance(self): 
        return self.token_contract.functions.balanceOf(self.address).call() / (10 ** self.token_contract.functions.decimals().call())


    def checkToken(self):
        tokenInfos = self.swapper.functions.getTokenInfos(self.token_address).call()
        buy_tax = round((tokenInfos[0] - tokenInfos[1]) / tokenInfos[0] * 100) 
        sell_tax = round((tokenInfos[2] - tokenInfos[3]) / tokenInfos[2] * 100)
        if tokenInfos[5] and tokenInfos[6] == True:
            honeypot = False
        else:
            honeypot = True
        return buy_tax, sell_tax, honeypot


    def checkifTokenBuyDisabled(self):
        disabled = self.swapper.functions.getTokenInfos(self.token_address).call()[4] #True if Buy is enabled, False if Disabled.
        return disabled


    def estimateGas(self, txn):
        gas = self.w3.eth.estimateGas({
                    "from": txn['from'],
                    "to": txn['to'],
                    "value": txn['value'],
                    "data": txn['data']})
        gas = gas + (gas / 10) # Adding 1/10 from gas to gas!
        return gas


    def getOutputfromMATICtoToken(self):
        call = self.swapper.functions.getOutputfromMATICtoToken(
            self.token_address,
            int(self.quantity * (10**18)),
            ).call()
        Amount = call[0]
        Way = call[1]
        return Amount, Way


    def getOutputfromTokentoMATIC(self):
        call = self.swapper.functions.getOutputfromTokentoMATIC(
            self.token_address,
            int(self.token_contract.functions.balanceOf(self.address).call()),
            ).call()
        Amount = call[0]
        Way = call[1]
        return Amount, Way


    def buy_token(self):
        self.quantity = round(self.quantity,3) * (10**18)
        txn = self.swapper.functions.fromMATICtoToken(
            self.address,
            self.token_address,
            self.slippage
        ).buildTransaction(
            {'from': self.address, 
            'gas': 480000,
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.getTransactionCount(self.address), 
            'value': int(self.quantity)}
            )
        txn.update({ 'gas' : int(self.estimateGas(txn))})
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )
        txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(style.GREEN + "\nBUY Hash:",txn.hex() + style.RESET)
        txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
        sleep(3)
        if txn_receipt["status"] == 1: return True,style.GREEN +"\nBUY Transaction Successfull!" + style.RESET
        else: return False, style.RED +"\nBUY Transaction Faild!" + style.RESET


    def is_approve(self):
        Approve = self.token_contract.functions.allowance(self.address ,self.swapper_address).call()
        Aproved_quantity = self.token_contract.functions.balanceOf(self.address).call()
        if int(Approve) <= int(Aproved_quantity):
            return False
        else:
            return True

    def approve(self):
        if self.is_approve() == False:
            txn = self.token_contract.functions.approve(
                self.swapper_address,
                9999999999999999999999999
            ).buildTransaction(
                {'from': self.address, 
                'gas': 100000,
                'gasPrice': self.gas_price,
                'nonce': self.w3.eth.getTransactionCount(self.address), 
                'value': 0}
                )
            txn.update({ 'gas' : int(self.estimateGas(txn))})
            signed_txn = self.w3.eth.account.sign_transaction(
                txn,
                self.private_key
            )
            txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(style.GREEN + "\nApprove Hash:",txn.hex()+style.RESET)
            txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)   
            sleep(3)

            if txn_receipt["status"] == 1: return True,style.GREEN +"\nApprove Successfull!"+ style.RESET
            else: return False, style.RED +"\nApprove Transaction Faild!"+ style.RESET
        else:
            return True, style.GREEN +"\nAllready approved!"+ style.RESET


    def sell_tokens(self):
        self.approve()
        txn = self.swapper.functions.fromTokentoMATIC(
            self.address,
            self.token_address,
            int(self.token_contract.functions.balanceOf(self.address).call()),
            self.slippage
        ).buildTransaction(
            {'from': self.address, 
            'gas': 550000,
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.getTransactionCount(self.address), 
            'value': 0}
            )
        txn.update({ 'gas' : int(self.estimateGas(txn))})
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )
        txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(style.GREEN + "\nSELL Hash :",txn.hex() + style.RESET)
        sleep(3)
        txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
        if txn_receipt["status"] == 1: return True,style.GREEN +"\nSELL Transaction Successfull!" + style.RESET
        else: return False, style.RED +"\nSELL Transaction Faild!" + style.RESET