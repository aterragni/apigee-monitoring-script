'''
  Copyright 2023 Google. This software is provided as-is,
  without warranty or representation for any use or purpose.
'''

# import needed libraries (you need to install them in your python env before proceeding, please use pip install -r requirements.txt)
import google.auth
from google.auth.transport import requests
from google.oauth2 import service_account
import requests
import calendar
import argparse
import csv



# Apigee APIs used by this script 
LIST_ORGS_API="https://apigee.googleapis.com/v1/organizations"
LIST_ENVS_API="https://apigee.googleapis.com/v1/organizations/{ORG}/environments"
GET_API_SUM_API='https://apigee.googleapis.com/v1/organizations/{ORG}/environments/{ENV}/stats?select=sum(message_count)&timeRange={MONTH}/1/{YEAR}+00:00~{MONTH}/{LAST_DAY_OF_THE_MONTH}/{YEAR}+00:00'




# ************************************************
# Initialize parameters parser

parser = argparse.ArgumentParser(description = "Apigee API analysis script")

parser.add_argument('--month', type=int, required=True, help='The month on which you want to run the analysis. Values accepted: 1-12')
parser.add_argument('--year', type=int, required=True, help='The year on which you want to run the analysis. Format accepted: 2023')

parser.add_argument('--auth', type=str, required=True, help='The authorization type you want to use. Values accepted: token or key')
group = parser.add_mutually_exclusive_group()
group.add_argument('--key',type=str, help='Only if you selected auth=key. Path of .json service account key (must be enabled to use Apigee APIs)')
group.add_argument('--token',type=str, help='Only if you selected auth=token. Pass this value to automatically grep the token of the account you are using $(gcloud auth application-default print-access-token) or $(gcloud auth print-access-token)')

args = parser.parse_args()
# ************************************************



# ************************************************
# extracting parameters

# extracting the end day of the selected month, it will be used in the analytics extraction query
LAST_DAY_OF_THE_MONTH = str(calendar.monthrange(args.year, args.month)[1])


if(args.auth=='key'):
    # the python script logs-in through the service account and gets the token to use the APIs
    credentials = service_account.Credentials.from_service_account_file(args.key, scopes=['https://www.googleapis.com/auth/cloud-platform'])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    b_token = "Bearer " + str(credentials.token)
    HEADERS = {"Authorization": b_token}


if(args.auth=='token'):
    b_token = "Bearer " + str(args.token)
    HEADERS = {"Authorization": b_token}
# ************************************************



# ************************************************
# starting analysis

print('Selected month: ' + str(args.month) + "/" + str(args.year))

# listing Apigee organizations
try:
    org_response = requests.get(LIST_ORGS_API, headers=HEADERS)
    ORGS=[]
    for o in org_response.json()["organizations"]:
        ORGS.append(o["organization"])
except Exception as e:
    print('error in listing the organizations')
    print(e)
    quit()


# variable to store metrics, it will be used to build the csv export
data = []

# for every org, listing the envs
for ORG in ORGS:
    print("\n\nOrg: ", ORG)
    try:
        env_response = requests.get(LIST_ENVS_API.format(**{'ORG':ORG}), headers=HEADERS)
        envs_json = env_response.json()
    except Exception as e:
        print('error in listing the envs for organization:', str(ORG))
        print(e)
        continue

    # for every env in the organization, extracting the total number of calls made to all APIs.
    for ENV in envs_json:
        print("\nEnv: ", ENV)
        anaytics_response = requests.get(GET_API_SUM_API.format(**{'ORG':ORG, 'ENV': ENV, 'MONTH': str(args.month), 'YEAR': str(args.year) , 'LAST_DAY_OF_THE_MONTH': LAST_DAY_OF_THE_MONTH }), headers=HEADERS)
        if "metrics" in anaytics_response.json()["environments"][0].keys():
            metric=str(anaytics_response.json()["environments"][0]["metrics"][0]['values'][0])
            print("Total number of API calls: " + metric)
            data.append([ORG,ENV,metric])
        else:
            print('no metrics available')
            data.append([ORG,ENV,0])        
    

with open(str(args.year)+'-'+str(args.month)+'.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(['org', 'env', 'metric'])

    # write multiple rows
    writer.writerows(data)
