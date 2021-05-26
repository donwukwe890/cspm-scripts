import requests
import json

# If you are API 2 or API 3, change the URL to api2 or api3.prismacloud.io
url = "https://api.prismacloud.io/search/config"

# Place your auth token in the variable below
token = ""
payload="{\n    \"query\": \"config from cloud.resource where cloud.type = 'azure' AND api.name = 'azure-network-nic-list' as X; config where api.name= 'azure-network-nsg-list' AND json.rule = securityRules[?any(access equals Allow and direction equals Inbound and (sourceAddressPrefix equals Internet or sourceAddressPrefix equals * or sourceAddressPrefix equals 0.0.0.0/0 or sourceAddressPrefix equals ::/0) and (destinationPortRange contains _Port.inRange(3389,3389) or destinationPortRanges[*] contains _Port.inRange(3389,3389) ))] exists as Y; filter  \\\"($.['X'].['properties.networkSecurityGroup'].['id'] contains $.Y.name)\\\" ; show X; \",\n    \"timeRange\": {\n        \"type\": \"relative\",\n        \"value\": {\n            \"unit\": \"hour\",\n            \"amount\": 24\n        }\n    }\n}"
headers = {
  'Content-Type': 'application/json',
  'x-redlock-auth': token,
  'Accept': 'application/json; text/csv; charset=UTF-8',
}

# Post the query to the Prisma Cloud URL
response = requests.request("POST", url, headers=headers, data=payload)

response_dict = json.loads(response.text)

# Get the Azure Nic data as a dictionary
azure_nics = response_dict.get('data')['items']

vm_with_nics = 0
nics_without_vms = 0

for line in azure_nics:
    print("Network Interface:", line.get('name'))
    obj = line.get('data')
    if obj['properties.virtualMachine']['id'] == '':
        print("Virtual Machine:", "Not attached")
        nics_without_vms = nics_without_vms + 1
    else:
        print("Virtual Machine:", obj['properties.virtualMachine']['id'].split('/')[-1])
        vm_with_nics = vm_with_nics + 1
    print("")

# Count the Nics without VMs attached, Nics with VMs attached, and the total number
print("VM Count:", vm_with_nics)
print("Nics without VMs Count:", nics_without_vms)
print("Total Number:", vm_with_nics + nics_without_vms)
