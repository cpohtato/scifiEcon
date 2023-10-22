import matplotlib
matplotlib.use('tkagg')
from matplotlib import pyplot as plt
import numpy as np
from econ import *

SIM_LENGTH: int = 1000

INIT_EXECS: int = 4
INIT_DRONES: int = 30

total_pops = INIT_EXECS + INIT_DRONES

#   Create pops

popIdCounter: int = 0
listPops: list[list[Pop]] = [[] for i in range(NUM_JOB_TYPES)]

for i in range(INIT_EXECS):
    listPops[JOB_EXEC].append(Pop(popIdCounter, JOB_EXEC, POP_INIT_CRED, 0.5))
    popIdCounter += 1

for i in range(INIT_DRONES):
    randEdu = 0.25 + 0.5 * random.random()
    listPops[JOB_DRONE].append(Pop(popIdCounter, JOB_DRONE, POP_INIT_CRED, randEdu))
    popIdCounter += 1

#   Create firm
#   Hardcoded owner

#   Fusion plant
firmIdCounter = 0
listFirms: list[list[Firm]] = [[] for i in range(NUM_FIRM_TYPES)]

listFirms[FIRM_FUSION].append(Firm(firmIdCounter, 0, FIRM_FUSION, FIRM_INIT_CRED, 7.0))
firmIdCounter += 1

#   Food
listFirms[FIRM_FOOD].append(Firm(firmIdCounter, 1, FIRM_FOOD, FIRM_INIT_CRED, 6.0))
firmIdCounter += 1

listFirms[FIRM_FOOD].append(Firm(firmIdCounter, 2, FIRM_FOOD, FIRM_INIT_CRED, 4.0))
firmIdCounter += 1

listFirms[FIRM_FOOD].append(Firm(firmIdCounter, 3, FIRM_FOOD, FIRM_INIT_CRED, 2.0))
firmIdCounter += 1

#   Create labour market

listMarkets: list[Market] = []
for mktType in range(NUM_MARKETS):
    listMarkets.append(Market(mktType, None))

#   Stats
statMonths = [i for i in range(1, 1 + SIM_LENGTH)]
statMktPrices = [[] for i in range(NUM_MARKETS)]
statEnergySupply = []
statEmployment = []
statEnergyPoor = []
statFoodPoor = []

for month in range(SIM_LENGTH):

    print()
    print("===== Month " + str(month+1) + " =====")

    #   Pops offer labour
    #   Firm optimises production
    #   Pops get paid
    #   Production occurs
    #   Pops buy goods
    #   Pops consume goods and basic energy requirement
    #   Dividends get paid
    #   Adjust prices
    #   Refresh all entities

    for drone in listPops[JOB_DRONE]:

        if (listMarkets[MKT_FOOD].getPrice() == None): foodPrice = 1.0
        else: foodPrice = listMarkets[MKT_FOOD].getPrice()

        if (listMarkets[MKT_LABOUR].getPrice() == None):
            #   Separated out because in future, pop will need more information to decide
            #   e.g. newWage = drone.priceLabour(priceOfEssentialGoods)
            wage: float = drone.priceLabour(foodPrice)
            listMarkets[MKT_LABOUR].setPrice(wage)
        else: 
            wage = listMarkets[MKT_LABOUR].getPrice()

        listMarkets[MKT_LABOUR].addSupply(drone.offerLabour(wage, foodPrice))

    #   Firms optimise input bundle
    #   Order of firms is random
    numFirms = sum(len(industry) for industry in listFirms)
    randOrder = list(range(numFirms))
    random.shuffle(randOrder)

    for randFirm in randOrder:

        #   Aggregate information about input markets to give each firm
        marketConditions: list[list[float]] = []
        for mkt in range(NUM_MARKETS):
            marketConditions.append([listMarkets[mkt].getPrice(), 
                                    listMarkets[mkt].getSupplyAvailable()])

        #   Search 2D matrix for correct firm
        firmType = 0
        firmIdx = 0
        firmsPassed = 0
        firmFound = False
        while not firmFound:
            if (len(listFirms[firmType]) > (randFirm - firmsPassed)):
                firmFound = True
                firmIdx = randFirm - firmsPassed
            else: 
                firmsPassed += len(listFirms[firmType])
                firmType += 1
        
        #   listFirms[firmType][firmIdx] now selects the correct random firm

        #   Price anchoring in empty market does not apply to fusion plants
        if not (firmType == FIRM_FUSION):
            if (listMarkets[firmType].getPrice() == None):
                newPrice: float = listFirms[firmType][firmIdx].setNewPrice(marketConditions)
                listMarkets[firmType].setPrice(newPrice)

                #   Update market conditions
                marketConditions: list[list[float]] = []
                for mkt in range(NUM_MARKETS):
                    marketConditions.append([listMarkets[mkt].getPrice(), 
                                            listMarkets[mkt].getSupplyAvailable()])

        inputsConsumed: list[float] = listFirms[firmType][firmIdx].optimiseInput(marketConditions)

        #   Buy inputs from market
        for mkt in range(NUM_MARKETS):
            listMarkets[mkt].buy(inputsConsumed[mkt])

    #   Pay drones wages
    clearingRatio = listMarkets[MKT_LABOUR].getClearingRatio()
    wage = listMarkets[MKT_LABOUR].getPrice()

    for drone in listPops[JOB_DRONE]:
        drone.receiveWage(clearingRatio, wage)

    #   Produce output
    for firmType in range(NUM_FIRM_TYPES):
        for firm in listFirms[firmType]:
            outputsProduced = firm.produceGoods()

            if not (firmType == FIRM_FUSION):
                listMarkets[firmType].addSupply(outputsProduced)

    #   Pops consume energy requirements
    for type in range(NUM_JOB_TYPES):
        for pop in listPops[type]:
            pop.consumeEnergyReq()

    #   Pop order is randomised here

    numPops = sum(len(popType) for popType in listPops)
    randOrder = list(range(numPops))
    random.shuffle(randOrder)

    for randPop in randOrder:

        #   Aggregate information about input markets to give each pop
        marketConditions: list[list[float]] = []
        for mkt in range(NUM_MARKETS):
            marketConditions.append([listMarkets[mkt].getPrice(), 
                                    listMarkets[mkt].getSupplyAvailable()])

        #   Search 2D matrix for correct pop
        popType = 0
        popIdx = 0
        popsPassed = 0
        popFound = False
        while not popFound:
            if (len(listPops[popType]) > (randPop - popsPassed)):
                popFound = True
                popIdx = randPop - popsPassed
            else: 
                popsPassed += len(listPops[popType])
                popType += 1

        #   listPops[popType][popIdx] now selects the correct random pop
        #   Buy basic necessities first
        goodsConsumed: list[float] = listPops[popType][popIdx].consumeNecessities(marketConditions)

        #   Buy necessities from market
        for mkt in range(NUM_MARKETS):
            listMarkets[mkt].buy(goodsConsumed[mkt])

    #   Then process disposable income
    #   Add here and use same random order
    for randPop in randOrder:

        #   Aggregate information about input markets to give each pop
        marketConditions: list[list[float]] = []
        for mkt in range(NUM_MARKETS):
            marketConditions.append([listMarkets[mkt].getPrice(), 
                                    listMarkets[mkt].getSupplyAvailable()])

        #   Search 2D matrix for correct pop
        popType = 0
        popIdx = 0
        popsPassed = 0
        popFound = False
        while not popFound:
            if (len(listPops[popType]) > (randPop - popsPassed)):
                popFound = True
                popIdx = randPop - popsPassed
            else: 
                popsPassed += len(listPops[popType])
                popType += 1

        #   listPops[popType][popIdx] now selects the correct random pop
        #   Buy basic luxuries first
        goodsConsumed: list[float] = listPops[popType][popIdx].consumeLuxuries(marketConditions)

        #   Buy luxuries from market
        for mkt in range(NUM_MARKETS):
            listMarkets[mkt].buy(goodsConsumed[mkt])

    #   Firms get paid from market
    for firmType in range(NUM_FIRM_TYPES):
        if not (firmType == FIRM_FUSION):
            clearingRatio = listMarkets[firmType].getClearingRatio()
            price = listMarkets[firmType].getPrice()

            if not (price == None):
                for firm in listFirms[firmType]:
                    firm.receiveRevenue(clearingRatio, price)

    #   Firms pay dividends
    #   Owner is hardcoded
    dividend = listFirms[FIRM_FUSION][0].payDividend()
    print("Fusion dividend paid: " + str(round(dividend, 2)) + "c")
    listPops[JOB_EXEC][0].receiveDividend(dividend)

    dividend = listFirms[FIRM_FOOD][0].payDividend()
    print("Farm 0 dividend paid: " + str(round(dividend, 2)) + "c")
    listPops[JOB_EXEC][1].receiveDividend(dividend)

    dividend = listFirms[FIRM_FOOD][1].payDividend()
    print("Farm 1 dividend paid: " + str(round(dividend, 2)) + "c")
    listPops[JOB_EXEC][2].receiveDividend(dividend)

    dividend = listFirms[FIRM_FOOD][2].payDividend()
    print("Farm 2 dividend paid: " + str(round(dividend, 2)) + "c")
    listPops[JOB_EXEC][3].receiveDividend(dividend)

    #   Record stats
    statMktPrices[MKT_LABOUR].append(listMarkets[MKT_LABOUR].getPrice())
    statMktPrices[MKT_FOOD].append(listMarkets[MKT_FOOD].getPrice())
    statEmployment.append(listMarkets[MKT_LABOUR].getClearingRatio())

    #   Reset and adjust market prices
    for mkt in listMarkets:
        mkt.printResults()
        mkt.refresh()

    #   Refresh pops
    for jobType in range(NUM_JOB_TYPES):
        for pop in listPops[jobType]:
            pop.refresh()

    #   Refresh firms
    for firmType in range(NUM_FIRM_TYPES):
        for firm in listFirms[firmType]:
            firm.refresh()

    print("Fusion plant funds: " + str(round(listFirms[FIRM_FUSION][0].funds, 2)) + "c")
    print("Fusion owner funds: " + str(round(listPops[JOB_EXEC][0].funds, 2)) + "c")
    print("Fusion owner ESoL: " + str(round(listPops[JOB_EXEC][0].energyStandardOfLiving, 2)) + "c")

    print("Farm 0 funds: " + str(round(listFirms[FIRM_FOOD][0].funds, 2)) + "c")
    print("Farm 0 owner funds: " + str(round(listPops[JOB_EXEC][1].funds, 2)) + "c")
    print("Farm 0 owner ESoL: " + str(round(listPops[JOB_EXEC][1].energyStandardOfLiving, 2)) + "c")

    print("Drone 0 funds: " + str(round(listPops[JOB_DRONE][0].funds, 2)) + "c")
    print("Drone 0 ESoL: " + str(round(listPops[JOB_DRONE][0].energyStandardOfLiving, 2)) + "c")

    totalEnergySupply = 0.0

    energyStarveCount = 0
    foodStarveCount = 0
    for jobType in range(NUM_JOB_TYPES):
        for pop in listPops[jobType]:
            if (pop.energyStarved): energyStarveCount += 1
            if (pop.foodStarved): foodStarveCount += 1
            totalEnergySupply += pop.funds
    print("Energy starved: " + str(energyStarveCount))
    print("Food starved: " + str(foodStarveCount))
    statEnergyPoor.append(energyStarveCount/total_pops)
    statFoodPoor.append(foodStarveCount/total_pops)

    
    for firmType in range(NUM_FIRM_TYPES):
        for firm in listFirms[firmType]:
            totalEnergySupply += firm.funds

    print("Total energy supply: " + str(round(totalEnergySupply, 2)))
    statEnergySupply.append(totalEnergySupply)
    
plt.figure(1)
plt.plot(statMonths, statMktPrices[MKT_LABOUR][:], label="Wage")
plt.plot(statMonths, statMktPrices[MKT_FOOD][:], label="Food")
plt.title("Market Prices")
plt.xlabel("Months")
plt.ylabel("Credits")
plt.xlim(1, SIM_LENGTH)
plt.legend()

plt.figure(2)
plt.plot(statMonths, statEnergySupply)
plt.title("Total Energy Supply")
plt.xlabel("Months")
plt.ylabel("Credits")
plt.xlim(1, SIM_LENGTH)

plt.figure(3)
plt.plot(statMonths, statEmployment)
plt.title("Employment")
plt.xlabel("Months")
plt.ylabel("Employment ratio")
plt.xlim(1, SIM_LENGTH)

plt.figure(4)
plt.plot(statMonths, statEnergyPoor, label="Energy Poor")
plt.plot(statMonths, statFoodPoor, label="Food Poor")
plt.title("Poverty")
plt.xlabel("Months")
plt.ylabel("Proportion")
plt.xlim(1, SIM_LENGTH)
plt.legend()

plt.show()