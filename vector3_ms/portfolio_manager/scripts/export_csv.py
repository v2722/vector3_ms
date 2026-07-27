import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from datetime import datetime
from app.services.csv_service import (
    export_holdings_csv, export_transactions_csv, export_performance_csv
)

def main():
    parser = argparse.ArgumentParser(description="Export portfolio data to CSV files")
    parser.add_argument("type", choices=["holdings", "transactions", "performance"], help="Type of data to export")
    parser.add_argument("portfolio_id", type=int, help="Portfolio ID")
    parser.add_argument("--output", help="Output file path (default: auto-generated)")

    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"{args.type}_{args.portfolio_id}_{timestamp}.csv"
    output_file = args.output or default_filename

    if args.type == "holdings":
        csv_data = export_holdings_csv(args.portfolio_id)
    elif args.type == "transactions":
        csv_data = export_transactions_csv(args.portfolio_id)
    elif args.type == "performance":
        csv_data = export_performance_csv(args.portfolio_id)

    with open(output_file, "w") as f:
        f.write(csv_data)

    print(f"✓ {args.type.capitalize()} exported to {output_file}")

if __name__ == "__main__":
    main()
