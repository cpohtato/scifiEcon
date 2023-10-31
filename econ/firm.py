from .consts import *

class Firm():
    def __init__(self, firmId: int, ownerId: int, firmType: int, initCred: float, initCap: float):
        self.firmId = firmId
        self.ownerId = ownerId
        self.firmType = firmType
        self.funds = initCred
        self.dayExpenses = 0.0
        self.dayRevenue = 0.0

        #   Should eventually include capital in inventory
        self.capital = initCap
        self.inv = [0.0 for i in range(NUM_MARKETS)]

        #   Start as competitively as possible
        self.markup = MIN_MARKUP

    def setNewPrice(self, marketConditions: list[list[float]]):
        wage = marketConditions[MKT_LABOUR][0]
        labourSupply = marketConditions[MKT_LABOUR][1]
        maxLabour = min(labourSupply, self.funds/wage)

        #   This is hardcoded for now -- find a better way to estimate later
        LKRatio = 0.25
        labour = min(LKRatio * self.capital, maxLabour)
        if (labour == 0.0): return None

        inputCost = 0.0
        if (self.firmType == FIRM_CONSUMER):
            inputCost = 1 * marketConditions[MKT_PLASTICS][0]

        #   Solving for price using labour estimate and product markup
        #   This is best guess of lowest price possible for firm with adequate labour supply
        A = 1
        newPrice = DICT_PPC[self.firmType] * MAX_MARKUP * wage / (A * (1 - labour/self.capital)) + inputCost
        if (newPrice < 0): newPrice = 0
        return newPrice

    def prodFunc(self, K: float, L: float):
        #   Production points = A * (L - L^2 / (2K))
        #   A is technology/other bonuses, K is capital, L is labour

        prodPoints = 1.0 * (L - pow(L, 2) / (2 * K))

        return prodPoints
    
    def findOptimalLabour(self, marketConditions: list[list[float]]):
        wage = marketConditions[0][0]
        labourAvailable = marketConditions[0][1]

        #   Production directly convertible into credits for fusion plant
        #   This type turns productivity straight into credits
        #   No capital depreciation, constant profit margin
        # if (self.firmType == FIRM_ENERGY): price: float = CRED_PER_PP 
        if (self.firmType == FIRM_ENERGY): price: float = 1
        else: price: float = marketConditions[self.firmType][0]

        #   (price * 1) here should be replaced by (price * A)
        optimalLabour: float = self.capital * (1 - DICT_PPC[self.firmType] * self.markup * wage 
                                               / (price * 1))

        #   We can assume that productivity is monotonic up to inflection point
        #   Check for negative labour
        if (optimalLabour < 0): optimalLabour = 0

        #   Check for labour market contraints
        if (optimalLabour > labourAvailable):
                optimalLabour = labourAvailable

        #   Check budget constraint
        #   Spend up to half of budget on labour
        if (optimalLabour * wage > (self.funds * 0.5)):
            optimalLabour = (self.funds * 0.5) / wage

        return optimalLabour
    
    def profitFunc(self, bundle: list[float], prices: list[float]):
        if (self.firmType == FIRM_ENERGY):
            revenue = self.prodFunc(self.capital, bundle[MKT_LABOUR]) / DICT_PPC[self.firmType]
        elif (self.firmType == FIRM_CONSUMER):
            goodsProduced = self.prodFunc(self.capital, bundle[MKT_LABOUR]) / DICT_PPC[self.firmType]
            goodsProduced = min(goodsProduced, 1.0 * bundle[MKT_PLASTICS])
            revenue = goodsProduced * prices[self.firmType] * EQUILIBRIUM_RATIO
        else:
            goodsProduced = self.prodFunc(self.capital, bundle[MKT_LABOUR]) / DICT_PPC[self.firmType]
            revenue = goodsProduced * prices[self.firmType] * EQUILIBRIUM_RATIO
        
        costs = bundle[MKT_LABOUR] * prices[MKT_LABOUR]
        if (self.firmType == FIRM_CONSUMER): costs += goodsProduced * prices[MKT_PLASTICS]

        profit = revenue - costs
        return profit
    
    def negProfitFunc(self, bundle: list[float], prices: list[float]):
        return -1.0 * self.profitFunc(bundle, prices)
    
    def searchMaxProfit(self, supplyAvailable: list[float], supplyPrices: list[float], budget: float, numPoints: int):
        searchBounds = supplyAvailable
        for goodType in DICT_INPUTS[self.firmType]:
            maxCanBuy = budget / supplyPrices[goodType]
            if (maxCanBuy < searchBounds[goodType]): searchBounds[goodType] = maxCanBuy

        if (self.firmType == FIRM_PLASTICS):
            searchLabour = np.linspace(0, searchBounds[MKT_LABOUR], numPoints).tolist()
            maxProfit = 0.0
            optLabour = 0.0
            for labour in searchLabour[1:]:
                cost = labour * supplyPrices[MKT_LABOUR]
                if (cost > budget): break

                inputBundle = [0.0 for i in range(NUM_MARKETS)]
                inputBundle[MKT_LABOUR] = labour

                profit = self.profitFunc(inputBundle, supplyPrices)
                if (profit > maxProfit):
                    maxProfit = profit
                    optLabour = labour

            optInputBundle = [0.0 for i in range(NUM_MARKETS)]
            optInputBundle[MKT_LABOUR] = optLabour
            return optInputBundle

        if (self.firmType == FIRM_CONSUMER):

            searchLabour = np.linspace(0, searchBounds[MKT_LABOUR], numPoints).tolist()
            searchPlastics = np.linspace(0, searchBounds[MKT_PLASTICS], numPoints).tolist()

            maxProfit = 0.0
            optLabour = 0.0
            optPlastics = 0.0

            for labour in searchLabour[1:]:
                for plastics in searchPlastics[1:]:
                    cost = labour * supplyPrices[MKT_LABOUR] + plastics * supplyPrices[MKT_PLASTICS]
                    if (cost > budget): break

                    inputBundle = [0.0 for i in range(NUM_MARKETS)]
                    inputBundle[MKT_LABOUR] = labour
                    inputBundle[MKT_PLASTICS] = plastics

                    profit = self.profitFunc(inputBundle, supplyPrices)
                    if (profit > maxProfit):
                        maxProfit = profit
                        optLabour = labour
                        optPlastics = plastics

            optInputBundle = [0.0 for i in range(NUM_MARKETS)]
            optInputBundle[MKT_LABOUR] = optLabour
            optInputBundle[MKT_PLASTICS] = optPlastics
            return optInputBundle

    def optimiseInput(self, marketConditions: list[list[float]]):

        #   TODO: pls clean this disgusting mess
        
        inputsConsumed = [0 for i in range(NUM_MARKETS)]

        prices = []
        supplyAvailable = []
        for mkt in range(NUM_MARKETS):
            if (marketConditions[mkt][0] == None): prices.append(0.0)
            else: prices.append(marketConditions[mkt][0])
            supplyAvailable.append(marketConditions[mkt][1])

        if (self.firmType == FIRM_PLASTICS):
            inputsConsumed = self.searchMaxProfit(supplyAvailable, prices, self.funds/2.0, 50)
            #   TODO: clean this
            self.inv[MKT_LABOUR] = inputsConsumed[MKT_LABOUR]

        elif (self.firmType == FIRM_CONSUMER):
            inputsConsumed = self.searchMaxProfit(supplyAvailable, prices, self.funds/2.0, 50)
            #   TODO: clean this
            self.inv[MKT_LABOUR] = inputsConsumed[MKT_LABOUR]
            self.inv[MKT_PLASTICS] = inputsConsumed[MKT_PLASTICS]

        else:

            supplyBounds = Bounds([0.0 for mkt in range(NUM_MARKETS)], supplyAvailable)
            budget = LinearConstraint(prices, [-np.inf], [self.funds/2.0])
            initBundle = [0.0 for mkt in range(NUM_MARKETS)]
            solution = minimize(self.negProfitFunc,
                                initBundle,
                                prices,
                                method='SLSQP',
                                bounds=supplyBounds,
                                constraints=budget)
            inputsConsumed = solution.x
            self.inv[MKT_LABOUR] = inputsConsumed[MKT_LABOUR]

        

        # if (self.firmType == FIRM_CONSUMER):
        #     attemptToMake = self.findGoodsProduced()
        #     if (attemptToMake > marketConditions[MKT_PLASTICS][1]):
        #         self.inv[MKT_PLASTICS] = marketConditions[MKT_PLASTICS][1]
        #     else:
        #         self.inv[MKT_PLASTICS] = attemptToMake

        for mkt in range(NUM_MARKETS):
            self.dayExpenses += prices[mkt] * self.inv[mkt]

        self.funds -= self.dayExpenses

        #   Only optimise labour for now
        # wage = marketConditions[MKT_LABOUR][0]
        # labourSupply = marketConditions[MKT_LABOUR][1]
        # if (labourSupply == 0.0): return inputsConsumed
        # if (wage == None): return inputsConsumed

        # if not (self.firmType == FIRM_ENERGY):
        #     price = marketConditions[self.firmType][0]
        #     if (price == None): return inputsConsumed

        # requestedLabour: float = self.findOptimalLabour(marketConditions)

        # inputsConsumed[MKT_LABOUR] = requestedLabour
        # self.inv[0] = requestedLabour
        # wage = marketConditions[0][0]
        # labourExpenses = requestedLabour * wage
        

        #   Assuming that all machinery is utilised
        # machineryOperatingCost = self.capital * MACHINE_OP_COST
        # self.funds -= machineryOperatingCost

        # self.dayExpenses += labourExpenses #+ machineryOperatingCost

        # print(DICT_FIRM[self.firmType] + " hired " + str(round(requestedLabour, 2)))

        return self.inv
    
    def findGoodsProduced(self):
        prodPoints = self.prodFunc(self.capital, self.inv[MKT_LABOUR])
        goodsProduced = prodPoints / DICT_PPC[self.firmType]
        # if (self.firmType == FIRM_CONSUMER): goodsProduced = min(goodsProduced, self.inv[MKT_PLASTICS])
        if (goodsProduced < 0.0): goodsProduced = 0
        return goodsProduced

    def produceOutput(self):
        goodsProduced = self.findGoodsProduced()
        if not (self.firmType == FIRM_ENERGY): return goodsProduced

        #   Directly convert production into credits
        # print("Energy generated: " + str(round(goodsProduced, 2)))
        self.funds += goodsProduced
        self.dayRevenue = goodsProduced
        #   TODO: remove this for energy firms
        self.markup = MAX_MARKUP
        return 0.0   
        
    def receiveRevenue(self, clearingRatio: float, price: float):
        qtySupplied = self.findGoodsProduced()
        self.dayRevenue = qtySupplied * clearingRatio * price
        self.funds += self.dayRevenue

    def payTax(self, companyTaxRate: float, energyTaxRate: float):
        profit = self.dayRevenue - self.dayExpenses
        if (profit <= 0): return 0
        if (self.firmType == FIRM_ENERGY): totalTaxRate = companyTaxRate + energyTaxRate
        else: totalTaxRate = companyTaxRate
        tax = profit * totalTaxRate
        self.funds -= tax
        return tax

    def updateMarketShare(self, totalQty: float):
        qtySupplied = self.findGoodsProduced()
        if (totalQty == 0): marketShare = 0.0
        else: marketShare: float = qtySupplied / totalQty
        self.markup = MIN_MARKUP + (MAX_MARKUP - MIN_MARKUP) * marketShare
    
    def payDividend(self):
        dividend = self.funds * DIVIDEND_RATIO
        self.funds -= dividend
        return dividend
    
    def refresh(self):
        #   Consume all inputs
        self.inv = [0.0 for i in range(NUM_MARKETS)]
        self.dayExpenses = 0.0
        self.dayRevenue = 0.0