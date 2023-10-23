from .consts import *

class Pop():
    def __init__(self, popId: int, jobType: int, initFunds: float, initEdu: float):
        self.popId: int = popId
        self.jobType: int = jobType
        self.funds: float = initFunds
        self.edu: float = initEdu
        self.offeredLabour: bool = False
        self.offeredLabourAmount: float = 0.0
        self.income: float = 0.0
        self.energyStarved: bool = False
        self.energyStandardOfLiving: float = 0.0
        self.foodStarved = False
        self.inv = [0.0 for good in range(NUM_MARKETS)]

    def offerLabour(self, wage: float, foodPrice: float, incomeTaxRate: float):
        self.offeredLabour = True
        labourMax = self.edu
        costOfLiving = DAILY_CRED_REQ + foodPrice + self.energyStandardOfLiving
        ratio = (wage * (1 - incomeTaxRate) * labourMax * EQUILIBRIUM_RATIO) / (costOfLiving * MIN_MARKUP)
        labourOffered = ratio * EQUILIBRIUM_RATIO * labourMax
        labourOffered = min(labourOffered, labourMax)
        self.offeredLabourAmount = labourOffered
        return labourOffered
    
    def priceLabour(self, foodPrice: float, incomeTaxRate: float):
        costOfLiving = DAILY_CRED_REQ + foodPrice + self.energyStandardOfLiving
        labourOffered = self.edu * EQUILIBRIUM_RATIO
        newWage = (costOfLiving / labourOffered) / (1 - incomeTaxRate)
        return newWage
    
    def receiveWage(self, clearingRatio: float, wage: float):
        if not self.offeredLabour: return
        self.income = self.offeredLabourAmount * clearingRatio * wage
        self.funds += self.income

    def receiveDividend(self, dividend: float):
        self.income = dividend
        self.funds += self.income

    def receiveSubsidy(self, subsidy: float):
        self.funds += subsidy

    def receiveGoods(self, bundle: list[float]):
        for good in range(NUM_MARKETS):
            self.inv[good] += bundle[good]

    def consumeEnergyReq(self):

        #   Basic energy requirement
        if (self.funds >= DAILY_CRED_REQ):
            self.funds -= DAILY_CRED_REQ
            self.energyStarved = False
        else:
            self.funds = 0
            self.energyStarved = True

    def buyBasics(self, marketConditions: list[list[float]]):

        bundle = [0.0 for good in range(NUM_MARKETS)]

        foodPrice = marketConditions[FIRM_FOOD][0]
        foodSupply = marketConditions[FIRM_FOOD][1]

        if (self.funds == 0): return bundle
        if (foodSupply == 0): return bundle

        maxFoodPossible = min(self.funds/foodPrice, foodSupply)
        foodToBuy = min(maxFoodPossible, DAILY_FOOD_REQ)
        bundle[FIRM_FOOD] = foodToBuy
        self.inv[MKT_FOOD] += foodToBuy
        self.funds -= foodToBuy * foodPrice
        return bundle

    def buyLuxuries(self, marketConditions: list[list[float]]):

        bundle = [0.0 for good in range(NUM_MARKETS)]

        #   Pops optimise burning energy and buying more stuff
        disposable = self.funds * (1 - POP_SAVINGS_RATIO)

        foodPrice = marketConditions[FIRM_FOOD][0]
        foodSupply = marketConditions[FIRM_FOOD][1]

        #   Hardcoded utility function, change later
        #   U = F^ALPHA * E^BETA
        ALPHA = 0.75
        BETA = 0.25

        optEnergy = disposable / (ALPHA/BETA + 1)

        if (foodPrice == None):
            optFood = 0
        else:
            optFood = ALPHA/(BETA * foodPrice) * optEnergy
            # optFood = disposable / foodPrice

            foodToBuy = min(optFood, foodSupply)
            bundle[MKT_FOOD] = foodToBuy
            self.inv[MKT_FOOD] += foodToBuy
            self.funds -= foodToBuy * foodPrice

        #   Energy standard of living
        #   Energy just gets burned here
        self.energyStandardOfLiving = 0.8 * self.energyStandardOfLiving + 0.2 * optEnergy
        self.funds -= self.energyStandardOfLiving

        return bundle
    
    def consumeGoods(self):
        if (self.inv[MKT_FOOD] < DAILY_FOOD_REQ): self.foodStarved = True
        else: self.foodStarved = False
        self.inv[MKT_FOOD] = 0.0

    def refresh(self):
        self.offeredLabour = False
        self.offeredLabourAmount = 0.0
        self.income = 0.0
    
    def getEdu(self):
        #   Could be more complicated in future
        return self.edu
    
    def payIncomeTax(self, incomeTaxRate: float):
        tax = self.income * incomeTaxRate
        self.funds -= tax
        return tax