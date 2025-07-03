import pyomo.environ as pyo
from .actors.consumer import declare_goal_consumer
from .actors.prod_electrolyzer import declare_goal_p_electrolyzer


def declare_goal(
    model: pyo.ConcreteModel,
    P_electrolyzer: list[str],
    P_SMR: list[str],
    Cons: list[str],
    Time: list[int],
    Demand_H2: dict[str, list[float]],
) -> None:
    # Acteurs
    Prod = P_electrolyzer + P_SMR
    Actors = Prod + Cons

    # Variables représentant la valeur de la fonction objective si optimisation individuelle
    model.goal = pyo.Var(Actors, within=pyo.Reals)

    declare_goal_consumer(model, Prod, Cons, Time, Demand_H2)
    declare_goal_p_electrolyzer(model, P_electrolyzer, Cons, Time)
