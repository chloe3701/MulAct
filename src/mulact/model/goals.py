import pyomo.environ as pyo
from mulact.data.case_study import Actor
from .actors.consumer import declare_goal_consumer
from .actors.prod_electrolyzer import declare_goal_p_electrolyzer
from .actors.prod_smr import declare_goal_p_smr


def declare_goal(
    model: pyo.ConcreteModel,
    P_electrolyzer: list[str],
    P_SMR: list[str],
    Cons: list[str],
    Time: list[int],
    Actors: dict[str, Actor],
) -> None:
    # Acteurs
    Prod = P_electrolyzer + P_SMR
    Actors_names = Prod + Cons

    # Variables représentant la valeur de la fonction objective si optimisation individuelle
    model.goal = pyo.Var(Actors_names, within=pyo.Reals)

    declare_goal_consumer(model=model, Prod=Prod, Cons=Cons, Time=Time, Actors=Actors)
    declare_goal_p_electrolyzer(model, P_electrolyzer, Cons, Time)
    declare_goal_p_smr(model, P_SMR, Cons, Time)
