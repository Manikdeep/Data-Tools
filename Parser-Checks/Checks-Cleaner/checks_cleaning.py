import pandas as pd
# Import parser from dateutil
from dateutil import parser
import spacy
from word2number import w2n
import googlemaps
from datetime import datetime
import re
import sys  

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

####Check_Date and Picture_Date
def format_date(df, column_name):
    formatted_dates = []
    
    for date_str in df[column_name]:
        try:
            date = parser.parse(date_str)
            formatted_dates.append(date.strftime('%m/%d/%Y'))
        except OverflowError as oe:
            print(f"Overflow error with date_str: '{date_str}' - {oe}")
            formatted_dates.append(' ')
        except (TypeError, ValueError) as e:
            # If parsing fails for reasons other than OverflowError
            formatted_dates.append(' ')

    formatted_column_name = 'Formatted_' + column_name
    df[formatted_column_name] = formatted_dates

    cols = df.columns.tolist()
    date_index = cols.index(column_name)
    formatted_date_index = cols.index(formatted_column_name)

    cols.pop(formatted_date_index)
    cols.insert(date_index + 1, formatted_column_name)
    df = df[cols]
    df.drop(column_name, axis=1, inplace=True)
    return df

data = pd.read_csv('<your project directory>/Checks.csv')
data_cleaned = data.dropna(how='all').replace('', pd.NA).dropna(how='all')

# Adjust the parsing of 'Picture Date' using dateutil for flexibility
data_cleaned['Picture Date'] = data_cleaned['Picture Date'].apply(lambda x: parser.parse(x).strftime('%m/%d/%Y') if pd.notnull(x) else x)

# data_cleaned['Picture Date'] = pd.to_datetime(data_cleaned['Picture Date'],format='%d/%m/%Y')
# print(data_cleaned['Picture Date'])
# data_cleaned['Picture Date'] = data_cleaned['Picture Date'].dt.strftime('%m/%d/%Y')
columns = ['Check Date']
for column in columns:
    data_cleaned = format_date(data_cleaned, column)

#Names
Model = spacy.load('en_core_web_sm')
def replace_and_print_persons(text):
    if isinstance(text, str):
        NER_text = Model(text)
        modified_text = text
        is_person = False
        for ent in NER_text.ents:
            if ent.label_ == "PERSON":
                is_person = True
                modified_text = text
                print("Recognized PERSON:", ent.text)
                break  
        return modified_text if is_person else ""
    else:
        return ""
data_cleaned['Victim Name'] = data_cleaned['Victim Name'].apply(replace_and_print_persons)

##Check_Amount
pattern = r'^(.*?)(?:\bUS DOLLARS\b|$|\b\d+\s+and\s+\d+/\d+\s*DOLLARS\b)|\b(?:[A-Za-z]*\s)?(?:[A-Za-z]+\s)?(?:[A-Za-z]+\s)?[A-Za-z]+\s?dollars\b|\b(?:[A-Za-z]*\s?[A-Za-z]+\s?)+\b'
def convert_to_numerical(match):
    amount_in_words = match.group(0).strip("$").strip()
    try:
        if amount_in_words:
            amount_numerical = w2n.word_to_num(amount_in_words)
            return f"${amount_numerical:,.2f}"
        else:
            return match.group(0)
    except (ValueError, IndexError):
        return match.group(0)

data_cleaned['Check Amount'] = data_cleaned['Check Amount'].apply(lambda text: re.sub(pattern, convert_to_numerical, str(text), flags=re.IGNORECASE))
data_cleaned['Check Amount'] = data_cleaned['Check Amount'].replace('nan', '')
data_cleaned['Check Amount'] = data_cleaned['Check Amount'].apply(lambda amount: f'${amount}' if re.search(r'\d', str(amount)) and not str(amount).startswith('$') else amount)
to_remove = r'[a-zA-Z0-9\.]{15,}'
data_cleaned['Check Amount'] = data_cleaned['Check Amount'].replace(to_remove, '', regex=True)


#Business_Address
def geocode_address(address, api_key):
    gmaps = googlemaps.Client(key=api_key, timeout=10)

    street_address = None
    street_name=None
    city = None
    state = None
    zipcode = None
    country = None

    geocode_result = gmaps.geocode(address)
    if not geocode_result:
        print(f"No geocode result found for address '{address}'")
    else:
        street_address = geocode_result[0]['formatted_address'] 
        address_parts = street_address.split(', ')

        street_name = address_parts[0]
        print(f"Street:{street_name}")

      
        city = None
        for component in geocode_result[0]['address_components']:
            if 'locality' in component['types']:
                city = component['long_name']
        if city is not None:
            print('City:', city)
        else:
            print('City:', 'Not found')

        state = None
        for component in geocode_result[0]['address_components']:
            if 'administrative_area_level_1' in component['types']:
                state = component['long_name']
        if state is not None:
            print('State:', state)
        else:
            print('State:', 'Not found')

      
        zipcode = None
        for component in geocode_result[0]['address_components']:
            if 'postal_code' in component['types']:
                zipcode = component['long_name']
        if zipcode is not None:
            print('ZIP code:', zipcode)
        else:
            print('Zipcode:', 'Not found')

       
        country = None
        for component in geocode_result[0]['address_components']:
            if 'country' in component['types']:
                country = component['long_name']
        if country is not None:
            print('Country:', country)
        else:
            print('Country:', 'Not found')
    
    return {'Geocoded_Address': address,'Street': street_name, 'City': city, 'State': state, 'Zipcode': zipcode, 'Country': country}

list =['City','State','Zipcode']
Address_list = data_cleaned['Business Address'].tolist()
results = []
for address in Address_list:
    print(f"Address is : {address}")
    result = geocode_address(address, 'GOOGLE_MAPS_API_KEY')
    results.append(result)
    print("____________________________________________________")

df_results = pd.DataFrame(results, columns=['Geocoded_Business_Address','Street', 'City', 'State', 'Zipcode', 'Country'])
Address_index = data_cleaned.columns.get_loc("Business Address")
data_final = pd.concat([data_cleaned.iloc[:, :Address_index + 1], df_results, data_cleaned.iloc[:, Address_index + 1:]], axis=1)
#data = data[data.astype(str).applymap(lambda x: x.strip() != '').all(axis=1)]
#data_final = data_final.drop('Geocoded_Business_Address')
data_final.to_csv('<your project directory>/Checks_Cleaned.csv', index=False)
 
