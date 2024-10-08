import os
import sys
import time
import json
from utils import get_files, calculate_price, calculate_google_maps_price
import openai
from colr import Colr as C

from dotenv import load_dotenv
load_dotenv()

# Parse


def parse(text):
    PROMPT_MESSAGE = """Parse this output in the format {"date": ..., "bank_name": ..., "bank_address": ..., "victim_name": ..., "victim_street_address": ..., "business_name": ..., "business_address": ..., "check_amount": ...}, if you can't parse it, return empty values but the same JSON object. Return only a single JSON object, no other text but the JSON object. \n ------ \n"""

    # "victim_zipcode": ..., "victim_city": ..., "victim_state": ...,

    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"{text} {PROMPT_MESSAGE}"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])

    result = completion.choices[0].message.content

    print(result)

    return result

# Main


def main(directory, corrupt_files, out):
    files = get_files(directory)
    files_to_parse = []
    files_with_outputs = []

    with open(corrupt_files, "r") as f:
        cfiles = [line.strip() for line in f if line.strip()]
        for file in cfiles:
            files_to_parse.append(json.loads(file)["filename"] + ".txt")

    for i in files:
        if i in files_to_parse:
            with open(os.path.join(directory, i), "r") as f:
                files_with_outputs.append(
                    {"filename": i, "content": "".join(f.read().split("\n")[:-1])})

    cost_of_operation = 0

    for file in files_with_outputs:
        cost_of_operation += calculate_price(
            file["content"])

    print("Number of files:", len(files_with_outputs))

    print("Cost of operation:", C(
        f"${cost_of_operation}", fore="red", style="bright"))

    print("Do you want to continue?", C("(y/n)", fore="yellow"))

    if input() == "y":
        start_time = time.time()
        parsed = []
        for file in files_with_outputs:
            try:
                # Sleep function to avoid getting ratelimited
                # time.sleep(0.025)

                filename = file["filename"].split(".txt")[0]
                output = parse(file["content"])

                parsed.append(
                    {"filename": filename, "content": output})

            except Exception as e:
                raise e
                # raise e

        with open(out + ".error.jsonl", "w") as f:
            for file in parsed:
                json.dump(file, f)
                f.write("\n")
            f.close()

        end_time = time.time()

        time_elapsed = end_time - start_time

        print(C(f"Done in {time_elapsed} seconds.",
              fore="green", style="bright"))
    else:
        print("Exiting...")
        sys.exit(1)


if __name__ == "__main__":
    main(directory=sys.argv[1], corrupt_files=sys.argv[2], out=sys.argv[3])
