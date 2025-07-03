from .actors.consumer import declare_constraint_consumer
from .actors.prod_electrolyzer import declare_constraints_p_electrolyzer
from mulact.data.case_study import Actor
from mulact.data.case_study import Energy
import pyomo.environ as pyo


def declare_constraints(
    model: pyo.ConcreteModel,
    P_electrolyzer: list[str],
    P_smr: list[str],
    Cons: list[str],
    Energie: dict[str, Energy],
    Time: list[int],
    Actors: dict[str, Actor],
    Prix_vente_H2: dict[str, dict[str, float]],
    optim_CO2_heure: bool,
) -> None:
    Prod = P_electrolyzer + P_smr

    declare_constraint_consumer(
        model=model,
        Cons=Cons,
        Prod=Prod,
        Time=Time,
        Actors=Actors,
        Prix_vente_H2=Prix_vente_H2,
    )

    declare_constraints_p_electrolyzer(
        model=model,
        P_electrolyzer=P_electrolyzer,
        Cons=Cons,
        Actors=Actors,
        Energie=Energie,
        Time=Time,
        optim_CO2_heure=optim_CO2_heure,
        Prix_vente_H2=Prix_vente_H2,
    )