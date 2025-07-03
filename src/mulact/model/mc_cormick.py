import pyomo.environ as pyo


def optim_mc_cormick(
    model: pyo.ConcreteModel, Prod: list[str], Cons: list[str], optim_prix: bool
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
