from .consts import *

class Govt():
    def __init__(self, initFunds: float, incomeTaxRate: float, companyTaxRate: float):
        self.funds = initFunds
        self.incomeTaxRate = incomeTaxRate
        self.companyTaxRate = companyTaxRate
        self.dayTaxRaised: float = 0.0

    def receiveTaxRevenue(self, taxRevenue: float):
        self.dayTaxRaised += taxRevenue
        self.funds += taxRevenue

    def giveWelfareBudget(self):
        welfareBudget: float = self.funds / 2
        self.funds -= welfareBudget
        return welfareBudget

    def refresh(self):
        self.dayTaxRaised = 0.0