import csv
from dataclasses import dataclass
import mulact.param_config as param_config


# fichier de données csv
fichier_données = r"C:\Users\CD282263\mulact\src\mulact\data\Stage_dataseries.csv"

# Debut des données 106
debut_data = 0

# Energie
Energie = ["Elec_reseau", "PV", "Gaz"]
Electricite = ["Elec_reseau", "PV"]

# Producteurs
P_electrolyseur = ["P1_electrolyse(avec PV)", "P2_electrolyse"]
P_SMR = ["P3_SMR"]
Prod = P_electrolyseur + P_SMR

# Consommateurs
Cons = ["C1_industriel", "C2_mobilite"]

# Acteurs
Acteurs = Prod + Cons


def read_data(csv_file: str, time_horizon: int):
    Production_elec = {e: [] for e in Electricite}
    Impact_elec = {e: [] for e in Electricite}
    Prix_energie = {e: [] for e in Energie}
    Demande_H2 = {c: [] for c in Cons}

    with open(csv_file, "r") as file:
        reader = csv.reader(file, delimiter=";")

        # Récupération des index
        index = {}
        headers = next(reader)
        for i, header in enumerate(headers):
            index[header] = i

        for e in Electricite:
            if e not in index:
                raise ValueError(f"'{e}' n'existe pas dans le fichier CSV.")
            Production_elec[e] = []
            if e + "_impact" not in index:
                raise ValueError(f"'{e}'_impact n'existe pas dans le fichier CSV.")
            Impact_elec[e] = []
        for e in Energie:
            if e + "_prix" not in index:
                raise ValueError(f"'{e}'_prix n'existe pas dans le fichier CSV.")
            Prix_energie[e] = []
        for c in Cons:
            if c not in index:
                raise ValueError(f"'{c}'_prix n'existe pas dans le fichier CSV.")
            Demande_H2[c] = []

        # Passer les lignes d'information
        for _ in range(3):
            next(reader, None)

        # Aller au début des données souhaitées
        for _ in range(debut_data):
            next(reader, None)

        # Complétion des données
        for t, row in enumerate(reader):
            if t >= time_horizon:
                break
            for e in Electricite:
                Production_elec[e].append(float(row[index[e]]))
                Impact_elec[e].append(float(row[index[e + "_impact"]]))
            for e in Energie:
                Prix_energie[e].append(float(row[index[e + "_prix"]]))
            for c in Cons:
                Demande_H2[c].append(round(float(row[index[c]]), 2))
    return Production_elec, Impact_elec, Prix_energie, Demande_H2


# Production_elec : Stock disponible d'électricité - en MWh
# Impact_elec : Impact carbone de l'électricité - en kgCo2/MWh
# Prix_energie : Prix de l'énergie - en €/MWh
# Demande_H2 : Demande d'H2 du client j
# Production_elec, Impact_elec, Prix_energie, Demande_H2 = read_data(
#     fichier_données, Time_horizon
# )


@dataclass
class Electrolyzer:
    # Rendement electrolyseur - en kgH2/MWh
    efficiency: float = 20
    # Taille max de l'electrolyseur - en MW
    size_max: float = 10
    # CAPEX - en EUR/MW
    capex: float = 6e5
    # duree de vie - en années
    lifetime: float = 10

    # CAPEX - en EUR/MW/h
    @property
    def hourly_capex(self):
        return self.capex / (8760 * self.lifetime)


@dataclass
class Storage:
    # Taille max du stockage - en kgH2
    size_max: float = 1e3
    # CAPEX stockage - en EUR/kgH2
    capex: float = 1e3
    # duree de vie stockage - en années
    lifetime: float = 10

    # CAPEX - en EUR/kgH2/h
    @property
    def hourly_capex(self):
        return self.capex / (8760 * self.lifetime)


@dataclass
class SteamMethaneReformer:
    # Rendement vaporeformage - en kgH2/MWh
    efficiency: float = 20
    # Taille vaporeformeur - en MW
    size: float = 1e10
    # Impact vaporeformage - en kgCO2/kgH2
    impact: float = 10


@dataclass
class CCS:
    # Taille max du captage - en kgCO2
    size_max: float = 1e3
    # CAPEX captage - en EUR/kgCO2
    capex: float = 4_800
    # duree de vie captage - en années
    lifetime: float = 10

    # CAPEX - en EUR/kgCO2/h
    @property
    def hourly_capex(self):
        return self.capex / (8760 * self.lifetime)
