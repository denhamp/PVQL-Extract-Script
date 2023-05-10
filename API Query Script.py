import requests
import getpass
import sys

import yaml

requests.packages.urllib3.disable_warnings()

# Login Function uses information from the config.yml file to access the tenant.
# GetPass is used to get user password without echoing to the console.

with open(sys.argv[1], 'r') as yaml_file:
    yaml_data = yaml.safe_load(yaml_file)
tenant_url = yaml_data['tenant']['url']
username = yaml_data['tenant']['username']
headers = {
    "Cache-Control": "no-cache",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}

print(' Trying to Login')
url = tenant_url + "/api/v1/auth/login"
password = getpass.getpass(prompt='Enter your tenant password: ')
data = {"username": username, "password": password}
resp = requests.post(url, headers=headers, data=data, verify=False)
resp.raise_for_status()
token = (resp.headers['Authorization'])
print(' Login Completed')

# Function to access the required data using PVQL.

url = tenant_url + "/v0/applications/latest_version"

url = "https://essensys-us.analytics.accedian.io/api/capture-orchestrate/v0/captures /?offset = 0 & limit = 100"

headers = {
    "Accept": "application/json",
    "Authorization": token,
}

resp = requests.get(url, headers=headers, data=data, verify=False)
resp.raise_for_status()

print(resp)
