import pyomo.environ as pyo
from mulact.data.case_study import Actor
from mulact.data.case_study import Energy


def declare_goal_p_smr(
    model: pyo.ConcreteModel,
    P_smr: list[str],
    Cons: list[str],
    Time: list[int],
) -> None:
    Time_horizon = len(Time)

    # /!\ si modification, ne pas oublier de la changer dans point_nadir.py
    def C_goal_p_smr_rule(m, i):
        cout_energie = m.P_energie_total[i]
        cout_CAPEX = m.P_CAPEX_Captage[i] * Time_horizon
        recettes = sum(model.P_H2_vendu[i,j,t] for j in Cons for t in Time)
        return m.goal[i] == cout_energie + cout_CAPEX - recettes
    model.C_goal_p_smr = pyo.Constraint(P_smr, rule = C_goal_p_smr_rule)



# Contraintes flux physiques
def declare_constraints_p_smr_physical_flux(
    model: pyo.ConcreteModel,
    P_smr: list[str],
    Cons: list[str],
    Actors: dict[str, Actor],
    Time: list[int],
) -> None:

    # Quantité d'énergie achetée par le producteur
    def C_prod_smr_0_rule(m, i, t):
        return m.Q_energie_total[i,t] == sum(m.Q_energie[i,e,t] for e in Actors[i].internal_struct.energy_sources)
    model.C_prod_smr_0 = pyo.Constraint(P_smr, Time, rule = C_prod_smr_0_rule)

    # Quantité d'H2 produite avec le gaz acheté
    def C_prod_smr_1_rule(m, i, t):
        return m.Q_H2_prod[i,t] == m.Q_energie_total[i,t] * Actors[i].internal_struct.SMR.efficiency
    model.C_prod_smr_1 = pyo.Constraint(P_smr, Time, rule = C_prod_smr_1_rule)

    # Quantité d'H2 vendu
    def C_prod_smr_1bis_rule(m, i, t):
        return m.Q_H2_a_vendre[i,t] == m.Q_H2_prod[i,t]
    model.C_prod_smr_1bis = pyo.Constraint(P_smr, Time, rule = C_prod_smr_1bis_rule)

    # Contrainte de dimensionnement electrolyseur
    def C_prod_smr_2_rule(m, i, t):
        return m.Q_energie_total[i,t] <= Actors[i].internal_struct.SMR.size
    model.C_prod_smr_2 = pyo.Constraint(P_smr, Time, rule = C_prod_smr_2_rule)

    # Quantité d'H2 vendu
    def C_prod_smr_3_rule(m, i, t):
        return m.Q_H2_prod[i,t] == sum(m.Q_H2_vendu[i,j,t] for j in Cons)
    model.C_prod_smr_3 = pyo.Constraint(P_smr, Time, rule = C_prod_smr_3_rule)

    # Contrainte de dimensionnement système de capture CO2
    def C_prod_smr_4_rule(m, i, t):
        return m.Captage[i,t] <= m.Taille_captage[i]
    model.C_prod_smr_4 = pyo.Constraint(P_smr, Time, rule = C_prod_smr_4_rule)

    # Taille max captage
    def C_prod_smr_5_rule(m, i):
        return m.Taille_captage[i] <= Actors[i].internal_struct.ccs.size_max
    model.C_prod_smr_5 = pyo.Constraint(P_smr, rule = C_prod_smr_5_rule)


def declare_constraints_p_smr_economic(
    model: pyo.ConcreteModel,
    P_smr: list[str],
    Cons: list[str],
    Energie: dict[str, Energy],
    Actors: dict[str, Actor],
    Time: list[int],
    Prix_vente_H2: dict[str, dict[str, float]],
) -> None:
# Cout de production d'H2 : Energie
    def C_prod_smr_6_rule(m, i):
        energy_used = Actors[i].internal_struct.energy_sources
        return m.P_energie_total[i] == sum(
            sum(m.Q_energie[i, e, t] * Energie[e].price[t] for e in energy_used)
            for t in Time
        )
    model.C_prod_smr_6 = pyo.Constraint(P_smr, rule = C_prod_smr_6_rule)

    # Cout de production : CAPEX par heure
    def C_prod_smr_7_rule(m, i):
        capex_t_captage = Actors[i].internal_struct.ccs.hourly_capex
        return m.P_CAPEX_Captage[i] == m.Taille_captage[i] * capex_t_captage
    model.C_prod_smr_7 = pyo.Constraint(P_smr, rule = C_prod_smr_7_rule)    

    # Prix vendu aux consommateurs (contrainte redondante avec la modélisation des consommateurs)
    def C_prod_smr_8_rule(m, i, j, t):
        return m.P_H2_vendu[i, j, t] == m.Q_H2_vendu[i,j,t] * Prix_vente_H2[i][j]
    model.C_prod_smr_8 = pyo.Constraint(P_smr, Cons, Time, rule = C_prod_smr_8_rule)

def declare_constraints_p_smr_environmental(
    model: pyo.ConcreteModel,
    P_smr: list[str],
    Actors: dict[str, Actor],
    Time: list[int],
    optim_CO2_heure: bool,
) -> None:
# Emissions de CO2 liés au vaporéformage
    def C_prod_smr_9_rule(m, i, t):
        Impact_vaporeformage = Actors[i].internal_struct.SMR.impact
        return m.Emission_vaporeformage[i,t] == m.Q_H2_prod[i, t] * Impact_vaporeformage
    model.C_prod_smr_9 = pyo.Constraint(P_smr, Time, rule = C_prod_smr_9_rule)

    # Impact carbone producteur
    def C_prod_smr_10_rule(m, i, t):
        return m.Impact_prod[i,t] == m.Emission_vaporeformage[i,t] - m.Captage[i,t]
    model.C_prod_smr_10 = pyo.Constraint(P_smr, Time, rule = C_prod_smr_10_rule)

    # Contraintes d'emissions maximum
    # Si contrainte horaire
    if optim_CO2_heure:
        def C_prod_smr_11_rule(m, i, t):
            return m.Impact_prod[i, t] <= Actors[i].internal_struct.impact_max * m.Q_H2_prod[i, t]
        model.C_prod_smr_11 = pyo.Constraint(P_smr, Time, rule = C_prod_smr_11_rule)
     # Si contrainte en moyenne
    else:
        def C_prod_smr_11_rule(m, i):
            return sum(m.Impact_prod[i, t] for t in Time) <= Actors[i].internal_struct.impact_max * sum(m.Q_H2_prod[i, t] for t in Time)
        model.C_prod_smr_11 = pyo.Constraint(P_smr, rule = C_prod_smr_11_rule)

def declare_constraints_p_smr(
    model: pyo.ConcreteModel,
    P_smr: list[str],
    Cons: list[str],
    Actors: dict[str, Actor],
    Energie: dict[str, Energy],
    Time: list[int],
    Prix_vente_H2: dict[str, dict[str, float]],
    optim_CO2_heure: bool,
) -> None:
    declare_constraints_p_smr_physical_flux(
        model=model,
        P_smr=P_smr,
        Cons=Cons,
        Actors=Actors,
        Time=Time,
    )

    declare_constraints_p_smr_economic(
        model=model,
        P_smr=P_smr,
        Cons=Cons,
        Energie=Energie,
        Actors=Actors,
        Time=Time,
        Prix_vente_H2=Prix_vente_H2,
    )

    declare_constraints_p_smr_environmental(
        model=model,
        P_smr=P_smr,
        Actors=Actors,
        Time=Time,
        optim_CO2_heure=optim_CO2_heure,
    )