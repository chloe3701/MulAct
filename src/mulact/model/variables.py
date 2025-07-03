import pyomo.environ as pyo


def declare_variables_flux(
    model: pyo.ConcreteModel,
    Prod: list[str],
    Cons: list[str],
    Time: list[int],
    Energie: list[str],
) -> None:
    # Quantitée d'énergie provenant de la source e consommée par le producteur i à temps t. En MWh
    # Q_energie[i,e,t]
    model.Q_energie = pyo.Var(Prod, Energie, Time, within=pyo.NonNegativeReals)

    # Quantitée d'énergie totale consommée par le producteur i à temps t. En MWh
    # Q_energie_total[i,t]
    model.Q_energie_total = pyo.Var(Prod, Time, within=pyo.NonNegativeReals)

    # Quantitée d'H2 produite par le producteur i à temps t. En kgH2
    # Q_H2_prod[i,t]
    model.Q_H2_prod = pyo.Var(Prod, Time, within=pyo.NonNegativeReals)

    # Quantitée d'H2 dans le stock du producteur i à temps t. En kgH2
    # Q_H2_stock[i,t]
    model.Q_H2_stock = pyo.Var(Prod, Time, within=pyo.NonNegativeReals)

    # Quantitée d'H2 dans le stock initial du producteur i. En kgH2
    # Q_H2_init_stock[i]
    model.Q_H2_init_stock = pyo.Var(Prod, within=pyo.NonNegativeReals)

    # Quantité d’H2 rentrant dans le stockage du producteur i à temps t. En kgH2
    # Q_H2_stock_in[i,t]
    model.Q_H2_stock_in = pyo.Var(Prod, Time, within=pyo.NonNegativeReals)

    # Quantité d’H2 sortant du stockage du producteur i à temps t. En kgH2
    # Q_H2_stock_out[i,t]
    model.Q_H2_stock_out = pyo.Var(Prod, Time, within=pyo.NonNegativeReals)

    # Quantité d’H2 vendue sur le marché par le producteur i à temps t (avant répartition entre les consommateurs). En kgH2
    # Q_H2_a_vendre[i,t]
    model.Q_H2_a_vendre = pyo.Var(Prod, Time, within=pyo.NonNegativeReals)

    # Quantité d’H2 vendue par le producteur i au consommateur j à temps t. En kgH2
    # Q_H2_vendu[i,j,t]
    model.Q_H2_vendu = pyo.Var(Prod, Cons, Time, within=pyo.NonNegativeReals)


def declare_variables_dimension(model: pyo.ConcreteModel, Prod: list[str]) -> None:
    # Taille de l'électrolyseur du producteur i. En MW
    # Taille_electrolyseur[i]
    model.Taille_electrolyseur = pyo.Var(Prod, within=pyo.NonNegativeReals)

    # Taille du stockage du producteur i. En kgH2
    # Taille_stockage[i]
    model.Taille_stockage = pyo.Var(Prod, within=pyo.NonNegativeReals)

    # Taille du captage de CO2 du producteur i. En kgCO2
    # Taille_captage[i]
    model.Taille_captage = pyo.Var(Prod, within=pyo.NonNegativeReals)


def declare_variables_eco(
    model: pyo.ConcreteModel, Prod: list[str], Cons: list[str], Time: list[int]
) -> None:
    """_summary_

    Args:
        model (pyo.ConcreteModel): _description_
        Prod (list[str]): _description_
        Cons (list[str]): _description_
        Time (list[int]): _description_
    """
    # Variables économiques

    # Prix total de l'énergie consommée par le producteur i. En EUR
    # P_energie_total[i]
    model.P_energie_total = pyo.Var(Prod, within=pyo.NonNegativeReals)

    # Coût d’investissement du producteur i pour son électrolyseur par heure. En EUR/h
    # P_CAPEX_Electrolyseur[i]
    model.P_CAPEX_Electrolyseur = pyo.Var(Prod, within=pyo.NonNegativeReals)

    # Coût d’investissement du producteur i pour son stockage par heure. En EUR/h
    # P_CAPEX_Stockage[i]
    model.P_CAPEX_Stockage = pyo.Var(Prod, within=pyo.NonNegativeReals)

    # Coût d’investissement du producteur i pour son système de captage d'émission CO2 par heure. En EUR/h
    # P_CAPEX_Captage[i]
    model.P_CAPEX_Captage = pyo.Var(Prod, within=pyo.NonNegativeReals)

    # Prix payé par le consommateur j au producteur i à temps t. En EUR
    # P_H2_vendu[i,j,t]
    model.P_H2_vendu = pyo.Var(Prod, Cons, Time, within=pyo.NonNegativeReals)


def declare_variables_environnement(
    model: pyo.ConcreteModel, Prod: list[str], Time: list[int]
) -> None:
    # Impact CO2 du producteur i à temps t. En kgCO2
    # Impact_prod[i,t]
    model.Impact_prod = pyo.Var(Prod, Time, within=pyo.NonNegativeReals)

    # Emissions de CO2 générés par le vaporeformage du producteur i à temps t. En kgCO2
    # Emission_vaporeformage[i,t]
    model.Emission_vaporeformage = pyo.Var(Prod, Time, within=pyo.NonNegativeReals)

    # Emissions de CO2 captées par le producteur via vaporéformage i à temps t. En kgCO2
    # Captage[i,t]
    model.Captage = pyo.Var(Prod, Time, within=pyo.NonNegativeReals)


def declare_variables(
    model: pyo.ConcreteModel,
    Prod: list[str],
    Cons: list[str],
    Time: list[int],
    Energie: list[str],
) -> None:
    # --------------------------------------------------#
    #               Variables de décision              #
    # --------------------------------------------------#
    declare_variables_flux(model, Prod, Cons, Time, Energie)
    declare_variables_dimension(model, Prod)
    declare_variables_eco(model, Prod, Cons, Time)
    declare_variables_environnement(model, Prod, Time)
