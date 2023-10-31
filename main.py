from econ import *

def main():

    arcadia = Planet()

    #   Stats
    #   TODO: make some class for all this info
    statDays = [i for i in range(1, 1 + SIM_LENGTH)]
    statWages = []
    statFoodPrices = []
    statPlasticsPrices = []
    statCGPrices = []
    statWagesAdjusted = []
    statFoodPricesAdjusted = []
    statCGPricesAdjusted = []
    statTotalEnergySupply = []
    statEmployment = []
    statEmploymentWeekMA = []
    statEnergyPoor = []
    statFoodPoor = []
    statEnergyESoL = []
    statFoodESoL = []
    statDroneESoL = []
    statGovtESoL = []
    statCGESoL = []
    statLabourSold = []
    statFoodSold = []
    statPlasticsSold = []
    statCGSold = []

    statEnergyIncome = []
    statFoodIncome = []
    statDroneIncome = []
    statGovtIncome = []
    statCGIncome = []

    for day in range(SIM_LENGTH):

        print()
        print("===== Day " + str(day+1) + " =====")

        if (day == 200):
            # arcadia.govt.incomeTaxRate = 0.2
            # arcadia.govt.companyTaxRate = 0.5
            arcadia.govt.energyTaxRate = 0.4

        mktPrices, employment, energyPoor, foodPoor, totalEnergySupply, avgESoL, incomes, sales = arcadia.step()

        statWages.append(mktPrices[MKT_LABOUR])
        statFoodPrices.append(mktPrices[MKT_FOOD])
        statPlasticsPrices.append(mktPrices[MKT_PLASTICS])
        statCGPrices.append(mktPrices[MKT_CONSUMER])
        statEmployment.append(employment)
        statEnergyPoor.append(energyPoor)
        statFoodPoor.append(foodPoor)
        statTotalEnergySupply.append(totalEnergySupply)
        statEnergyESoL.append(avgESoL[0])
        statFoodESoL.append(avgESoL[1])
        statDroneESoL.append(avgESoL[2])
        statGovtESoL.append(avgESoL[3])
        statCGESoL.append(avgESoL[4])
        if (mktPrices[MKT_LABOUR] == None): 
            statWagesAdjusted.append(None)
        else:
            statWagesAdjusted.append(mktPrices[MKT_LABOUR]/totalEnergySupply)
        if (mktPrices[MKT_FOOD] == None):
            statFoodPricesAdjusted.append(None)
        else:
            statFoodPricesAdjusted.append(mktPrices[MKT_FOOD]/totalEnergySupply)
        if (mktPrices[MKT_CONSUMER] == None):
            statCGPricesAdjusted.append(None)
        else:
            statCGPricesAdjusted.append(mktPrices[MKT_FOOD]/totalEnergySupply)
        statEnergyIncome.append(incomes[0])
        statFoodIncome.append(incomes[1])
        statDroneIncome.append(incomes[2])
        statGovtIncome.append(incomes[3])
        statCGIncome.append(incomes[4])
        statLabourSold.append(sales[MKT_LABOUR])
        statFoodSold.append(sales[MKT_FOOD])
        statPlasticsSold.append(sales[MKT_PLASTICS])
        statCGSold.append(sales[MKT_CONSUMER])

        if (day < 6):
            statEmploymentWeekMA.append(employment)
        else:
            avgEmp = sum(statEmployment[day-6:day+1]) / 7
            statEmploymentWeekMA.append(avgEmp)
    
    figCount = 0

    figCount += 1
    plt.figure(figCount)
    plt.plot(statDays, statWages, label="Wage")
    plt.plot(statDays, statFoodPrices, label="Food")
    plt.plot(statDays, statPlasticsPrices, label="Plastics")
    plt.plot(statDays, statCGPrices, label="CG")
    plt.title("Market Prices")
    plt.xlabel("Days")
    plt.ylabel("Credits")
    plt.xlim(1, SIM_LENGTH)
    plt.legend()

    figCount += 1
    plt.figure(figCount)
    plt.plot(statDays, statTotalEnergySupply)
    plt.title("Total Energy Supply")
    plt.xlabel("Days")
    plt.ylabel("Credits")
    plt.xlim(1, SIM_LENGTH)

    figCount += 1
    plt.figure(figCount)
    plt.plot(statDays, statEmployment, label='Raw')
    plt.plot(statDays, statEmploymentWeekMA, label='Moving Avg')
    plt.title("Employment")
    plt.xlabel("Days")
    plt.ylabel("Employment ratio")
    plt.xlim(1, SIM_LENGTH)

    figCount += 1
    plt.figure(figCount)
    plt.plot(statDays, statEnergyPoor, label="Energy Poor")
    plt.plot(statDays, statFoodPoor, label="Food Poor")
    plt.title("Poverty")
    plt.xlabel("Days")
    plt.ylabel("Proportion")    
    plt.xlim(1, SIM_LENGTH)
    plt.legend()

    # figCount += 1
    # plt.figure(figCount)
    # plt.plot(statDays, statEnergyESoL, label="Energy ESoL")
    # plt.plot(statDays, statFoodESoL, label="Food ESoL")
    # plt.plot(statDays, statDroneESoL, label="Drone ESoL")
    # plt.plot(statDays, statGovtESoL, label="Govt ESoL")
    # plt.plot(statDays, statCGESoL, label="CG ESoL")
    # plt.title("Average ESoL")
    # plt.xlabel("Days")
    # plt.ylabel("ESoL")
    # plt.xlim(1, SIM_LENGTH)
    # plt.legend()

    figCount += 1
    plt.figure(figCount)
    plt.plot(statDays, statWagesAdjusted, label="Wage")
    plt.plot(statDays, statFoodPricesAdjusted, label="Food")
    plt.plot(statDays, statCGPricesAdjusted, label="CG")
    plt.title("Adjusted Market Prices")
    plt.xlabel("Days")
    plt.ylabel("Credits/Credit")
    plt.xlim(1, SIM_LENGTH)
    plt.legend()

    figCount += 1
    plt.figure(figCount)
    plt.plot(statDays, statEnergyIncome, label="Energy")
    plt.plot(statDays, statFoodIncome, label="Food")
    plt.plot(statDays, statDroneIncome, label="Drone")
    plt.plot(statDays, statGovtIncome, label="Govt")
    plt.plot(statDays, statCGIncome, label="CG")
    plt.title("Average Income")
    plt.xlabel("Days")
    plt.ylabel("Credits")
    plt.xlim(1, SIM_LENGTH)
    plt.legend()

    figCount += 1
    plt.figure(figCount)
    plt.plot(statDays, statLabourSold, label="Labour")
    plt.plot(statDays, statFoodSold, label="Food")
    plt.plot(statDays, statCGSold, label="CG")
    plt.plot(statDays, statPlasticsSold, label="Plastics")
    plt.title("Market Sales")
    plt.xlabel("Days")
    plt.ylabel("Qty")
    plt.xlim(1, SIM_LENGTH)
    plt.legend()

    plt.show()

if (__name__ == "__main__"):
    main()