import csv
from dataclasses import dataclass
import mulact.config as config


# fichier de données csv
fichier_données = r"C:\Users\CD282263\mulact\src\mulact\data\Stage_dataseries.csv"

# Debut des données 106
debut_data = 0
# Horizon de temps en heure max = 8736
Time_horizon = config.Time_horizon
# Energie
Energie = ["Elec_reseau", "PV", "Gaz"]
Electricite = ["Elec_reseau", "PV"]

# Producteurs
P_electrolyseur = ["P1_electrolyse(avec PV)", "P2_electrolyse"]
P_SMR = ["P3_SMR"]
Prod =  P_electrolyseur + P_SMR

# Consommateurs
Cons = ["C1_industriel", "C2_mobilite"]

# Acteurs
Acteurs = Prod + Cons

# Time
Time = [i for i in range(Time_horizon)]





def read_data(csv_file,Time_horizon):
    Production_elec = {e: [] for e in Electricite}
    Impact_elec = {e: [] for e in Electricite} 
    Prix_energie = {e: [] for e in Energie}
    Demande_H2 = {c: [] for c in Cons}

    with open(csv_file, 'r') as file:
        reader = csv.reader(file, delimiter=';')

        # Récupération des index
        index = {}
        headers = next(reader)
        for i, header in enumerate(headers):
            index[header] = i
        
        for e in Electricite:
            if e not in index:
                raise ValueError(f"'{e}' n'existe pas dans le fichier CSV.")
            Production_elec[e] = []
            if e+"_impact" not in index:
                raise ValueError(f"'{e}'_impact n'existe pas dans le fichier CSV.")
            Impact_elec[e] = []
        for e in Energie:
            if e+"_prix" not in index:
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
            if t >= Time_horizon:
                break
            for e in Electricite:
                Production_elec[e].append(float(row[index[e]]))
                Impact_elec[e].append(float(row[index[e+"_impact"]]))
            for e in Energie:
                Prix_energie[e].append(float(row[index[e+"_prix"]]))
            for c in Cons:
                Demande_H2[c].append(round(float(row[index[c]]),2))   
    return Production_elec, Impact_elec, Prix_energie, Demande_H2


# Production_elec : Stock disponible d'électricité - en MWh
# Impact_elec : Impact carbone de l'électricité - en kgCo2/MWh
# Prix_energie : Prix de l'énergie - en €/MWh
# Demande_H2 : Demande d'H2 du client j
Production_elec, Impact_elec, Prix_energie, Demande_H2 = read_data(fichier_données, Time_horizon)


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
    
@dataclass
class ProducteurElectrolyzer:
    name: str
    electrolyzer: Electrolyzer
    storage: Storage

@dataclass
class ProducteurSMR:
    name: str
    SMR: SteamMethaneReformer
    ccs: CCS


# ----------------------------#
#    Données producteurs      #
# ----------------------------#

# Impact Co2 maximal autorisé - en kgCO2 / kgH2
Impact_max = {p: 3.5 for p in Prod}

# ----------------------------#
#    Données consommateurs    #
# ----------------------------#
# Prix de vente - en €/kgH2
Prix_vente_H2 = config.Prix_vente_H2

# Demande totale
Demande_totale = sum(sum(values) for values in Demande_H2.values())
# Prix acceptés par le consommateur : prix cible et prix max
Pire_prix = {"C1_industriel":10, "C2_mobilite":20}

Meilleur_prix = {"C1_industriel":0, "C2_mobilite":0}

def main(P_electrolyseur: list[str], P_SMR: list[str]) -> int:
    """_summary_

    Args:
        P_electrolyseur (list[str]): _description_
        P_SMR (list[str]): _description_

    Returns:
        int: _description_
    """
    producers = {
        ely_prod : ProducteurElectrolyzer(
            name=ely_prod,
            electrolyzer = Electrolyzer(),
            storage = Storage(),
        )
        for ely_prod in P_electrolyseur
        }

    for smr_prod in P_SMR:
        producers[smr_prod] = ProducteurSMR(
            name = smr_prod,
            SMR= SteamMethaneReformer(),
            ccs=CCS()
        )

    print(f"{producers}")

    return 1

if __name__=="__main__":
    main()

