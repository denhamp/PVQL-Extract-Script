import requests
import getpass
import sys
import yaml

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

def login_func(yaml_data):
    tenant_url = yaml_data.get("tenant", {}).get("url")
    username = yaml_data.get("tenant", {}).get("username")
    pvql_query = yaml_data.get("tenant", {}).get("pvql query")
    output_file = yaml_data.get("tenant", {}).get("output file")

    if not all([tenant_url, username, pvql_query, output_file]):
        raise ValueError("Missing required fields in the YAML configuration.")

    url = f"{tenant_url}/api/v1/auth/login"
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    password = getpass.getpass(prompt="Enter your tenant password: ")
    data = {"username": username, "password": password}
    
    resp = requests.post(url, headers=headers, data=data, verify=False)
    resp.raise_for_status()
    
    token = resp.headers.get("Authorization")
    return token, tenant_url, pvql_query, output_file

def query_data(token, tenant_url, pvql_query):
    url = f"{tenant_url}/pvbackd/api/query"
    headers = {
        "Accept": "application/json",
        "Authorization": token,
    }
    data = {"expr": pvql_query}
    
    resp = requests.post(url, headers=headers, data=data, verify=False)
    resp.raise_for_status()
    
    data_json = resp.json()
    return data_json

def main():
    try:
        with open(sys.argv[1], "r") as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
        
        token, tenant_url, pvql_query, output_file = login_func(yaml_data)
        data_json = query_data(token, tenant_url, pvql_query)
        
        with open(output_file, "w") as f:
            columns = [col["name"] for col in data_json["result"]["info"]["columns"]["key"]]
            columns += [col["name"] for col in data_json["result"]["info"]["columns"]["values"]]
            f.write(",".join(columns) + "\n")
            
            for entry in data_json["result"]["data"]:
                keys = [entry["key"][i].get("value", entry["key"][i].get("status")) for i in range(len(columns))]
                values = [entry["values"][i].get("value", entry["values"][i].get("status")) for i in range(len(columns))]
                f.write(",".join(map(str, keys + values)) + "\n")
                
        print("Data written to:", output_file)
        print("Total entries:", len(data_json["result"]["data"]))
        
    except (IndexError, FileNotFoundError):
        print("Usage: python script.py <config_file.yaml>")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
