from .utils import *

SIM_LENGTH: int = 360

INIT_EXECS: int = 4
INIT_DRONES: int = 30

#   Proportion of goods in market sold to be considered market-clearing
EQUILIBRIUM_RATIO = 0.9

MIN_MARKUP = 1.2 / EQUILIBRIUM_RATIO
MAX_MARKUP = 2.2 / EQUILIBRIUM_RATIO

DIVIDEND_RATIO = 0.05
PRICE_VISCOSITY = 0.1

#   1.0 credit = 33 Wh * 1m = 0.33 MWh
DAILY_CRED_REQ: float = 1.0
DAILY_FOOD_REQ: float = 1.0

MACHINE_OP_COST = 0.0

POP_SAVINGS_RATIO = 0.5

POP_INIT_CRED = 2.0

NUM_JOB_TYPES = 2

JOB_EXEC = 0
JOB_DRONE = 1

DICT_POP = {
    JOB_EXEC: "Exec",
    JOB_DRONE: "Drone"
}

FIRM_INIT_CRED = 10.0

NUM_FIRM_TYPES = 2

FIRM_ENERGY = 0
FIRM_FOOD = 1

DICT_FIRM = {
    FIRM_ENERGY: "Fusion",
    FIRM_FOOD: "Food"
}

NUM_MARKETS = 2

MKT_LABOUR = 0
MKT_FOOD = 1

DICT_MKT = {
    MKT_LABOUR: "Labour",
    MKT_FOOD: "Food"
}

CRED_PER_PP = 10.0

DICT_PPC = {
    FIRM_ENERGY: 1.0/CRED_PER_PP,
    FIRM_FOOD: 0.1
}

DICT_VISC = {
    MKT_LABOUR: 1.0,
    MKT_FOOD: 1.0
}