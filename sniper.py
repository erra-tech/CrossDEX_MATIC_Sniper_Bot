# Thanks To Tranding-Tigers for give me permission to do that!

from txns import TXN
import argparse, yaml
from time import sleep
from halo import Halo
from style import style

ascii = """
   ____                             
  / __/__________ _                 
 / _// __/ __/ _ `/                 
/___/_/_/_/ _\_,_/              __  
  / |/ /__ / /__    _____  ____/ /__
 /    / -_) __/ |/|/ / _ \/ __/  '_/
/_/|_/\__/\__/|__,__/\___/_/ /_/\_\ 
                                    
                https://erra.network
"""

parser = argparse.ArgumentParser(description='Set your Token and Amount example: "sniper.py -t 0x831753dd7087cac61ab5644b308642cc1c33dc13 -a 0.2 -s 15"')
parser.add_argument('-t', '--token', help='str, Token for snipe e.g. "-t 0x831753dd7087cac61ab5644b308642cc1c33dc13"')
parser.add_argument('-a', '--amount',default=0, help='float, Amount in MATIC to snipe e.g. "-a 0.1"')
parser.add_argument('-tx', '--txamount', default=1, nargs="?", const=1, type=int, help='int, how mutch tx you want to send? It Split your MATIC Amount in e.g. "-tx 5"')
parser.add_argument('-hp', '--honeypot', action="store_true", help='Check if your token to buy is a Honeypot, e.g. "-hp" or "--honeypot"')
parser.add_argument('-nb', '--nobuy', action="store_true", help='No Buy, Skipp buy, if you want to use only TakeProfit/StopLoss/TrailingStopLoss')
parser.add_argument('-tp', '--takeprofit', default=0, nargs="?", const=True, type=int, help='int, Percentage TakeProfit from your input MATIC amount "-tp 50" ')
parser.add_argument('-sl', '--stoploss', default=0, nargs="?", const=True, type=int, help='int, Percentage Stop loss from your input MATIC amount "-sl 50" ')
parser.add_argument('-tsl', '--trailingstoploss', default=0, nargs="?", const=True, type=int, help='int, Percentage Trailing-Stop-loss from your first Quote "-tsl 50" ')
parser.add_argument('-wb', '--awaitBlocks', default=0, nargs="?", const=True, type=int, help='int, Await Blocks before sending BUY Transaction "-ab 50" ')
parser.add_argument('-so', '--sellonly',  action="store_true", help='Sell all your Tokens from given address')
parser.add_argument('-bo', '--buyonly',  action="store_true", help='Buy Tokens with from your given amount')
parser.add_argument('-dsec', '--DisabledSwapEnabledCheck',  action="store_true", help='this argument disabled the SwapEnabled Check!')
args = parser.parse_args()


class SniperBot():
    def __init__(self):
        self.parseArgs()
        self.settings = self.safe_loadSettings()
        self.SayWelcome()
    

    def safe_loadSettings(self):
        with open("config.yaml","r") as settings:
            settings = yaml.safe_load(settings)
        return settings


    def SayWelcome(self):
        print(style().GREEN + ascii+ style().RESET)
        print(style().BLUE +"""Attention, you pay 1% Tax on your swap amount!"""+ style().RESET)
        print(style().BLUE +"Start Sniper Tool with following arguments:"+ style().RESET)
        print(style().BLUE + "---------------------------------"+ style().RESET)
        print(style().GREEN + "Amount for Buy:",style().BLUE + str(self.amount) + " MATIC"+ style().RESET)
        print(style().GREEN + "Token to Interact :",style().BLUE + str(self.token) + style().RESET)
        print(style().GREEN + "Transaction to send:",style().BLUE + str(self.tx)+ style().RESET)
        print(style().GREEN + "Amount per transaction :",style().BLUE + str("{0:.8f}".format(self.amountForSnipe))+ style().RESET)
        print(style().GREEN + "Await Blocks before buy :",style().BLUE + str(self.wb)+ style().RESET)
        if self.tsl != 0:
            print(style().GREEN + "Trailing Stop loss Percent :",style().BLUE + str(self.tsl)+ style().RESET)
        if self.tp != 0:
            print(style().GREEN + "Take Profit Percent :",style().BLUE + str(self.tp)+ style().RESET)
            print(style().GREEN + "Target Output for Take Profit:",style().BLUE +str("{0:.8f}".format(self.takeProfitOutput))+ style().RESET)
        if self.sl != 0:
            print(style().GREEN + "Stop loss Percent :",style().BLUE + str(self.sl)+ style().RESET)
            print(style().GREEN + "Sell if Output is smaller as:",style().BLUE +str("{0:.8f}".format(self.stoploss))+ style().RESET)
        print(style().BLUE + "---------------------------------"+ style().RESET)
        

    def parseArgs(self):
        self.token = args.token
        if self.token == None:
            print(style.RED+"Please Check your Token argument e.g. -t 0x831753dd7087cac61ab5644b308642cc1c33dc13")
            print("exit!")
            raise SystemExit
        self.amount = args.amount
        if args.nobuy != True:  
            if not args.sellonly: 
                if self.amount == 0:
                    print(style.RED+"Please Check your Amount argument e.g. -a 0.01")
                    print("exit!")
                    raise SystemExit
        self.tx = args.txamount
        self.amountForSnipe = float(self.amount) / float(self.tx)
        self.hp = args.honeypot
        self.wb = args.awaitBlocks
        self.tp = args.takeprofit
        self.sl = args.stoploss 
        self.tsl = args.trailingstoploss
        self.stoploss = 0
        self.takeProfitOutput = 0
        if self.tp != 0:
            self.takeProfitOutput = self.calcProfit()
        if self.sl != 0:
            self.stoploss = self.calcloss()


    def calcProfit(self):
        a = ((self.amountForSnipe * self.tx) * self.tp) / 100
        b = a + (self.amountForSnipe * self.tx)
        return b 
    

    def calcloss(self):
        a = ((self.amountForSnipe * self.tx) * self.sl) / 100
        b = (self.amountForSnipe * self.tx) - a
        return b 

    def calcNewTrailingStop(self, currentPrice):
        a = (currentPrice  * self.tsl) / 100
        b = currentPrice - a
        return b

    def awaitBuy(self):
        spinner = Halo(text='await Buy', spinner='dots')
        spinner.start()
        for i in range(self.tx):
            spinner.start()
            self.TXN = TXN(self.token, self.amountForSnipe)
            tx = self.TXN.buy_token()
            spinner.stop()
            print(tx[1])
            if tx[0] != True:
                raise SystemExit 

    def awaitSell(self):
        spinner = Halo(text='await Sell', spinner='dots')
        spinner.start()
        self.TXN = TXN(self.token, self.amountForSnipe)
        tx = self.TXN.sell_tokens()
        spinner.stop()
        print(tx[1])
        if tx[0] != True:
            raise SystemExit 


    def awaitApprove(self):
        spinner = Halo(text='await Approve', spinner='dots')
        spinner.start()
        self.TXN = TXN(self.token, self.amountForSnipe)
        tx = self.TXN.approve()
        spinner.stop()
        print(tx[1])
        if tx[0] != True:
            raise SystemExit 


    def awaitBlocks(self):
        spinner = Halo(text='await Blocks', spinner='dots')
        spinner.start()
        waitForBlock = self.TXN.getBlockHigh() + self.wb
        while True:
            sleep(0.13)
            if self.TXN.getBlockHigh() > waitForBlock:
                spinner.stop()
                break
        print(style().BLUE+"[DONE] Wait Blocks finish!")
        

    def awaitLiquidity(self):
        spinner = Halo(text='await Liquidity', spinner='dots')
        spinner.start()
        while True:
            sleep(0.07)
            try:
                _,_, DEX =self.TXN.getOutputfromETHtoToken()
                name = self.TXN.getSwapName(DEX)
                spinner.stop()
                print(style().BLUE+ f"[DONE] Liquidity Found @{name}"+ style().RESET)
                break
            except Exception as e:
                print(e)
                if "UPDATE" in str(e):
                    raise SystemExit
                continue
        print(style().BLUE+"[DONE] Liquidity is Added!"+ style().RESET)


    def awaitEnabledBuy(self):
        spinner = Halo(text='await Dev Enables Swapping', spinner='dots')
        spinner.start()
        while True:
            sleep(0.07)
            try:
                if self.TXN.isTokenBuyabled() == True:
                    spinner.stop()
                    break
            except Exception as e:
                if "UPDATE" in str(e):
                    print(e)
                    raise SystemExit
                continue
        print(style().BLUE+"[DONE] Swapping is Enabeld!"+ style().RESET)
    

    def awaitMangePosition(self):
        #spinner = Halo(text='LoadingManagePosition', spinner='dots')
        #spinner.start()
        highestLastPrice = 0
        TokenBalance = round(self.TXN.get_token_balance(),5)
        while True:
            LastPrice = float(self.TXN.getOutputfromTokentoETH()[0] / (10**18))
            if self.tsl != 0:
                if LastPrice > highestLastPrice:
                    highestLastPrice = LastPrice
                    TrailingStopLoss = self.calcNewTrailingStop(LastPrice)
                if LastPrice < TrailingStopLoss:
                    #spinner.stop()
                    print()
                    print(style().BLUE+"[TRAILING STOP LOSS] Triggert!"+ style().RESET)
                    self.awaitSell()
                    break
            if self.takeProfitOutput != 0:
                if LastPrice >= self.takeProfitOutput:
                    #spinner.stop()
                    print()
                    print(style().BLUE+"[TAKE PROFIT] Triggert!"+ style().RESET)
                    self.awaitSell()
                    break
            if self.stoploss != 0:
                if LastPrice <= self.stoploss:
                    #spinner.stop()
                    print()
                    print(style().BLUE+"[STOP LOSS] Triggert!"+ style().RESET)
                    self.awaitSell()
                    break
            
            print("Token Balance:       " + str("{0:.5f}".format(TokenBalance)) + "     | CurrentOutput: "+str("{0:.5f}".format(LastPrice))+" MATIC", end="\r")
            sleep(1)

            if self.stoploss != 0:
                print("SL below: " + str("{0:.3f}".format(self.stoploss)) + " MATIC", end="\r")
                sleep(1)
            if self.takeProfitOutput != 0:
                print("TP over: " + str("{0:.3f}".format(self.takeProfitOutput)) + " MATIC", end="\r")
                sleep(1)
            if self.tsl != 0:  
                print("TSL below: " + str("{0:.3f}".format(TrailingStopLoss)) + " MATIC", end="\r")
                sleep(1)

        print(style().BLUE+"[DONE] Position Manager Finished!"+ style().RESET)


    def StartUP(self):
        self.TXN = TXN(self.token, self.amountForSnipe)
        if args.sellonly:
            print("Start SellOnly, Selling Now all tokens!")
            inp = input("please confirm y/n\n")
            if inp.lower() == "y": 
                print(self.TXN.sell_tokens()[1])
                raise SystemExit
            else:
                raise SystemExit

        if args.buyonly:
            print(f"Start BuyOnly, buy now with {self.amountForSnipe} MATIC tokens!")
            print(self.TXN.buy_token()[1])
            raise SystemExit

        if args.nobuy != True:
            self.awaitLiquidity()
            if args.DisabledSwapEnabledCheck != True:
                self.awaitEnabledBuy()

        honeyTax = self.TXN.checkToken()
        if self.hp == True:
            print(style().GREEN +"Checking Token is Honeypot..." + style().RESET)
            if honeyTax[2] == True:
                print(style.RED + "Token is Honeypot, exiting")
                raise SystemExit 
            elif honeyTax[2] == False:
                print(style().BLUE +"[DONE] Token is NOT a Honeypot!" + style().RESET)

        if honeyTax[1] > self.settings["MaxSellTax"]:
            print(style().RED+"Token SellTax exceeds Settings.yaml, exiting!")
            raise SystemExit

        if honeyTax[0] > self.settings["MaxBuyTax"]:
            print(style().RED+"Token BuyTax exceeds Settings.yaml, exiting!")
            raise SystemExit

        if float(self.TXN.getLiquidityInUSDC()) <= float(self.settings["MinLiquidityUSDC"]):
            print(style().RED+"Token MinLiquidityUSDC lower than settings, quit!")
            raise SystemExit
        else:
            print(style().GREEN + "[DONE] Token Liquidity is lager than Settings!" +style().RESET)

        if self.wb != 0: 
            self.awaitBlocks()

        if args.nobuy != True:
            self.awaitBuy()

        self.awaitApprove()
        if self.tsl != 0 or self.stoploss != 0 or self.takeProfitOutput != 0:
            self.awaitMangePosition()
        print(style().BLUE + "[DONE] Erra.Network Sniper Bot finish!" + style().RESET)

SniperBot().StartUP()
