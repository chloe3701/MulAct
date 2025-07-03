import pyomo.environ as pyo
import logging
from .variables import declare_variables
from mulact.data.case_study import CaseStudy

# from mulact.model.variable
from .constraints import declare_constraints
from .goals import declare_goal
from .mc_cormick import optim_mc_cormick

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def init_model(case_study: CaseStudy) -> pyo.ConcreteModel:
    network = case_study.network

    # list[str]
    Prod_name = network.name_p_electrolyzer + case_study.network.name_p_smr
    Cons_name = network.name_cons
    Energy_name = network.name_energy

    # list[int]
    Time = [i for i in range(case_study.time)]

    # dict[str,Actor]
    Actors = network.actors
    # dict[str,Energy]
    Energy = network.energies

    model = pyo.ConcreteModel()

    # Declaration des variables du model
    declare_variables(
        model=model, Prod=Prod_name, Cons=Cons_name, Time=Time, Energie=Energy_name
    )

    # Declaration des contraintes du model
    declare_constraints(
        model=model,
        Cons=Cons_name,
        P_electrolyzer=network.name_p_electrolyzer,
        P_smr=network.name_p_smr,
        Energie=Energy,
        Time=Time,
        Actors=Actors,
        Prix_vente_H2=network.h2_market_prices,
        optim_CO2_heure=case_study.optim_CO2_heure,
    )

    declare_goal(
        model=model,
        P_electrolyzer=network.name_p_electrolyzer,
        P_SMR=network.name_p_smr,
        Cons=network.name_cons,
        Time=Time,
        Actors=Actors,
    )
    optim_mc_cormick(model, Prod_name, Cons_name, Actors, Time, case_study.optim_price)

    Nb_var = sum(1 for _ in model.component_data_objects(pyo.Var))
    Nb_contr = sum(1 for _ in model.component_data_objects(pyo.Constraint))
    logger.info(f"Nombre de variables : {Nb_var}")
    logger.info(f"Nombre de contraintes : {Nb_contr}")

    return model
