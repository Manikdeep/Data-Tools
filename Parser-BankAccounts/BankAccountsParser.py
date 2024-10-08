import json
import os
import openai
import pandas as pd
import ast
import re
from datetime import datetime
import bankcheckmodule

# loads the API key from the secrets.json file
def load_api_key(secrets_file="secrets.json"):
    with open(secrets_file) as f:
        secrets = json.load(f)
    return secrets["OPENAI_API_KEY"]


# reads the text files from the directory and returns a list of varprompts, photo_ids and dates
def read_varprompts_from_directory(directory):
    varprompts = []
    photo_ids = []
    dates = []
    titles=[]
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            photoId, fileDate,title = get_date_and_id_from_title(filename)
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                varprompts.append(file.read())
                photo_ids.append(photoId)
                titles.append(title)
                dates.append(fileDate)
    return varprompts, photo_ids, dates,titles

# returns the photo_id and date from the title of the text file
def get_date_and_id_from_title(title):
    re1 = title.split("@")
    photo_id = ""
    date = ""
    if '.DS_Store' not in re1:
        photo_id = re1[0].split("_")[1]
        date = re1[1].split("_")[0]
    return photo_id, date,title

# preprocesses the response text to remove commas from numbers
def preprocess_response_text(response_text):
    response_text = re.sub(r'(?<=\b)(\d+)(?=,|\n|\]|$)', lambda x: str(int(x.group())), response_text)
    return response_text

# extracts the account information ('Account_Number', 'Bank_Name', 'Amount', 'Account_Type') from the account dictionary
def extract_account_info(account_list,title):
    account_info_list = []
    for account_dict in account_list:
        banksReturnedByModule = bankcheckmodule.findbanknamebytextdes(account_dict.get('Bank_Name', ''))
        account_info = {
                'Account_Number': account_dict.get('Account_Number', ''),
                'Bank_Name': "",
                'Amount': account_dict.get('Amount', ''),
                'Account_Type': account_dict.get('Account_Type', '')
            }
        if len(banksReturnedByModule)>0:
            account_info['Bank_Name'] = banksReturnedByModule[0]
        elif banksReturnedByModule==[]:
            # print("BEFORE"+str(banksReturnedByModule) )
            banksReturnedByModule = bankcheckmodule.findbanknamebyfilename('<your project directory>/BankAccounts/Textfiles/'+title) # path to the text files passed to the bankcheckmodule.py 
            # print("AFTER"+str(banksReturnedByModule) )
            if banksReturnedByModule==[]:
                account_info['Bank_Name']=""
            elif len(banksReturnedByModule)>0:
                account_info['Bank_Name']=banksReturnedByModule[0]
            

        account_info_list.append(account_info)
    return account_info_list

api_key = load_api_key()
openai.api_key = api_key

# relative path to the directory containing the text files (Derived from OCR)
directory = "<your project directory>/BankAccounts/Textfiles"
varprompts, photo_ids, dates,titles = read_varprompts_from_directory(directory)

data = []
total_files = len(photo_ids)
print(f"Total number of photo_ids: {total_files}")
count = 0

# Iterate through the varprompts, photo_ids and dates and call the OpenAI API to get the response
for varprompt, photo_id, date, title in zip(varprompts, photo_ids, dates, titles):
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt="find bank account number (only numbers as string), bank name, available balance or amount (only numbers as strings), and type of account (categorize it as 'savings', 'Checking', 'credit', or ' ' ).\nreply as list of dictionaries with keys 'Account_Number', 'Bank_Name', 'Amount' and 'Account_Type'\n" + varprompt,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        response_text = response.choices[0]['text']

        # Preprocess the response_text string entries (string dictionaries) and convert them to dictionaries
        response_text = re.sub(r'\n', '', response_text)
        extracted_dicts = re.findall(r'\[.*?\]', response_text)
        response_dicts = [ast.literal_eval(dictionary) for dictionary in extracted_dicts]
        
        for account_info_dict in response_dicts:
            account_info_list = extract_account_info(account_info_dict,title)
            for account_info in account_info_list:
                account_info['photo_id'] = photo_id
                account_info['date'] = date
                data.append(account_info)
                print(account_info)

        count += 1
        print(f"Filenumber: {count}, with id: {photo_id} processed.")

    except Exception as e:
        print(f"Error processing file: {photo_id}_{date}.txt")
        print(f"Error description: {str(e)}")
        continue  # Skip to the next iteration if there's an error

# Create a DataFrame using pandas
df = pd.DataFrame(data)

# Rearrange columns to have 'photo_id' and 'date' at the beginning
df = df[['photo_id', 'date', 'Bank_Name', 'Account_Type', 'Account_Number', 'Amount'] + [col for col in df.columns if col not in ['photo_id', 'date', 'Bank_Name', 'Account_Type', 'Account_Number', 'Amount']]]

print("\nRearranged dataframe completed!!!")
print("\nWriting data to excel file...\n")

# Get the current datetime
current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

# Append datetime to the filename
excel_filename = f"account_info_{current_datetime}.xlsx"

# Save the DataFrame to the Excel file
df.to_excel(excel_filename, index=False)

print(f"Account information saved to {excel_filename}")