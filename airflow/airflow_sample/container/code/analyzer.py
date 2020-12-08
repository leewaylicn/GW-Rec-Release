import argparse
import time
import distutils.util

def get_args():
    """"""
    parser = argparse.ArgumentParser(
        description="Portfolio Analyzer",
        epilog="Analyzes a user's financial portfolio for a given year"
    )

    parser.add_argument('-y', action="store", required=True, help='Year to analyze', type=str)

    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    year = args.y
    
    print("Importing user's portfolio...")
    time.sleep(5)

    print("Import complete...")

    print("Analyzing portfolio for year:", year)
    time.sleep(10)
    
    print("Preparing results")
    time.sleep(5)

    print("Exporting results...")
    time.sleep(5)
    print("Results for year", year, "exported to database.")==
