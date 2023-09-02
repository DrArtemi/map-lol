import argparse
from pathlib import Path
from bayes_parser import BayesParser


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="Bayes folder path to load", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    path = Path(args.path)
    if not path.exists():
        raise FileNotFoundError(f"{path}")
    
    bp = BayesParser(path)
    bp.get_teams_stats()
