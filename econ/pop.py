from .consts import *

class Pop():
    def __init__(self, popId: int, jobType: int, initFunds: float, initEdu: float):
        self.popId: int = popId
        self.jobType: int = jobType
        self.funds: float = initFunds
        self.edu: float = initEdu
        self.offeredLabour: bool = False
        self.offeredLabourAmount: float = 0.0
        self.dayGrossIncome: float = 0.0
        self.daySubsidies: float = 0.0
        self.dayTaxPaid: float = 0.0
        self.energyStarved: bool = False
        self.energyStandardOfLiving: float = 0.0
        self.foodStarved = False
        self.inv = [0.0 for good in range(NUM_MARKETS)]

        self.energyPref = 0.05 + 0.1 * random.random()
        self.foodPref = 0.05 + 0.1 * random.random()
        self.cgPref = 0.6 + 0.3 * random.random()

        self.willingnessToWork = 0.9 + 0.2 * random.random()

    def offerLabour(self, wage: float, foodPrice: float, cgPrice: float, incomeTaxRate: float):
        self.offeredLabour = True
        labourMax = self.edu
        costOfLiving = DAILY_CRED_REQ + foodPrice + self.energyStandardOfLiving + cgPrice
        ratio = (wage * (1 - incomeTaxRate) * labourMax * EQUILIBRIUM_RATIO) / (costOfLiving * MIN_MARKUP)
        labourOffered = ratio * EQUILIBRIUM_RATIO * labourMax * self.willingnessToWork
        labourOffered = min(labourOffered, labourMax)
        self.offeredLabourAmount = labourOffered
        return labourOffered
    
    def priceLabour(self, foodPrice: float, cgPrice: float, incomeTaxRate: float):
        costOfLiving = DAILY_CRED_REQ + foodPrice + self.energyStandardOfLiving + cgPrice
        labourOffered = self.edu * EQUILIBRIUM_RATIO
        newWage = (costOfLiving / labourOffered) / (1 - incomeTaxRate)
        return newWage
    
    def receiveWage(self, clearingRatio: float, wage: float):
        if not self.offeredLabour: return
        self.dayGrossIncome = self.offeredLabourAmount * clearingRatio * wage
        self.funds += self.dayGrossIncome

    def receiveDividend(self, dividend: float):
        self.dayGrossIncome += dividend
        self.funds += self.dayGrossIncome

    def receiveSubsidy(self, subsidy: float):
        self.daySubsidies += subsidy
        self.funds += self.daySubsidies

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
    
    def utilityFunc(self, bundle: list[float]): 
        energy: float = bundle[0]
        food: float = bundle[1]
        cg: float = bundle[2]
        utility = pow(energy+1, self.energyPref) * pow(food+1, self.foodPref) * pow(cg+1, self.cgPref)
        return utility
    
    def negUtilityFunc(self, bundle: list[float]): 
        negUtility = -1.0 * self.utilityFunc(bundle)
        return negUtility
    
    def margUtilityFunc(self, bundle: list[float]):
        energy: float = bundle[0]
        food: float = bundle[1]
        cg: float = bundle[2]
        dE = self.energyPref * pow(energy+1, self.energyPref-1) * pow(food+1, self.foodPref) * pow(cg+1, self.cgPref)
        dF = pow(energy+1, self.energyPref) * self.foodPref * pow(food+1, self.foodPref-1) * pow(cg+1, self.cgPref)
        dC = pow(energy+1, self.energyPref) * pow(food+1, self.foodPref) * self.cgPref * pow(cg+1, self.cgPref - 1)
        dArr = np.array([dE, dF, dC])
        return dArr

    def negMargUtilityFunc(self, bundle: list[float]):
        negMU = -1.0 * self.margUtilityFunc(bundle)
        return negMU

    def buyLuxuries(self, marketConditions: list[list[float]]):

        bundle = [0.0 for good in range(NUM_MARKETS)]
        disposable = self.funds * (1 - POP_SAVINGS_RATIO)
        if (disposable < 0.0): 
            disposable = 0.0
            self.energyStandardOfLiving = 0.8 * self.energyStandardOfLiving
            return bundle

        foodPrice = marketConditions[MKT_FOOD][0]
        if (foodPrice == None): 
            foodPrice = 0.0
            foodSupply = 0.0
        else:
            foodSupply = marketConditions[MKT_FOOD][1]
        
        cgPrice = marketConditions[MKT_CONSUMER][0]
        if (cgPrice == None):
            cgPrice = 0.0
            cgSupply = 0.0
        else:
            cgSupply = marketConditions[MKT_CONSUMER][1]

        disposable = np.float32(disposable)
        foodSupply = np.float32(foodSupply)
        cgSupply = np.float32(cgSupply)
        foodPrice = np.float32(foodPrice)
        cgPrice = np.float32(cgPrice)

        supplyBounds = Bounds(np.array([0.0, 0.0, 0.0]), np.array([disposable, foodSupply, cgSupply]))
        budgetConstraint = LinearConstraint(np.array([1.0, foodPrice, cgPrice]), np.array([-np.inf]), np.array([disposable]))
        initBundle = np.array([0.0, 0.0, 0.0])
        solution = minimize(self.negUtilityFunc, 
                            initBundle, 
                            method='SLSQP',
                            constraints=budgetConstraint, 
                            bounds=supplyBounds,
                            jac=self.negMargUtilityFunc)

        optEnergy = solution.x[0]
        optFood = solution.x[1]
        optCG = solution.x[2]

        bundle[MKT_FOOD] = optFood
        self.funds -= optFood * foodPrice
        bundle[MKT_CONSUMER] = optCG
        self.funds -= optCG * cgPrice

        #   Energy standard of living is a moving filter that represents pop expectations
        #   Energy just gets burned here
        self.energyStandardOfLiving = 0.8 * self.energyStandardOfLiving + 0.2 * optEnergy
        self.funds -= optEnergy

        if (self.jobType == JOB_EXEC):
            if ((self.popId == 5)):
                follow = True

        return bundle
    
    def consumeGoods(self):
        if (self.inv[MKT_FOOD] < DAILY_FOOD_REQ): self.foodStarved = True
        else: self.foodStarved = False
        self.inv[MKT_FOOD] = 0.0

    def refresh(self):
        self.offeredLabour = False
        self.offeredLabourAmount = 0.0
        self.dayGrossIncome = 0.0
        self.daySubsidies = 0.0
        self.dayTaxPaid= 0.0
    
    def getEdu(self):
        #   Could be more complicated in future
        return self.edu
    
    def payIncomeTax(self, incomeTaxRate: float):
        self.dayTaxPaid += self.dayGrossIncome * incomeTaxRate
        self.funds -=self.dayTaxPaid
        return self.dayTaxPaid
    
    def getNettIncome(self):
        #   Includes income and subsidies less tax
        return self.dayGrossIncome + self.daySubsidies - self.dayTaxPaid