import pyomo.environ as pyo
from mulact.data.case_study import Actor


def declare_goal_consumer(
    model: pyo.ConcreteModel,
    Prod: list[str],
    Cons: list[str],
    Time: list[int],
    Actors: dict[str, Actor],
) -> None:
    # /!\ si modification, ne pas oublier de la changer dans point_nadir.py
    # Valeur de la fonction objective des consommateur:
    # prix au kilo de l'H2
    def C_goal_consumer_rule(m, j):
        prix_total = sum(model.P_H2_vendu[i, j, t] for t in Time for i in Prod)
        demand_j = Actors[j].internal_struct.demand_h2
        demande_tot_cons = sum(demand_j[t] for t in Time)

        if demande_tot_cons == 0:
            return m.goal[j] == 0
        else:
            return m.goal[j] == prix_total / demande_tot_cons

    model.C_goal_consumer = pyo.Constraint(Cons, rule=C_goal_consumer_rule)


def declare_constraint_consumer(
    model: pyo.ConcreteModel,
    Cons: list[str],
    Prod: list[str],
    Time: list[int],
    Actors: dict[str, Actor],
    Prix_vente_H2: dict[str, dict[str, float]],
) -> None:
    # La demande est satisfaite
    def C_load_satisfaction_rule(m, j, t):
        return (
            sum(m.Q_H2_vendu[i, j, t] for i in Prod)
            == Actors[j].internal_struct.demand_h2[t]
        )

    model.C_load_satisfaction = pyo.Constraint(
        Cons, Time, rule=C_load_satisfaction_rule
    )

    # Prix payé aux producteur (contrainte redondante avec la modélisation des producteurs)
    def C_cost_is_mass_times_price_rule(m, i, j, t):
        return m.P_H2_vendu[i, j, t] == m.Q_H2_vendu[i, j, t] * Prix_vente_H2[i][j]

    model.C_cost_is_mass_times_price = pyo.Constraint(
        Prod, Cons, Time, rule=C_cost_is_mass_times_price_rule
    )
