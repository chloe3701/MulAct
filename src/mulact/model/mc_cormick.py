import pyomo.environ as pyo
from mulact.data.case_study import Actor


def optim_mc_cormick(
    model: pyo.ConcreteModel,
    Prod: list[str],
    Cons: list[str],
    Actors: list[Actor],
    Time: list[int],
    optim_prix: bool,
) -> None:
    # /!\ Seulement si on utilise la relaxation linéaire de McCormick pour optimiser le prix
    if optim_prix:
        # Le prix n'est plus fixé, mais devient une variable d'optimisation
        # Prix de l'hydrogène entre le producteur i et le consommateur j. En EUR/kgH2
        # P_H2_contrat[i,j]
        model.P_H2_contrat = pyo.Var(Prod, Cons, within=pyo.NonNegativeReals)

        # Remove the constraints using a fixed price
        if hasattr(model, "C_cost_is_mass_times_price"):
            del model.C_cost_is_mass_times_price
        if hasattr(model, "C_prod_elec_15"):
            del model.C_prod_elec_15
        if hasattr(model, "C_prod_smr_8"):
            del model.C_prod_smr_8

        def C_cormick_1_rule(m, i, j, t):
            cons = Actors[j]
            return m.P_H2_vendu[i, j, t] <= m.Q_H2_vendu[i, j, t] * cons.pire_prix

        model.C_cormick_1 = pyo.Constraint(Prod, Cons, Time, rule=C_cormick_1_rule)

        def C_cormick_2_rule(m, i, j, t):
            cons = Actors[j]
            return m.P_H2_vendu[i, j, t] <= cons.demand_h2[t] * m.P_H2_contrat[i, j]

        model.C_cormick_2 = pyo.Constraint(Prod, Cons, Time, rule=C_cormick_2_rule)

        def C_cormick_3_rule(m, i, j, t):
            cons = Actors[j]
            return (
                m.P_H2_vendu[i, j, t]
                >= cons.pire_prix * m.Q_H2_vendu[i, j, t]
                + cons.demand_h2[t] * m.P_H2_contrat[i, j]
                - cons.pire_prix * cons.demand_h2[t]
            )

        model.C_cormick_3 = pyo.Constraint(Prod, Cons, Time, rule=C_cormick_3_rule)

        def C_cormick_4_rule(m, i, j, t):
            return m.P_H2_vendu[i, j, t] >= 0

        model.C_cormick_4 = pyo.Constraint(Prod, Cons, Time, rule=C_cormick_4_rule)
