import matplotlib
matplotlib.use('tkagg')
from matplotlib import pyplot as plt
# import numpy as np
from econ import *

def main():

    arcadia = Planet()

    #   Stats
    statDays = [i for i in range(1, 1 + SIM_LENGTH)]
    statWages = []
    statFoodPrices = []
    statTotalEnergySupply = []
    statEmployment = []
    statEnergyPoor = []
    statFoodPoor = []

    for day in range(SIM_LENGTH):

        print()
        print("===== Day " + str(day+1) + " =====")
        mktPrices, employment, energyPoor, foodPoor, totalEnergySupply = arcadia.step()

        statWages.append(mktPrices[MKT_LABOUR])
        statFoodPrices.append(mktPrices[MKT_FOOD])
        statEmployment.append(employment)
        statEnergyPoor.append(energyPoor)
        statFoodPoor.append(foodPoor)
        statTotalEnergySupply.append(totalEnergySupply)
    
    plt.figure(1)
    plt.plot(statDays, statWages, label="Wage")
    plt.plot(statDays, statFoodPrices, label="Food")
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

    plt.show()

if (__name__ == "__main__"):
    main()