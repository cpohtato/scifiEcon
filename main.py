from econ import *

def main():

    arcadia = Planet()

    #   Stats
    statDays = [i for i in range(1, 1 + SIM_LENGTH)]
    statWages = []
    statFoodPrices = []
    statCGPrices = []
    statWagesAdjusted = []
    statFoodPricesAdjusted = []
    statCGPricesAdjusted = []
    statTotalEnergySupply = []
    statEmployment = []
    statEnergyPoor = []
    statFoodPoor = []
    statEnergyESoL = []
    statFoodESoL = []
    statDroneESoL = []
    statGovtESoL = []
    statCGESoL = []

    for day in range(SIM_LENGTH):

        print()
        print("===== Day " + str(day+1) + " =====")

        if (day == 360):
            # arcadia.govt.incomeTaxRate = 0.2
            # arcadia.govt.companyTaxRate = 0.5
            arcadia.govt.energyTaxRate = 0.2

        mktPrices, employment, energyPoor, foodPoor, totalEnergySupply, avgESoL = arcadia.step()

        statWages.append(mktPrices[MKT_LABOUR])
        statFoodPrices.append(mktPrices[MKT_FOOD])
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
    
    plt.figure(1)
    plt.plot(statDays, statWages, label="Wage")
    plt.plot(statDays, statFoodPrices, label="Food")
    plt.plot(statDays, statCGPrices, label="CG")
    plt.title("Market Prices")
    plt.xlabel("Days")
    plt.ylabel("Credits")
    plt.xlim(1, SIM_LENGTH)
    plt.legend()

    plt.figure(2)
    plt.plot(statDays, statTotalEnergySupply)
    plt.title("Total Energy Supply")
    plt.xlabel("Days")
    plt.ylabel("Credits")
    plt.xlim(1, SIM_LENGTH)

    plt.figure(3)
    plt.plot(statDays, statEmployment)
    plt.title("Employment")
    plt.xlabel("Days")
    plt.ylabel("Employment ratio")
    plt.xlim(1, SIM_LENGTH)

    plt.figure(4)
    plt.plot(statDays, statEnergyPoor, label="Energy Poor")
    plt.plot(statDays, statFoodPoor, label="Food Poor")
    plt.title("Poverty")
    plt.xlabel("Days")
    plt.ylabel("Proportion")    
    plt.xlim(1, SIM_LENGTH)
    plt.legend()

    plt.figure(5)
    plt.plot(statDays, statEnergyESoL, label="Energy ESoL")
    plt.plot(statDays, statFoodESoL, label="Food ESoL")
    plt.plot(statDays, statDroneESoL, label="Drone ESoL")
    plt.plot(statDays, statGovtESoL, label="Govt ESoL")
    plt.plot(statDays, statCGESoL, label="CG ESoL")
    plt.title("Average ESoL")
    plt.xlabel("Days")
    plt.ylabel("ESoL")
    plt.xlim(1, SIM_LENGTH)
    plt.legend()

    plt.figure(6)
    plt.plot(statDays, statWagesAdjusted, label="Wage")
    plt.plot(statDays, statFoodPricesAdjusted, label="Food")
    plt.plot(statDays, statCGPricesAdjusted, label="CG")
    plt.title("Adjusted Market Prices")
    plt.xlabel("Days")
    plt.ylabel("Credits/Credit")
    plt.xlim(1, SIM_LENGTH)
    plt.legend()

    plt.show()

if (__name__ == "__main__"):
    main()