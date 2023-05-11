# apigee-monitoring-script
For each Apigee organization and environment you own, this scripts lists the total number of calls made to all APIs in that organization and environment for a specific month.

The script outputs the results textually on the console and in a csv file:

| Org | Env  | Metric |
|-----|------|--------|
| A   | axyz | 100    |
| B   | bxyz | 300    |
| C   | cxyz | 200    |

## Permissions
The service account or user used to run the script needs to have the following [permission](https://cloud.google.com/apigee/docs/api-platform/system-administration/apigee-roles): 
```
Apigee Analytics Viewer 
```

## Python Libraries 
```
google.auth
requests
```
You can install them by running this command:
```
pip install -r requirements.txt
```

## Execution Parameters
```
api_analysis.py [-h] --month MONTH --year YEAR --auth AUTH [--key KEY | --token TOKEN]

arguments:
  -h, --help     show this help message and exit
  --month MONTH  The month on which you want to run the analysis. Values accepted: 1-12
  --year YEAR    The year on which you want to run the analysis. Format accepted: 2023
  --auth AUTH    The authorization type you want to use. Values accepted: token or key
  --key KEY      Only if you selected auth=key. Path of .json service account key (must be enabled to use Apigee APIs)
  --token TOKEN  Only if you selected auth=token. Pass this value to automatically grep the token of the account you are using $(gcloud auth application-default print-access-token) or $(gcloud auth print-access-token)
```

## Example
Run this script to analyze March 2023 by authenticating via token from your personal workstation:
```
python3 api_analysis.py --month=3 --year=2023 --auth=token --token=$(gcloud auth print-access-token)
```

## Reference
* [Apigee API authentication methods](https://cloud.google.com/apigee/docs/api-platform/get-started/api-get-started)
* [List organization API](https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations/list)
* [List environments API](https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments/list)
* [Total number of calls made to all APIs](https://cloud.google.com/apigee/docs/api-platform/get-started/get-api-call-info#total-number-of-calls-made-to-all-apis)
