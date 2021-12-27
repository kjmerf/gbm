import argparse
import csv
from datetime import datetime, timezone
import json

def json_to_csv(input, output):
    """Write input JSON file to output CSV file"""

    with open(input) as i:
        data = json.load(i)

    with open(output, "w") as o:
        writer = csv.writer(o)
        writer.writerow(["unixtime", "dt", "price"])
        for row in data["prices"]:
            unixtime = int(str(row[0])[:-3])
            dt = datetime.fromtimestamp(unixtime, tz=timezone.utc)
            writer.writerow([row[0], dt, row[1]])

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="The JSON file containing historical data")
    parser.add_argument("output", help="The CSV file to which to write the historical data")
    args = parser.parse_args()

    json_to_csv(args.input, args.output)
