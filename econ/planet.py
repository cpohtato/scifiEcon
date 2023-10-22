from .pop import *
from .firm import *
from .market import *

class Planet():

    def __init__(self):
        self.listPops: list[list[Pop]]      = self.initPops()
        self.listFirms: list[list[Firm]]    = self.initFirms()
        self.listMarkets: list[Market]      = self.initMarkets()

    def step(self):

        #   Pops offer labour
        #   Firm optimises production
        #   Pops get paid
        #   Production occurs
        #   Pops buy goods
        #   Pops consume goods and basic energy requirement
        #   Dividends get paid
        #   Adjust prices
        #   Refresh all entities

        self.popsSupplyLabour()
        self.firmsBuyInputs()
        self.popsReceiveWages()
        self.firmsProduceOutput()
        self.popsConsumeGoods()
        self.firmsReceiveRevenue()
        self.firmsPayDividends()
        
        #   Record stats before refresh
        mktPrices = self.getMarketPrices()
        employment = self.listMarkets[MKT_LABOUR].getClearingRatio()
        self.printFunds()
        energyPoor, foodPoor = self.findPoverty()
        totalEnergySupply = self.findTotalEnergySupply()

        self.refreshEconomy()

        return mktPrices, employment, energyPoor, foodPoor, totalEnergySupply

    def popsSupplyLabour(self):
        for drone in self.listPops[JOB_DRONE]:

            if (self.listMarkets[MKT_FOOD].getPrice() == None): foodPrice = 1.0
            else: foodPrice = self.listMarkets[MKT_FOOD].getPrice()

            if (self.listMarkets[MKT_LABOUR].getPrice() == None):
                wage: float = drone.priceLabour(foodPrice)
                self.listMarkets[MKT_LABOUR].setPrice(wage)
            else: 
                wage = self.listMarkets[MKT_LABOUR].getPrice()

            self.listMarkets[MKT_LABOUR].addSupply(drone.offerLabour(wage, foodPrice))

    def firmsBuyInputs(self):
        #   Firms optimise input bundle
        randOrder = self.getFirmRandOrder()
        for randFirm in randOrder:
            marketConditions: list[list[float]] = self.getMarketConditions()
            firmType, firmIdx = self.findRandFirm(randFirm)

            #   Price anchoring in empty market does not apply to fusion plants
            if not (firmType == FIRM_ENERGY):
                if (self.listMarkets[firmType].getPrice() == None):
                    newPrice: float = self.listFirms[firmType][firmIdx].setNewPrice(marketConditions)
                    self.listMarkets[firmType].setPrice(newPrice)
                    marketConditions: list[list[float]] = self.getMarketConditions()

            inputsConsumed: list[float] = self.listFirms[firmType][firmIdx].optimiseInput(marketConditions)

            #   Buy inputs from market
            for mkt in range(NUM_MARKETS):
                self.listMarkets[mkt].buy(inputsConsumed[mkt])

    def getFirmRandOrder(self):
        #   Random order of firms
        #   TODO: rework this so that we can get pop or firm rand order with same function
        numFirms = sum(len(industry) for industry in self.listFirms)
        randOrder = list(range(numFirms))
        random.shuffle(randOrder)
        return randOrder
    
    def getMarketConditions(self):
        #   Returns 2D array of price (0) and available quantity (1) for each market
        marketConditions: list[list[float]] = []
        for mkt in range(NUM_MARKETS):
            marketConditions.append([self.listMarkets[mkt].getPrice(), 
                                    self.listMarkets[mkt].getSupplyAvailable()])
        return marketConditions
    
    def findRandFirm(self, randFirm: int):
        #   Search 2D matrix for correct firm given randFirm index from getFirmRandOrder()
        #   listFirms[firmType][firmIdx] should select the correct random firm
        #   TODO: rework this so that we can find rand firm or pop using same function      
        firmType = 0
        firmIdx = 0
        firmsPassed = 0
        firmFound = False
        while not firmFound:
            if (len(self.listFirms[firmType]) > (randFirm - firmsPassed)):
                firmFound = True
                firmIdx = randFirm - firmsPassed
            else: 
                firmsPassed += len(self.listFirms[firmType])
                firmType += 1
        return firmType, firmIdx
    
    def popsReceiveWages(self):
        #   Pay drones wages
        clearingRatio = self.listMarkets[MKT_LABOUR].getClearingRatio()
        wage = self.listMarkets[MKT_LABOUR].getPrice()

        for drone in self.listPops[JOB_DRONE]:
            drone.receiveWage(clearingRatio, wage)

    def firmsProduceOutput(self):
        #   Produce output
        for firmType in range(NUM_FIRM_TYPES):
            for firm in self.listFirms[firmType]:
                outputsProduced = firm.produceGoods()

                if not (firmType == FIRM_ENERGY):
                    self.listMarkets[firmType].addSupply(outputsProduced)

    def popsConsumeGoods(self):
        self.popsConsumeEnergyRequirement()
        
        #   Pop order is randomised here
        numPops = sum(len(popType) for popType in self.listPops)
        randOrder = list(range(numPops))
        random.shuffle(randOrder)

        for randPop in randOrder:

            #   Aggregate information about input markets to give each pop
            marketConditions: list[list[float]] = []
            for mkt in range(NUM_MARKETS):
                marketConditions.append([self.listMarkets[mkt].getPrice(), 
                                        self.listMarkets[mkt].getSupplyAvailable()])

            #   Search 2D matrix for correct pop
            popType = 0
            popIdx = 0
            popsPassed = 0
            popFound = False
            while not popFound:
                if (len(self.listPops[popType]) > (randPop - popsPassed)):
                    popFound = True
                    popIdx = randPop - popsPassed
                else: 
                    popsPassed += len(self.listPops[popType])
                    popType += 1

            #   listPops[popType][popIdx] now selects the correct random pop
            #   Buy basic necessities first
            goodsConsumed: list[float] = self.listPops[popType][popIdx].consumeNecessities(marketConditions)

            #   Buy necessities from market
            for mkt in range(NUM_MARKETS):
                self.listMarkets[mkt].buy(goodsConsumed[mkt])

        #   Then process disposable income
        #   Add here and use same random order
        for randPop in randOrder:

            #   Aggregate information about input markets to give each pop
            marketConditions: list[list[float]] = []
            for mkt in range(NUM_MARKETS):
                marketConditions.append([self.listMarkets[mkt].getPrice(), 
                                        self.listMarkets[mkt].getSupplyAvailable()])

            #   Search 2D matrix for correct pop
            popType = 0
            popIdx = 0
            popsPassed = 0
            popFound = False
            while not popFound:
                if (len(self.listPops[popType]) > (randPop - popsPassed)):
                    popFound = True
                    popIdx = randPop - popsPassed
                else: 
                    popsPassed += len(self.listPops[popType])
                    popType += 1

            #   listPops[popType][popIdx] now selects the correct random pop
            #   Buy basic luxuries first
            goodsConsumed: list[float] = self.listPops[popType][popIdx].consumeLuxuries(marketConditions)

            #   Buy luxuries from market
            for mkt in range(NUM_MARKETS):
                self.listMarkets[mkt].buy(goodsConsumed[mkt])

    def popsConsumeEnergyRequirement(self):
        #   Pops consume energy requirements
        for type in range(NUM_JOB_TYPES):
            for pop in self.listPops[type]:
                pop.consumeEnergyReq()

    def firmsReceiveRevenue(self):
        #   Firms get paid from market
        for firmType in range(NUM_FIRM_TYPES):
            if not (firmType == FIRM_ENERGY):
                clearingRatio = self.listMarkets[firmType].getClearingRatio()
                price = self.listMarkets[firmType].getPrice()

                if not (price == None):
                    for firm in self.listFirms[firmType]:
                        firm.receiveRevenue(clearingRatio, price)

    def firmsPayDividends(self):
        #   Firms pay dividends
        #   Owner is hardcoded
        dividend = self.listFirms[FIRM_ENERGY][0].payDividend()
        print("Fusion dividend paid: " + str(round(dividend, 2)) + "c")
        self.listPops[JOB_EXEC][0].receiveDividend(dividend)

        dividend = self.listFirms[FIRM_FOOD][0].payDividend()
        print("Farm 0 dividend paid: " + str(round(dividend, 2)) + "c")
        self.listPops[JOB_EXEC][1].receiveDividend(dividend)

        dividend = self.listFirms[FIRM_FOOD][1].payDividend()
        print("Farm 1 dividend paid: " + str(round(dividend, 2)) + "c")
        self.listPops[JOB_EXEC][2].receiveDividend(dividend)

        dividend = self.listFirms[FIRM_FOOD][2].payDividend()
        print("Farm 2 dividend paid: " + str(round(dividend, 2)) + "c")
        self.listPops[JOB_EXEC][3].receiveDividend(dividend)

    def refreshEconomy(self):
        #   Reset and adjust market prices
        for mkt in self.listMarkets:
            mkt.printResults()
            mkt.refresh()

        #   Refresh pops
        for jobType in range(NUM_JOB_TYPES):
            for pop in self.listPops[jobType]:
                pop.refresh()

        #   Refresh firms
        for firmType in range(NUM_FIRM_TYPES):
            for firm in self.listFirms[firmType]:
                firm.refresh()

    def getMarketPrices(self):
        prices: list[float] = []
        for mkt in self.listMarkets:
            prices.append(mkt.getPrice())
        return prices

    def printFunds(self):
        print("Fusion plant funds: " + str(round(self.listFirms[FIRM_ENERGY][0].funds, 2)) + "c")
        print("Fusion owner funds: " + str(round(self.listPops[JOB_EXEC][0].funds, 2)) + "c")
        print("Fusion owner ESoL: " + str(round(self.listPops[JOB_EXEC][0].energyStandardOfLiving, 2)) + "c")

        print("Farm 0 funds: " + str(round(self.listFirms[FIRM_FOOD][0].funds, 2)) + "c")
        print("Farm 0 owner funds: " + str(round(self.listPops[JOB_EXEC][1].funds, 2)) + "c")
        print("Farm 0 owner ESoL: " + str(round(self.listPops[JOB_EXEC][1].energyStandardOfLiving, 2)) + "c")

        print("Drone 0 funds: " + str(round(self.listPops[JOB_DRONE][0].funds, 2)) + "c")
        print("Drone 0 ESoL: " + str(round(self.listPops[JOB_DRONE][0].energyStandardOfLiving, 2)) + "c")
    
    def findPoverty(self):
        total_pops = INIT_EXECS + INIT_DRONES
        energyStarveCount = 0
        foodStarveCount = 0

        for jobType in range(NUM_JOB_TYPES):
            for pop in self.listPops[jobType]:
                if (pop.energyStarved): energyStarveCount += 1
                if (pop.foodStarved): foodStarveCount += 1

        print("Energy starved: " + str(energyStarveCount))
        print("Food starved: " + str(foodStarveCount))

        energyPoor: float = energyStarveCount / total_pops
        foodPoor: float = foodStarveCount / total_pops
        return energyPoor, foodPoor
    
    def findTotalEnergySupply(self):
        totalEnergySupply = 0.0
        for jobType in range(NUM_JOB_TYPES):
            for pop in self.listPops[jobType]:
                totalEnergySupply += pop.funds
        
        for firmType in range(NUM_FIRM_TYPES):
            for firm in self.listFirms[firmType]:
                totalEnergySupply += firm.funds

        print("Total energy supply: " + str(round(totalEnergySupply, 2)))

        return totalEnergySupply

    def initPops(self):
        idCounter: int = 0
        listPops: list[list[Pop]] = [[] for i in range(NUM_JOB_TYPES)]

        for i in range(INIT_EXECS):
            listPops[JOB_EXEC].append(Pop(idCounter, JOB_EXEC, POP_INIT_CRED, 0.5))
            idCounter += 1

        for i in range(INIT_DRONES):
            randEdu = 0.25 + 0.5 * random.random()
            listPops[JOB_DRONE].append(Pop(idCounter, JOB_DRONE, POP_INIT_CRED, randEdu))
            idCounter += 1

        return listPops

    def initFirms(self):
        #   Hardcoded owners for now
        #   Fusion plant
        idCounter = 0
        listFirms: list[list[Firm]] = [[] for i in range(NUM_FIRM_TYPES)]

        listFirms[FIRM_ENERGY].append(Firm(idCounter, 0, FIRM_ENERGY, FIRM_INIT_CRED, 7.0))
        idCounter += 1

        #   Food
        listFirms[FIRM_FOOD].append(Firm(idCounter, 1, FIRM_FOOD, FIRM_INIT_CRED, 6.0))
        idCounter += 1

        listFirms[FIRM_FOOD].append(Firm(idCounter, 2, FIRM_FOOD, FIRM_INIT_CRED, 4.0))
        idCounter += 1

        listFirms[FIRM_FOOD].append(Firm(idCounter, 3, FIRM_FOOD, FIRM_INIT_CRED, 2.0))
        idCounter += 1

        return listFirms
    
    def initMarkets(self):
        listMarkets: list[Market] = []
        for mktType in range(NUM_MARKETS):
            listMarkets.append(Market(mktType, None))
        return listMarkets