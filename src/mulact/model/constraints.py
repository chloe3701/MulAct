from .actors.consumer import declare_constraint_consumer
from mulact.data.case_study import Actor
import pyomo.environ as pyo


def declare_constraints(
    model: pyo.ConcreteModel,
    Prod: list[str],
    Cons: list[str],
    Time: list[int],
    Actors: dict[str,Actor],
    Prix_vente_H2: dict[str, dict[str, float]],
) -> None:
    declare_constraint_consumer(
        model=model,
        Cons=Cons,
        Prod=Prod,
        Time=Time,
        Actors=Actors,
        Prix_vente_H2=Prix_vente_H2)
