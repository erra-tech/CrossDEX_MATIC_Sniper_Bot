# Polygon_Quickswap_Sniper_Bot
Here is our Sniper bot from Erra.tech. You pay 1.5% fees on your swap amount. Automated features like Check Enabled Swapping and HoneypotCheck are included, and much more. You ALWAYS buy with Matic, the contract can convert your Matic to USDC/USDT if the token amount in that pool is higher, and buy your tokens with USDC/USDT!
In addition, you have the ability to check your purchased tokens for loss or profit (percentage input!) and react quickly when selling.

# Install
First of all, you need install Python3+
Run on Android you need Install [Termux](https://termux.com/) (Only from F-Droid is up to date!)
## Termux Setup:
```shell
pkg install python git cmake
pip install web3
pip install halo
```
```shell
Unix: $ sudo apt install python3 git cmake gcc
Windows: You need for build Web3 have installed VisualStudio BuildTools (cmake)!
```
### Setup your Address and secret key in config.yaml.

Download Code:  
```shell
git clone https://github.com/erra-tech/Polygon_Quickswap_Sniper_Bot/
cd Polygon_Quickswap_Sniper_Bot
```

Python Requirements install:  
```python
python -m pip install -r requirements.txt
```  

Start Sniper:  
```js
python sniper.py -t <TOKEN_ADDRESS> -a <AMOUNT> -tx <TXAMOUNT> -hp -wb <BLOCKS WAIT BEFORE BUY> -tp <TAKE PROFIT IN PERCENT> -sl <STOP LOSE IN PERCENT>
python sniper.py -t 0x831753DD7087CaC61aB5644b308642cc1c33Dc13 -a 0.001 -tx 2 -hp  -wb 10 -tp 50
python sniper.py -t 0x831753DD7087CaC61aB5644b308642cc1c33Dc13 --sellonly
python sniper.py -t 0x831753DD7087CaC61aB5644b308642cc1c33Dc13 -a 0.001 --buyonly
python sniper.py -t 0x831753DD7087CaC61aB5644b308642cc1c33Dc13 -tsl 10 -nb
```  

Here are all options with small infos:  

```python

requires:
-t or --token, Token for snipe e.g. "-t 0x34faa80fec0233e045ed4737cc152a71e490e2e3"
-a or --amount, float, Amount in Bnb to snipe e.g. "-a 0.1"
-tx or --txamount, how mutch tx you want to send? It split your BNB amount in e.g. "-tx 5"
```


  
```python
Position Managemant *optional*:
-tp or --takeprofit, Percentage TakeProfit from your input BNB amount. e.g. "-tp 50" 
-sl or --stoploss, Percentage StopLoss from your input BNB amount. e.g. "-tp 50" 
-tsl or --trailingstoploss, Percentage Trailing-Stop-loss from your first Quote "-tsl 50"
```
  

```python

extra:
-hp or --honeypot, if you use this Flag, your token get checks if token is honypot before buy!
-nb or --nobuy, No Buy, Skipp buy, if you want to use only TakeProfit/StopLoss/TrailingStopLoss
```
