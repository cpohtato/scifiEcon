from .consts import *

class Pop():
    def __init__(self, popId: int, jobType: int, initFunds: float, initEdu: float):
        self.popId: int = popId
        self.jobType: int = jobType
        self.funds: float = initFunds
        self.edu: float = initEdu
        self.offeredLabour: bool = False
        self.offeredLabourAmount: float = 0.0
        self.energyStarved: bool = False
        self.energyStandardOfLiving: float = 0.0
        self.foodStarved = False

    def offerLabour(self, wage: float, foodPrice: float):
        self.offeredLabour = True
        labourMax = self.edu
        costOfLiving = MONTHLY_CRED_REQ + foodPrice + self.energyStandardOfLiving
        ratio = (wage * labourMax * EQUILIBRIUM_RATIO) / (costOfLiving * MIN_MARKUP)
        labourOffered = ratio * EQUILIBRIUM_RATIO * labourMax
        labourOffered = min(labourOffered, labourMax)
        self.offeredLabourAmount = labourOffered
        return labourOffered
    
    def priceLabour(self, foodPrice: float):
        costOfLiving = MONTHLY_CRED_REQ + foodPrice + self.energyStandardOfLiving
        labourOffered = self.edu * EQUILIBRIUM_RATIO
        newWage = costOfLiving / labourOffered
        return newWage
    
    def receiveWage(self, clearingRatio: float, wage: float):
        if not self.offeredLabour: return
        self.funds += self.offeredLabourAmount * clearingRatio * wage

    def receiveDividend(self, dividend: float):
        self.funds += dividend

    def consumeEnergyReq(self):

        #   Basic energy requirement
        if (self.funds > MONTHLY_CRED_REQ):
            self.funds -= MONTHLY_CRED_REQ
            self.energyStarved = False
        else:
            self.funds = 0
            self.energyStarved = True

    def consumeNecessities(self, marketConditions: list[list[float]]):

        consumptionBundle = [0.0 for good in range(NUM_MARKETS)]

        foodPrice = marketConditions[FIRM_FOOD][0]
        foodSupply = marketConditions[FIRM_FOOD][1]

        if (self.funds == 0): return consumptionBundle
        if (foodSupply == 0): return consumptionBundle

        maxFoodPossible = min(self.funds/foodPrice, foodSupply)
        foodToBuy = min(maxFoodPossible, MONTHLY_FOOD_REQ)
        consumptionBundle[FIRM_FOOD] = foodToBuy

        if (foodToBuy < MONTHLY_FOOD_REQ): self.foodStarved = True
        else: self.foodStarved = False

        self.funds -= foodToBuy * foodPrice
        return consumptionBundle

    def consumeLuxuries(self, marketConditions: list[list[float]]):

        consumptionBundle = [0.0 for good in range(NUM_MARKETS)]

        #   Pops optimise burning energy and buying more stuff
        disposable = self.funds * (1 - POP_SAVINGS_RATIO)

        foodPrice = marketConditions[FIRM_FOOD][0]
        foodSupply = marketConditions[FIRM_FOOD][1]

        #   Hardcoded utility function, change later
        #   U = F^ALPHA * E^BETA
        ALPHA = 0.75
        BETA = 0.25

        optEnergy = disposable / (ALPHA/BETA + 1)
        # optEnergy = 0

        if not (foodPrice == None):
            optFood = ALPHA/(BETA * foodPrice) * optEnergy
            # optFood = disposable / foodPrice

            foodToBuy = min(optFood, foodSupply)
            consumptionBundle[MKT_FOOD] = foodToBuy
            self.funds -= foodToBuy * foodPrice
        else:
            optFood = 0

        #   Energy standard of living
        #   Energy just gets burned here
        self.energyStandardOfLiving = 0.8 * self.energyStandardOfLiving + 0.2 * optEnergy
        self.funds -= self.energyStandardOfLiving

        return consumptionBundle

    def refresh(self):
        self.offeredLabour = False
        self.offeredLabourAmount = 0.0
    
    def getEdu(self):
        #   Could be more complicated in future
        return self.edu