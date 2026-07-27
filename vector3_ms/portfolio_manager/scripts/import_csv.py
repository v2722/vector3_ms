import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from app.services.csv_service import import_assets_csv, import_transactions_csv

def main():
    parser = argparse.ArgumentParser(description="Import CSV files into portfolio manager")
    parser.add_argument("type", choices=["assets", "transactions"], help="Type of data to import")
    parser.add_argument("file", help="CSV file path")
    parser.add_argument("--portfolio-id", type=int, help="Portfolio ID (required for transactions)")

    args = parser.parse_args()

    with open(args.file, "r") as f:
        csv_content = f.read()

    if args.type == "assets":
        result = import_assets_csv(csv_content)
        print(f"✓ {result['imported']} assets imported successfully")
    elif args.type == "transactions":
        if not args.portfolio_id:
            print("Error: --portfolio-id is required for transaction import")
            sys.exit(1)
        result = import_transactions_csv(csv_content, args.portfolio_id)
        print(f"✓ {result['imported']} transactions imported to portfolio {args.portfolio_id}")

if __name__ == "__main__":
    main()
