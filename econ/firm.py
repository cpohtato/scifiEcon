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
        self.inv = [0 for i in range(NUM_MARKETS)]

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

        #   Solving for price using labour estimate and minimum product markup
        #   This is best guess of lowest price possible for firm with adequate labour supply
        A = 1
        newPrice = DICT_PPC[self.firmType] * MIN_MARKUP * wage / (A * (1 - labour/self.capital))
        if (newPrice < 0): newPrice = 0
        return newPrice

    def prodFunc(self, K: float, L: float):
        #   Production points = A * (L - L^2 / (2K))
        #   A is technology/other bonuses, K is capital, L is labour

        prodPoints = L - pow(L, 2) / (2 * K)

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

    def optimiseInput(self, marketConditions: list[list[float]]):
        
        inputsConsumed = [0 for i in range(NUM_MARKETS)]

        #   Only optimise labour for now
        wage = marketConditions[MKT_LABOUR][0]
        labourSupply = marketConditions[MKT_LABOUR][1]
        if (labourSupply == 0.0): return inputsConsumed
        if (wage == None): return inputsConsumed

        if not (self.firmType == FIRM_ENERGY):
            price = marketConditions[self.firmType][0]
            if (price == None): return inputsConsumed

        requestedLabour: float = self.findOptimalLabour(marketConditions)

        inputsConsumed[MKT_LABOUR] = requestedLabour
        self.inv[0] = requestedLabour
        wage = marketConditions[0][0]
        labourExpenses = requestedLabour * wage
        self.funds -= labourExpenses

        #   Assuming that all machinery is utilised
        machineryOperatingCost = self.capital * MACHINE_OP_COST
        self.funds -= machineryOperatingCost

        self.dayExpenses += labourExpenses + machineryOperatingCost

        # print(DICT_FIRM[self.firmType] + " hired " + str(round(requestedLabour, 2)))

        return inputsConsumed
    
    def findGoodsProduced(self):
        prodPoints = self.prodFunc(self.capital, self.inv[0])
        goodsProduced = prodPoints / DICT_PPC[self.firmType]
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
        marketShare: float = qtySupplied / totalQty
        self.markup = MIN_MARKUP + (MAX_MARKUP - MIN_MARKUP) * marketShare
    
    def payDividend(self):
        dividend = self.funds * DIVIDEND_RATIO
        self.funds -= dividend
        return dividend
    
    def refresh(self):
        #   Consume all labour
        self.inv[MKT_LABOUR] = 0
        self.dayExpenses = 0.0
        self.dayRevenue = 0.0