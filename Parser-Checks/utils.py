import os
import re
import tiktoken
import json
from decimal import Decimal
import openai
import googlemaps
from scourgify import normalize_address_record
from scourgify.exceptions import UnParseableAddressError

from dotenv import load_dotenv
load_dotenv()


def get_files(dirname):
    files = []
    for file in os.listdir(dirname):
        if file.endswith(".txt"):
            files.append(file)
    return files


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not presently implemented for model {model}.""")


def calculate_price(text):
    """Returns the price for a given number of tokens."""
    return (num_tokens_from_messages([{"role": "user", "content": text}]) / Decimal("1000")) * Decimal("0.002")


def calculate_google_maps_price(calls):
    return Decimal("0.0056") * calls


def parse(text):
    PROMPT_MESSAGE = """Parse this output in the format {"date": ..., "bank_name": ..., "bank_address": ..., "victim_name": ..., "victim_street_address": ..., "business_name": ..., "business_address": ..., "check_amount": ...}, if you can't parse it, return empty values but the same JSON object. Return only a single JSON object, no other text but the JSON object. \n ------ \n"""

    # "victim_zipcode": ..., "victim_city": ..., "victim_state": ...,

    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"{text} {PROMPT_MESSAGE}"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])

    result = completion.choices[0].message.content

    # print(result)

    return json.loads(result)


def get_coordinates(address):
    if len(address) == 0 or not address[0]:
        return None

    gmaps = googlemaps.Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))
    result = gmaps.geocode(address)

    if not result or not result[0]["geometry"]:
        return None

    latitude = result[0]["geometry"]["location"]["lat"]
    longitude = result[0]["geometry"]["location"]["lng"]

    try:
        formatted_address = normalize_address_record(
            result[0]["formatted_address"])

        if formatted_address["address_line_1"] is not None and formatted_address["address_line_2"] is not None:
            return (latitude, longitude, {"address": formatted_address["address_line_1"] + formatted_address["address_line_2"], "city": formatted_address["city"], "state": formatted_address["state"], "zipcode": formatted_address["postal_code"]})

        else:
            return (latitude, longitude, {"address": formatted_address["address_line_1"], "city": formatted_address["city"], "state": formatted_address["state"], "zipcode": formatted_address["postal_code"]})

    except UnParseableAddressError:
        formatted_address = result[0]["formatted_address"]

        return (latitude, longitude, {"address": formatted_address})


def extract_file_date(filename):
    return re.search(r'\d{2}-\d{2}-\d{4}', filename).group()
