from .consts import *

class Govt():
    def __init__(self, initFunds: float, incomeTaxRate: float, companyTaxRate: float, energyTaxRate: float):
        self.funds = initFunds
        self.incomeTaxRate = incomeTaxRate
        self.companyTaxRate = companyTaxRate
        self.energyTaxRate = energyTaxRate
        self.dayTaxRaised: float = 0.0
        self.dayAdminRatio: float = 1.0

        self.policyEnergyRedistribution = True
        self.policyFoodRedistribution = True

    def buyAdminLabour(self, marketConditions: list[list[float]]):
        wage = marketConditions[MKT_LABOUR][0]
        labourAvailable = marketConditions[MKT_LABOUR][1]

        labourDemand = 0.0
        numPops = INIT_EXECS + INIT_DRONES
        numFirms = 4
        numEnergyFirms = 1
        if (self.incomeTaxRate > 0.0): labourDemand += numPops * 0.01
        if (self.companyTaxRate > 0.0): labourDemand += numFirms * 0.1
        if (self.energyTaxRate > 0.0): labourDemand += numEnergyFirms * 0.1
        if (self.policyEnergyRedistribution): labourDemand += numPops * 0.01
        if (self.policyFoodRedistribution): labourDemand += numPops * 0.01

        labourRequested = min(labourDemand, labourAvailable)
        labourRequested = min(labourRequested, self.funds / wage)
        self.funds -= labourRequested * wage
        self.dayAdminRatio = labourRequested / labourDemand
        print("Govt labour: " + str(round(labourRequested, 2)) + "/" + str(round(labourDemand, 2)))

        bundle = [0.0 for good in range(NUM_MARKETS)]
        bundle[MKT_LABOUR] = labourRequested

        return bundle


    def receiveTaxRevenue(self, taxRevenue: float):
        self.dayTaxRaised += taxRevenue
        self.funds += taxRevenue

    def giveWelfareBudget(self):
        welfareBudget: float = self.funds / 2
        self.funds -= welfareBudget
        return welfareBudget
    
    def giveWelfare(self, poorDeficit: float):
        welfareBudget = self.funds
        if (welfareBudget < poorDeficit):
            deficitSubsidyRatio = welfareBudget / poorDeficit
        else:
            deficitSubsidyRatio = 1.0
            welfareBudget = poorDeficit
        
        self.funds -= welfareBudget
        return welfareBudget, deficitSubsidyRatio

    def refresh(self):
        print("Treasury: " + str(round(self.funds, 2)))
        self.dayTaxRaised = 0.0
        