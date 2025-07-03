import pyomo.environ as pyo
from mulact.data.case_study import CaseStudy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def individual_optimisation(model: pyo.ConcreteModel, study: CaseStudy) -> None:
    name_prod = study.network.name_p_electrolyzer + study.network.name_p_smr
    name_cons = study.network.name_cons
    actors = study.network.actors
    expr = sum(model.goal[a] for a in name_prod) + sum(
        model.goal[a]
        * sum(actors[a].internal_struct.demand_h2[t] for t in range(study.time))
        for a in name_cons
    )
    model.objective = pyo.Objective(expr=expr, sense=pyo.minimize)
    solver = pyo.SolverFactory("cplex")
    solver.solve(model, tee=False)

    for a in name_prod + name_cons:
        result = pyo.value(model.goal[a])
        logger.info(f"Objectif {a}: {result}")
