from mulact.data.case_study import declare_study
from mulact.model.pipeline import init_model
from mulact.param_config import Time_horizon


def main():
    case_study = declare_study(time_horizon=Time_horizon)
    model = init_model(case_study)


if __name__ == "__main__":
    main()
    print("Done")
