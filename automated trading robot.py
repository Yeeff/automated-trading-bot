import json, requests, threading
import time as timeStamp
from datetime import datetime
from binance.client import Client
from tkinter import *
from win10toast import ToastNotifier
import config

PRICE_IN_DEPTH = 0
QUANTITY_IN_DEPTH = 1

baseCurrencieList=["ETHBULL", "BULL","ETHBEAR","BEAR", "BTC"] 
coinPreselectedList = []

quoteCoin  = "USDT"

apiKey = config.apiKey 
secretKey = config.secretKey

client = Client(apiKey, secretKey)

def checkDensity (marketDepth, porcentageSet, minimunCantOrders, minimunTotalSum):
    
    totalSum=0
    orderCounter=0
    
    try:
       bestBid=float(marketDepth['bids'][0][PRICE_IN_DEPTH])
       bestAsk=float(marketDepth['asks'][0][PRICE_IN_DEPTH])
    except:
       return 2
         
    porcentageWindow = bestBid *(porcentageSet*0.01)
    
    #Restar a la primera orden si es compra y sumar si es venta
    topeBuy= bestBid -porcentageWindow
    topeSell=bestAsk+porcentageWindow

    #Bucles para sumar todas las ordenes que esten dentro de ese porcentaje
    try:
      while topeBuy<float(marketDepth['bids'][orderCounter][PRICE_IN_DEPTH]):
            totalSum += float(marketDepth['bids'][orderCounter][QUANTITY_IN_DEPTH])
            orderCounter=orderCounter+1
      totalSumBuy=totalSum
      totalCantBuy=orderCounter
      orderCounter=0;totalSum=0      
    
   
      while topeSell>float(marketDepth['asks'][orderCounter][PRICE_IN_DEPTH]):
            totalSum += float(marketDepth['asks'][orderCounter][QUANTITY_IN_DEPTH]) 
            orderCounter=orderCounter+1
      totalSumSell=totalSum
      totalCantSell=orderCounter
    except:
      return None  

    differenceCant = totalCantBuy/totalCantSell
    differenceSum = totalSumBuy/totalSumSell
    if differenceCant > minimunCantOrders:
        if differenceSum > minimunTotalSum:
          return coinPreselected(symbol, "buy", round(differenceCant,1),  getFormatedDateTimeNow() , bestBid)

    differenceCant = totalCantSell/totalCantBuy
    differenceSum = totalSumSell/ totalSumBuy
    if differenceCant > minimunCantOrders:
        if differenceSum > minimunTotalSum:
          return coinPreselected(symbol, "sell", round(differenceCant,1),  getFormatedDateTimeNow(), bestBid)

    return None


def applySecondFilter(pre_selected):

    porcentageSet = 0.2
    totalSum=0
    orderCounter=0
    marketDepth =pre_selected.getMarketDepth()
    
    try:
       bestBid=float(marketDepth['bids'][0][PRICE_IN_DEPTH])
       bestAsk=float(marketDepth['asks'][0][PRICE_IN_DEPTH])
    except:
       return 2
         
    porcentageWindow = bestBid *(porcentageSet*0.01)
    
    #Restar a la primera orden si es compra y sumar si es venta
    topeBuy= bestBid -porcentageWindow
    topeSell=bestAsk+porcentageWindow

    #Bucles para sumar todas las ordenes que esten dentro de ese porcentaje
    try:
      while topeBuy<float(marketDepth['bids'][orderCounter][PRICE_IN_DEPTH]):
            totalSum += float(marketDepth['bids'][orderCounter][QUANTITY_IN_DEPTH])
            orderCounter=orderCounter+1
      totalSumBuy=totalSum
      totalCantBuy=orderCounter
      orderCounter=0;totalSum=0      
   
      while topeSell>float(marketDepth['asks'][orderCounter][PRICE_IN_DEPTH]):
            totalSum += float(marketDepth['asks'][orderCounter][QUANTITY_IN_DEPTH]) 
            orderCounter=orderCounter+1
      totalSumSell=totalSum
      totalCantSell=orderCounter
    except:
      return None

    lenMax = max([totalCantSell, totalCantBuy])
    if pre_selected.getType() =="buy":
      if totalCantBuy > totalCantSell:
        if totalSumBuy > totalSumSell:
          if (totalSumBuy / lenMax) > (totalSumSell/ lenMax) :
            return True

    if pre_selected.getType() =="sell":
      if totalCantSell > totalCantBuy:
        if totalSumSell > totalSumBuy:
          if (totalSumSell / lenMax) > (totalSumBuy/ lenMax) :
            return True        

  
    return None
    



def getMarketDepth (market):
    url='https://api.binance.com/api/v3/depth'
    args={'symbol':market ,'limit':500}

    try:
       response=requests.get(url, params=args).json()
    except:
      return None
        
    if "bids" in response:
      return response
    else:
      print("Gettin market Error: {0}".format(response))
      timeStamp.sleep(3)
      return None  
         
def getFormatedDateTimeNow():
    dateTime= datetime.now()

    formatedDateTime= "{0}/{1} {2}:{3}".format(dateTime.month, dateTime.day, dateTime.hour, dateTime.minute      )
    return formatedDateTime

def showNotification(Message):
    toaster = ToastNotifier()
    try:
      toaster.show_toast(Message,"Something else") 
    except: return

    return

class coinPreselected:
    def __init__(self, symbol, type, highestCant, dateTimeIn, bestBid):
        self.symbol = symbol
        self.type = type
        self.highestCant = highestCant
        self.dateTimeIn = dateTimeIn
        self.bestBid = bestBid
     
    def getSymbol(self):
      return self.symbol
         
    def getType(self):
      return self.type

    def getBestBid(self):
      return self.bestBid

    def getHighestCant(self):
      return self.highestCant  
    
    def getDateTimeIn(self):
      return self.dateTimeIn
    
    def getMarketDepth(self):
      try:
        market = symbol +quoteCoin
        response = client.get_order_book(symbol= market , limit = "100")
      except:
        return None
        
      if "bids" in response:
        return response
      else:
        print("Gettin market Error: {0}".format(response))
        timeStamp.sleep(3)
        return None    


def createMarketOrder(orderSide):
    depth = client.get_order_book(symbol= market , limit = "5")

    bestBid = float( depth["bids"][0][0] ) 
    bestAsk = float( depth["asks"][0][0] ) 

    info = client.get_symbol_info(market)

    precision = info["baseAssetPrecision"] 

    for i in info["filters"]:
         if i["filterType"] == "MIN_NOTIONAL":
            minNotional = float( i["minNotional"] ) + 0.1
 
         if i["filterType"] == "PRICE_FILTER":
            tickSize = float( i["tickSize"] )

         if i["filterType"] == "LOT_SIZE":
            stepSize = float( i["stepSize"] )            
 
    if orderSide == SIDE_BUY:
       bestPriceWithSep = bestBid
    else:
       bestPriceWithSep = bestAsk   

    amount = minNotional / bestPriceWithSep
    amountByStep = int(float(amount)/stepSize)  * stepSize
    amountWithPrecision = "{:0.0{}f}".format(amountByStep, precision)

    if orderSide == SIDE_BUY:
       order = client.order_market_buy(
         symbol=market,
         quantity=amountWithPrecision)
       return order

    if orderSide == SIDE_SELL:
      order = client.order_market_sell(
        symbol=market,
        quantity=amountWithPrecision) 
      return order

    return None

#############################################################

while True:

      for baseCurrency in baseCurrencieList:  
          symbol = baseCurrency + quoteCoin
          
          Book=getMarketDepth(symbol)
          if Book == None: continue
          
          pre_selected=checkDensity(marketDepth=Book, porcentageSet=0.5, minimunCantOrders=3, minimunTotalSum=3) #libro,ventana,cantOrders,sumOrders
          if pre_selected == None: 
            continue
            print("Jump to continue when symbol is {}".format(symbol))

          if pre_selected.getSymbol() == "BTCUSDT":
             BULL_FilterPassed = checkDensity(client.get_order_book(symbol="BULLUSDT",limit="500"), 0.5, 3, 3)
             if BULL_FilterPassed != None:
               if BULL_FilterPassed.getType() == pre_selected.getType():
                  BULL_FilterPassed=True

             ETHBULL_FilterPassed = checkDensity(client.get_order_book(symbol="ETHBULLUSDT",limit="500"), 0.5,3, 3)
             if ETHBULL_FilterPassed != None:
               if ETHBULL_FilterPassed.getType() == pre_selected.getType():
                  ETHBULL_FilterPassed=True

             print("Others markets checked:  BULL_FilterPassed {},  ETHBULLUSDT {}".format(BULL_FilterPassed,ETHBULL_FilterPassed))

             if BULL_FilterPassed  or ETHBULL_FilterPassed : 
                
                print("{0}  {1}({2})   {3}   {4}".format(pre_selected.getType(), pre_selected.getSymbol(), pre_selected.getHighestCant(), pre_selected.getBestBid(), pre_selected.getDateTimeIn() ) )  
                threading.Thread(target=showNotification, args =(  "{0} {1} ({2})".format(pre_selected.getType(), baseCurrency , round(pre_selected.getHighestCant(),1))  , )).start()
          