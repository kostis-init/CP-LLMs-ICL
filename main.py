import argparse

from llms4cp.aplai_pipeline import run_aplai_pipeline
from llms4cp.nl4opt_pipeline import run_nl4opt
from llms4cp.puzzles_pipeline import run_lgp_pipeline


def pipeline():
    parser = argparse.ArgumentParser(description="Run CP modelling methods on datasets.")

    # Add arguments for the dataset and method
    parser.add_argument('--dataset', choices=['nl4opt', 'LGPs', 'APLAI'], required=True, help='Choose a dataset')
    parser.add_argument('--method', choices=['DIRECT', 'CPMPY', 'PSEUDO', 'NER'], required=True, help='Choose a method')

    # Parse the arguments
    args = parser.parse_args()

    # Run the chosen dataset with the chosen method
    if args.dataset == 'nl4opt':
        run_nl4opt(args.method)
    elif args.dataset == 'LGPs':
        run_lgp_pipeline(args.method)
    elif args.dataset == 'APLAI':
        run_aplai_pipeline(args.method)
    else:
        raise ValueError(f"Dataset {args.dataset} not supported")


if __name__ == '__main__':
    pipeline()
