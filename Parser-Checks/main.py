import os
import sys
import csv
import time
import json
from utils import get_files, calculate_price, calculate_google_maps_price, parse, get_coordinates, extract_file_date
from colr import Colr as C
import colorlog

# Logging
handler = colorlog.StreamHandler()
logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
handler.setFormatter(colorlog.ColoredFormatter(
    '%(red)s%(levelname)s:%(name)s:%(message)s'))

# Main


def main(inputs, out):
    with open(inputs, "r") as f:
        files = [json.loads(line.strip()) for line in f if line.strip()]

    cost_of_operation = calculate_google_maps_price(len(files))

    print("Cost of operation:", C(
        f"${cost_of_operation}", fore="red", style="bright"))

    print("Do you want to continue?", C("(y/n)", fore="yellow"))

    if input() != "y":
        print("Exiting...")
        sys.exit(1)

    parsed = []
    for file in files:
        try:
            filename = file["filename"].split(".txt")[0]
            output = file["content"]
            address = ""
            if output["victim_street_address"]:
                address = get_coordinates(output["victim_street_address"])

            output["victim_street_address"] = address

            parsed.append({"filename": filename, "content": output})

        except Exception as e:
            logger.warning(e)
            logger.warning(f"Error parsing {file['filename']}")
            logger.info("Traceback:")
            raise e

    with open(out, "w") as f:
        writer = csv.writer(f)

        header = ["Picture ID", "Picture Date", "Bank Name", "Bank Address", "Victim Name", "Victim Street Address", "Victim Zip Code",
                  "Victim City", "Victim State", "Victim Latitude", "Victim Longitude", "Business Name", "Business Address", "Check Date", "Check Amount"]

        writer.writerow(header)

        for item in parsed:
            address = {"latitude": "", "longitude": "",
                       "street": "", "zip": "", "city": "", "state": ""}

            if item["content"]["victim_street_address"]:
                address["latitude"] = item["content"]["victim_street_address"][0] if len(
                    item["content"]["victim_street_address"]) > 0 else ""
                address["longitude"] = item["content"]["victim_street_address"][1] if len(
                    item["content"]["victim_street_address"]) > 1 else ""
                address["street"] = item["content"]["victim_street_address"][2].get(
                    "address", "") if len(item["content"]["victim_street_address"]) > 2 else ""
                address["zip"] = item["content"]["victim_street_address"][2].get(
                    "zipcode", "") if len(item["content"]["victim_street_address"]) > 2 else ""
                address["city"] = item["content"]["victim_street_address"][2].get(
                    "city", "") if len(item["content"]["victim_street_address"]) > 2 else ""
                address["state"] = item["content"]["victim_street_address"][2].get(
                    "state", "") if len(item["content"]["victim_street_address"]) > 2 else ""

            row = [item["filename"],
                   extract_file_date(item["filename"]),
                   item["content"]["bank_name"],
                   item["content"]["bank_address"],
                   item["content"]["victim_name"],
                   address["street"],
                   address["zip"],
                   address["city"],
                   address["state"],
                   address["latitude"],
                   address["longitude"],
                   item["content"]["business_name"],
                   item["content"]["business_address"],
                   item["content"]["date"],
                   item["content"]["check_amount"]
                   ]

            writer.writerow(row)

    print(C("Done!", fore="green", style="bright"))

if __name__ == "__main__":
    main(inputs=sys.argv[1], out=sys.argv[2])
