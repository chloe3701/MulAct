import pyomo.environ as pyo
from .variables import declare_variables
from mulact.data.case_study import CaseStudy

# from mulact.model.variable
from .constraints import declare_constraints
from .goals import declare_goal
from .mc_cormick import optim_mc_cormick


def init_model(case_study: CaseStudy) -> pyo.ConcreteModel:
    network = case_study.network

    # list[str]
    Prod = network.name_p_electrolyzer + case_study.network.name_p_smr
    Cons = network.name_cons
    Energy = network.name_energy

    # list[int]
    Time = [i for i in range(case_study.time)]

    # dict[str,Actor]
    Actors = network.actors

    model = pyo.ConcreteModel()

    # Declaration des variables du model
    declare_variables(model=model, Prod=Prod, Cons=Cons, Time=Time, Energie=Energy)

    # Declaration des contraintes du model
    declare_constraints(
        model=model,
        Cons=Cons,
        Prod=Prod,
        Time=Time,
        Actors=Actors,
        Prix_vente_H2=network.h2_market_prices,
    )

    declare_goal(
        model=model,
        P_electrolyzer=network.name_p_electrolyzer,
        P_SMR=network.name_p_smr,
        Cons=network.name_cons,
        Time=Time,
        Actors=Actors,
    )

    # optim_mc_cormick(model, optim_price)
