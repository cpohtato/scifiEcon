from .consts import *

class Market():
    def __init__(self, mktType, price: float):
        self.mktType = mktType
        self.price = price
        self.supplyTotal: float = 0.0
        self.supplySold: float = 0.0

    def addSupply(self, supply: float):
        self.supplyTotal += supply

    def buy(self, qty: float):
        self.supplySold += qty

    def getClearingRatio(self):
        if (self.supplyTotal > 0):
            return self.supplySold / self.supplyTotal
        else:
            return 0.0
        
    def setPrice(self, price: float):
        self.price = price

    def printResults(self):
        if (self.price == None):
            print(DICT_MKT[self.mktType] + ": None")
        else:
            print(DICT_MKT[self.mktType] + ": " + 
                str(round(self.supplySold, 2)) + "/" + 
                str(round(self.supplyTotal, 2)) + " @ " + 
                str(round(self.price, 2)) + "c ea.")

    def refresh(self):
        self.adjustPrice()
        self.clearSupply()

    def adjustPrice(self):

        if (self.supplyTotal == 0.0):
            self.price = None
            return

        clearingRatio = self.getClearingRatio()
        if (clearingRatio == EQUILIBRIUM_RATIO): return
        if (clearingRatio > EQUILIBRIUM_RATIO):
            multiplier = 1 + DICT_VISC[self.mktType] * PRICE_VISCOSITY * random.random() * (clearingRatio / EQUILIBRIUM_RATIO)
        else:
            multiplier = 1 - DICT_VISC[self.mktType] * PRICE_VISCOSITY * random.random() * min(((2 - clearingRatio / EQUILIBRIUM_RATIO)), 1.1)
        self.price *= multiplier
            
    def clearSupply(self):
        self.supplyTotal = 0
        self.supplySold = 0

    def getPrice(self):
        return self.price

    def getSupplyAvailable(self):
        available = self.supplyTotal - self.supplySold
        if (available < 0.0): available = 0.0
        return available

    def getSupplyTotal(self):
        return self.supplyTotal
    
    def getSupplySold(self):
        return self.supplySold