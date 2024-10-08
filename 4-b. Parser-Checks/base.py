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


def main(directory, out):
    files = get_files(directory)
    files_with_outputs = []

    for file in files:
        with open(os.path.join(directory, file), "r", encoding='utf-8') as f:
            files_with_outputs.append(
                {"filename": file, "content": "".join(f.read().split("\n")[:-1])})

    cost_of_operation = 0

    for file in files_with_outputs:
        cost_of_operation += calculate_price(
            file["content"]) + calculate_google_maps_price(1)

    print("Cost of operation:", C(
        f"${cost_of_operation}", fore="red", style="bright"))

    print("Do you want to continue?", C("(y/n)", fore="yellow"))

    if input() == "y":
        start_time = time.time()
        parsed = []
        unparseable = []
        for file in files_with_outputs:
            output = ""
            try:
                # Sleep function to avoid getting ratelimited
                # time.sleep(0.025)

                filename = file["filename"].split(".txt")[0]
                output = parse(file["content"])

                if not output:
                    unparseable.append(
                        {"filename": file["filename"].split(".txt")[0], "content": output})
                    continue

                parsed.append(
                    {"filename": filename, "content": output})

            except Exception as e:
                logger.warning(e)
                logger.warning(f"Error parsing {file['filename']}")
                logger.info("Traceback:")
                unparseable.append(
                    {"filename": file["filename"].split(".txt")[0], "content": output})
                # raise e

        with open(out + ".jsonl", "w") as f:
            for file in parsed:
                json.dump(file, f)
                # Add newline but not to last line
                if file != parsed[-1]:
                    f.write("\n")
            f.close()

        with open("unparseable.jsonl", "w") as f:
            for file in unparseable:
                json.dump(file, f)
                f.write("\n")
            f.close()

        end_time = time.time()

        time_elapsed = end_time - start_time

        print(C(f"Done in {time_elapsed}", fore="green", style="bright"))
        print(C("Unparseable files:", fore="yellow", style="bright"))
        print(C(", ".join(unparseable), fore="red", style="bright"))
    else:
        print("Exiting...")
        sys.exit(1)


if __name__ == "__main__":
    main(directory=sys.argv[1], out=sys.argv[2])
