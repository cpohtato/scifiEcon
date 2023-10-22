from .utils import *

#   Proportion of goods in market sold to be considered market-clearing
EQUILIBRIUM_RATIO = 0.9

#   Lowest markup to be applied to goods after accounting for equilibrium ratio
MIN_MARKUP = 1.2 / EQUILIBRIUM_RATIO

DIVIDEND_RATIO = 0.05
PRICE_VISCOSITY = 0.1

#   1.0 credit = 1 kWh
MONTHLY_CRED_REQ: float = 1.0
MONTHLY_FOOD_REQ: float = 1.0

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

FIRM_FUSION = 0
FIRM_FOOD = 1

DICT_FIRM = {
    FIRM_FUSION: "Fusion",
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
    FIRM_FUSION: 1.0/CRED_PER_PP,
    FIRM_FOOD: 0.1
}

DICT_VISC = {
    MKT_LABOUR: 1.0,
    MKT_FOOD: 1.0
}