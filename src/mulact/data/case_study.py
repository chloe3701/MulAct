from dataclasses import dataclass
from .pre_processing import Electrolyzer
from .pre_processing import Storage
from .pre_processing import SteamMethaneReformer
from .pre_processing import CCS
from .pre_processing import read_data

from mulact.param_config import Prix_vente_H2
from mulact.param_config import optim_prix
from mulact.param_config import emission_CO2_heure
from mulact.param_config import data_csv


@dataclass
class Energy:
    name: str
    price: list[float]
    available_quantity: list[float] | None
    # Dans le cas du smr, l'impact n'est pas à l'achat du gaz mais à son utilisation
    impact: list[float] | None


@dataclass
class Producer:
    energy_sources: list[str]
    impact_max: float


@dataclass
class ProducteurElectrolyzer(Producer):
    electrolyzer: Electrolyzer
    storage: Storage


@dataclass
class ProducteurSMR(Producer):
    SMR: SteamMethaneReformer
    ccs: CCS


@dataclass
class Consumer:
    pire_prix: float
    meilleur_prix: float
    demand_h2: list[float]


@dataclass
class Actor:
    name: str
    internal_struct: Producer | Consumer


@dataclass
class Network:
    actors: dict[str, Actor]
    name_p_electrolyzer: list[str]
    name_p_smr: list[str]
    name_cons: list[str]

    energies: dict[str, Energy]
    name_energy: list[str]
    name_electricity: list[str]

    h2_market_prices: dict[str, dict[str, float]]


def declare_network(time_horizon: int) -> Network:
    # Modélisation du scénario :
    #   - 2 Producteur via électrolyse:
    #       P1 : Source d'énergie PV + réseau
    #       P2 : Source d'énergie réseau
    #   => Stockage et électrolyseur à dimensionner
    #   - 1 Producteur via vaporéformage
    #   => Captage d'émission CO2 à dimensionner
    #   - 2 Consommateurs d'H2

    Production_elec, Impact_elec, Prix_energie, Demande_H2 = read_data(
        data_csv, time_horizon
    )

    actors = {}
    # Producteurs via electrolyse avec pv
    actors["P1_electrolyse(avec PV)"] = Actor(
        name="P1_electrolyse(avec PV)",
        internal_struct=ProducteurElectrolyzer(
            energy_sources=["Elec_reseau", "PV"],
            impact_max=3.5,
            electrolyzer=Electrolyzer(),
            storage=Storage(),
        ),
    )
    # Producteurs via electrolyse sans pv
    actors["P2_electrolyse"] = Actor(
        name="P2_electrolyse",
        internal_struct=ProducteurElectrolyzer(
            energy_sources=["Elec_reseau"],
            impact_max=3.5,
            electrolyzer=Electrolyzer(),
            storage=Storage(),
        ),
    )
    # Producteurs via smr
    actors["P3_SMR"] = Actor(
        name="P3_SMR",
        internal_struct=ProducteurSMR(
            energy_sources=["Gaz"],
            impact_max=3.5,
            SMR=SteamMethaneReformer(),
            ccs=CCS(),
        ),
    )

    # Consommateurs
    # Prix acceptés par le consommateur : prix cible et prix max
    actors["C1_industriel"] = Actor(
        name="C1_industriel",
        internal_struct=Consumer(
            pire_prix=10, meilleur_prix=0, demand_h2=Demande_H2["C1_industriel"]
        ),
    )
    actors["C2_mobilite"] = Actor(
        name="C2_mobilite",
        internal_struct=Consumer(
            pire_prix=20, meilleur_prix=0, demand_h2=Demande_H2["C2_mobilite"]
        ),
    )

    # Déclaration des énergies
    energies = {}
    for e in ["Elec_reseau", "PV", "Gaz"]:
        if e in ["Elec_reseau", "PV"]:
            energies[e] = Energy(e, Prix_energie[e], Production_elec[e], Impact_elec[e])
        else:
            energies[e] = Energy(e, Prix_energie[e], None, None)

    case_study_network = Network(
        actors=actors,
        name_p_electrolyzer=["P1_electrolyse(avec PV)", "P2_electrolyse"],
        name_p_smr=["P3_SMR"],
        name_cons=["C1_industriel", "C2_mobilite"],
        energies=energies,
        name_energy=["Elec_reseau", "PV", "Gaz"],
        name_electricity=["Elec_reseau", "PV"],
        h2_market_prices=Prix_vente_H2,
    )
    return case_study_network


@dataclass
class CaseStudy:
    time: int
    network: Network
    optim_price: bool = False
    optim_CO2_heure: bool = True


def declare_study(time_horizon) -> CaseStudy:
    case_study = CaseStudy(
        time=time_horizon,
        network=declare_network(time_horizon),
        optim_price=optim_prix,
        optim_CO2_heure=emission_CO2_heure,
    )
    return case_study
