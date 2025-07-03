from mulact.data.case_study import declare_study
from mulact.model.pipeline import init_model


def main():
    case_study = declare_study(time_horizon=1)
    model = init_model(case_study)


if __name__ == "__main__":
    main()
    print("Done")
