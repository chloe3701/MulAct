import pyomo.environ as pyo
from mulact.data.case_study import Actor
from mulact.data.case_study import Energy


def declare_goal_p_electrolyzer(
    model: pyo.ConcreteModel,
    P_electrolyzer: list[str],
    Cons: list[str],
    Time: list[int],
) -> None:
    Time_horizon = len(Time)

    # /!\ si modification, ne pas oublier de la changer dans point_nadir.py
    def C_goal_p_electrolyzer_rule(m, i):
        cout_energie = m.P_energie_total[i]
        cout_CAPEX = (m.P_CAPEX_Electrolyseur[i] + m.P_CAPEX_Stockage[i]) * Time_horizon
        recettes = sum(m.P_H2_vendu[i, j, t] for t in Time for j in Cons)
        return m.fn_obj[i] == cout_energie + cout_CAPEX - recettes

    model.C_goal_p_electrolyzer = pyo.Constraint(
        P_electrolyzer, rule=C_goal_p_electrolyzer_rule
    )


# Contraintes flux physiques
def declare_constraints_p_electrolyzer_physical_flux(
    model: pyo.ConcreteModel,
    P_electrolyzer: list[str],
    Cons: list[str],
    Actors: dict[str, Actor],
    Time: list[int],
    Energie: dict[str, Energy],
) -> None:
    # Quantité d'énergie achetée par le producteur
    def C_prod_elec_1_rule(m, i, t):
        return m.Q_energie_total[i, t] == sum(
            m.Q_energie[i, e, t] for e in Energie.keys()
        )

    model.C_prod_elec_1 = pyo.Constraint(P_electrolyzer, Time, rule=C_prod_elec_1_rule)

    # Quantité d'H2 produite avec l'électricité achetée
    def C_prod_elec_2_rule(m, i, t):
        return (
            m.Q_H2_prod[i, t]
            == m.Q_energie_total[i, t]
            * Actors[i].internal_struct.electrolyzer.efficiency
        )

    model.C_prod_elec_2 = pyo.Constraint(P_electrolyzer, Time, rule=C_prod_elec_2_rule)

    # Contrainte de dimensionnement electrolyseur
    def C_prod_elec_3_rule(m, i, t):
        return m.Q_energie_total[i, t] <= m.Taille_electrolyseur[i]

    model.C_prod_elec_3 = pyo.Constraint(P_electrolyzer, Time, rule=C_prod_elec_3_rule)

    # Quantité d'H2 en stock
    def C_prod_elec_4_rule(m, i, t):
        if t == 0:
            return (
                m.Q_H2_stock[i, t]
                == m.Q_H2_init_stock[i] + m.Q_H2_stock_in[i, t] - m.Q_H2_stock_out[i, t]
            )
        else:
            return (
                m.Q_H2_stock[i, t]
                == m.Q_H2_stock[i, t - 1]
                + m.Q_H2_stock_in[i, t]
                - m.Q_H2_stock_out[i, t]
            )

    model.C_prod_elec_4 = pyo.Constraint(P_electrolyzer, Time, rule=C_prod_elec_4_rule)

    # Quantité initiale d'H2 en stock
    def C_prod_elec_5_rule(m, i):
        return m.Q_H2_init_stock[i] == 0.5 * m.Taille_stockage[i]

    model.C_prod_elec_5 = pyo.Constraint(P_electrolyzer, rule=C_prod_elec_5_rule)

    # Quantité finale d'H2 en stock
    def C_prod_elec_6_rule(m, i):
        return m.Q_H2_init_stock[i] == m.Q_H2_stock[i, Time[-1]]

    model.C_prod_elec_6 = pyo.Constraint(P_electrolyzer, rule=C_prod_elec_6_rule)

    # Quantité d'H2 à vendre
    def C_prod_elec_7_rule(m, i, t):
        return (
            m.Q_H2_a_vendre[i, t]
            == m.Q_H2_prod[i, t] - m.Q_H2_stock_in[i, t] + m.Q_H2_stock_out[i, t]
        )

    model.C_prod_elec_7 = pyo.Constraint(P_electrolyzer, Time, rule=C_prod_elec_7_rule)

    # Contrainte de dimensionnement stockage
    def C_prod_elec_8_rule(m, i, t):
        return m.Q_H2_stock[i, t] <= m.Taille_stockage[i]

    model.C_prod_elec_8 = pyo.Constraint(P_electrolyzer, Time, rule=C_prod_elec_8_rule)

    # Quantité d'H2 vendu
    def C_prod_elec_9_rule(m, i, t):
        return m.Q_H2_a_vendre[i, t] == sum(m.Q_H2_vendu[i, j, t] for j in Cons)

    model.C_prod_elec_9 = pyo.Constraint(P_electrolyzer, Time, rule=C_prod_elec_9_rule)

    # Taille max electrolyseur
    def C_prod_elec_10_rule(m, i):
        return (
            m.Taille_electrolyseur[i] <= Actors[i].internal_struct.electrolyzer.size_max
        )

    model.C_prod_elec_10 = pyo.Constraint(P_electrolyzer, rule=C_prod_elec_10_rule)

    # Taille max stockage
    def C_prod_elec_11_rule(m, i):
        return m.Taille_stockage[i] <= Actors[i].internal_struct.storage.size_max

    model.C_prod_elec_11 = pyo.Constraint(P_electrolyzer, rule=C_prod_elec_11_rule)


# def declare_constraints_p_electrolyzer_economic():

# def declare_constraints_p_electrolyzer_environmental():


def declare_constraints_p_electrolyzer(
    model: pyo.ConcreteModel,
    P_electrolyzer: list[str],
    Cons: list[str],
    Actors: dict[str, Actor],
    Energie: dict[str, Energy],
    Time: list[int],
    optim_CO2_heure: bool,
) -> None:
    declare_constraints_p_electrolyzer_physical_flux(
        model=model,
        P_electrolyzer=P_electrolyzer,
        Cons=Cons,
        Actors=Actors,
        Time=Time,
        Energie=Energie,
    )


#     # Contraintes économiques

#     # Cout de production d'H2 : Energie
#     def C_prod_elec_12_rule(m, i):
#         return m.P_energie_total[i] == sum(sum(m.Q_energie[i,e,t] * Prix_energie[e][t] for e in Energie) for t in Time)
#     model.C_prod_elec_12 = pyo.Constraint(P_electrolyzer, rule = C_prod_elec_12_rule)

#     # Cout de production : CAPEX par h
#     def C_prod_elec_13_rule(m, i):
#         return m.P_CAPEX_Electrolyseur[i] == m.Taille_electrolyseur[i] * CAPEX_t_electrolyseur[i]
#     model.C_prod_elec_13 = pyo.Constraint(P_electrolyzer, rule = C_prod_elec_13_rule)

#     def C_prod_elec_14_rule(m, i):
#         return m.P_CAPEX_Stockage[i] == m.Taille_stockage[i] * CAPEX_t_stockage[i]
#     model.C_prod_elec_14 = pyo.Constraint(P_electrolyzer, rule = C_prod_elec_14_rule)

#     # Si on n'optimise pas avec McCormick
#     # Prix vendu aux consommateurs (contrainte redondante avec la modélisation des consommateurs)
#     # Profit vente d'H2
#     if not optim_prix:
#         def C_prod_elec_15_rule(m, i, j, t):
#             return m.P_H2_vendu[i,j,t] == m.Q_H2_vendu[i,j,t] * m.Prix_vente_H2[i,j]
#         model.C_prod_elec_15 = pyo.Constraint(P_electrolyzer, Cons, Time, rule = C_prod_elec_15_rule)

#     # Contraintes environnement

#     # Impact carbone producteur
#     def C_prod_elec_16_rule(m, i, t):
#         return m.Impact_prod[i,t] == sum(m.Q_energie[i, e, t] * Impact_elec[e][t] for e in Electricite)
#     model.C_prod_elec_16 = pyo.Constraint(P_electrolyzer, Time, rule = C_prod_elec_16_rule)

#     # Contraintes d'emissions maximum
#     # Si contrainte horaire
#     if optim_CO2_heure:
#         def C_prod_elec_17_rule(m, i, t):
#             return m.Impact_prod[i, t] <= Impact_max[i] * m.Q_H2_prod[i, t]
#         model.C_prod_elec_17 = pyo.Constraint(P_electrolyzer, Time, rule = C_prod_elec_17_rule)
#     # Si contrainte en moyenne
#     else:
#         def C_prod_elec_17_rule(m, i):
#             return sum(m.Impact_prod[i, t] for t in Time) <= Impact_max[i] * sum(m.Q_H2_prod[i, t] for t in Time)
#         model.C_prod_elec_17 = pyo.Constraint(P_electrolyzer, rule = C_prod_elec_17_rule)

#     return model
