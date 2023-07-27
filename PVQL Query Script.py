import requests
import getpass
import sys

import yaml

requests.packages.urllib3.disable_warnings()

# Login Function uses information from the config.yml file to access the tenant.
# GetPass is used to get user password without echoing to the console.


def login_func():
    with open(sys.argv[1], "r") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    tenant_url = yaml_data["tenant"]["url"]
    print(f"Url: {tenant_url}")
    username = yaml_data["tenant"]["username"]
    print(f"Username: {username}")
    url = tenant_url + "/api/v1/auth/login"
    pvql_query = yaml_data["tenant"]["pvql query"]
    output_file = yaml_data["tenant"]["output file"]
    print(f"PVQL Query: {pvql_query}")
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    password = getpass.getpass(prompt="Enter your tenant password: ")
    data = {"username": username, "password": password}
    resp = requests.post(url, headers=headers, data=data, verify=False)
    resp.raise_for_status()
    token = resp.headers["Authorization"]

    return token, tenant_url, pvql_query, output_file


# Function to access the required data using PVQL.


def query_data(token, tenant_url, pvql_query):
    url = tenant_url + "/pvbackd/api/query"

    headers = {
        "Accept": "application/json",
        "Authorization": token,
    }
    data = {"expr": pvql_query}

    print(data)
    # Examples
    # data = {"expr":"server.rt BY application.name FROM tcp"}
    # data ={"expr":"traffic BY client.ip,server.ip,server.port,protostack FROM transport WHERE source.ip = 45.12.142.140 SINCE @now - 3600"}
    # data ={'expr':'ct.count BY server_name FROM tls SINCE @now-3600'}
    # data ={"expr":"traffic BY client.ip,server.ip,server.port,protostack FROM transport WHERE client.ip = 45.12.142.140 OR server.ip = 45.12.142.140}

    resp = requests.post(url, headers=headers, data=data, verify=False)
    resp.raise_for_status()

    dataj = resp.json()
    print(dataj)
    return dataj


def main():
    data = login_func()
    dataj = query_data(data[0], data[1], data[2])
    print(dataj)
    print("Number of Keys " + str(len(dataj["result"]["info"]["columns"]["key"])))
    with open(data[3], "w") as f:
        length = len(dataj["result"]["data"])
        i = 0
        j = 0
        k = 0
        while j < len(dataj["result"]["info"]["columns"]["key"]):
            ref = dataj["result"]["info"]["columns"]["key"][j]["name"]
            f.write(ref + ",")
            j += 1
        while k < len(dataj["result"]["info"]["columns"]["values"]):
            ref = dataj["result"]["info"]["columns"]["values"][k]["name"]
            f.write(ref + ",")
            k += 1
        f.write("\n")
        j = 0
        k = 0
        while i < length:
            while j < len(dataj["result"]["info"]["columns"]["key"]):
                if "value" in dataj["result"]["data"][i]["key"][j]:
                    keys1 = dataj["result"]["data"][i]["key"][j]["value"]
                else:
                    keys1 = dataj["result"]["data"][i]["key"][j]["status"]
                f.write(str(keys1) + ",")
                j += 1
            while k < len(dataj["result"]["info"]["columns"]["values"]):
                if "value" in dataj["result"]["data"][i]["values"][k]:
                    keys1 = dataj["result"]["data"][i]["values"][k]["value"]
                else:
                    keys1 = dataj["result"]["data"][i]["values"][k]["status"]
                f.write(str(keys1) + ",")
                k += 1
            k = 0
            i += 1
            j = 0
            f.write("\n")
        i = 1
        j = 1

    print("Total Data: " + str(len((dataj["result"]["data"]))))


if __name__ == "__main__":
    main()
