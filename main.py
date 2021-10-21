#DISCLAIMER: Please note: This script is meant for demo purposes only. All tools/
# #scripts in this repo are released for use "AS IS" without any warranties of any kind,
# #including, but not limited to their installation, use, or performance. Any use of
#these scripts and tools is at your own risk. There is no guarantee that they have
# #been through thorough testing in a comparable environment and we are not responsible
# #for any damage or data loss incurred with their use. You are responsible for
# #reviewing and testing any scripts you run thoroughly before use in any non-testing
# #environment.
#---Requirments:
##python 3.8 or higher
##Meraki SDK - pip3 install meraki

# usage python3 main.py

def validate_ip_address(address):
    try:
        ip = ipaddress.ip_address(address)
        print("IP address {} is valid.".format(address))
    except ValueError:
        print("IP address {} is not valid. Please check the address and try again!".format(address))
        sys.exit(0)
    return

import meraki
import getopt, csv, os, sys, time
import ipaddress


def main():

    arg_apikey = None
    arg_orgname = None
    arg_netname = None
    arg_dns1 = None
    arg_dns2 = None
    orgid = None
    netid = None

    #Catch and Validate user Input
    arg_apikey = input("Enter your API Key: ")
    if arg_apikey == "":
        print("API Key Required!")
        sys.exit(0)

    arg_orgname = input("Enter the Organization Name: ")
    if arg_orgname == "":
        print("Orginazation name is required!")
        sys.exit(0)

    arg_netname = input("Enter your Network Name: ")
    if arg_netname == "":
        print("Network neme is required!")
        sys.exit(0)

    arg_dns1 = input("Enter the 1st DNS Server IP: ")
    validate_ip_address(arg_dns1)

    arg_dns2 = input("Enter the 2nd DNS Server IP: ")
    validate_ip_address(arg_dns2)


    API_KEY = arg_apikey
    dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)

    # get orgid for specified org name
    org_response = dashboard.organizations.getOrganizations()

    for org in org_response:
        if org['name'].lower() == arg_orgname.lower():
            orgid = org['id']
            # print(orgid)
            print("Org" + " " + orgid + " " + "matched.")
        else:
            print("Exception: " + "Org: " + org['id'] + " does not match: " + org['name'] + ' Is not the orginization specified!')

    # Get Network ID for specified network name if network name has been specified
    print ("Resolving Network: " + arg_netname)
    networks = dashboard.organizations.getOrganizationNetworks(orgid, total_pages='all')
    for network in networks:
        if network['name'].lower() == arg_netname.lower():
            netid = network['id']
            #print(netid)

    #Get Orginization Devices and filter based on Product and Network
    devices = dashboard.organizations.getOrganizationDevices(orgid, total_pages='all')
    wireless = [device for device in devices if device['model'][:2] == 'MR' and device['networkId'] == netid]
    #print(wireless)

    try:
        s_device_data = []

        for s in wireless:
            #print(s)
            s_data_df = {'Serial': s['serial'], 'Model': s['model'], 'IP': s['lanIp']}
            #print(s_data_df)
            s_device_data.append(s_data_df)
            #print(s_device_data)

        for row in s_device_data:
            mgmt_data = dashboard.devices.getDeviceManagementInterface(row['Serial'])
            #print(mgmt_data)
            time.sleep(1)

            if mgmt_data['wan1']['usingStaticIp'] == True:
                response = dashboard.devices.updateDeviceManagementInterface(
                    row['Serial'], wan1={'staticDns': [arg_dns1, arg_dns2]})
                print("Serial" + ' ' + row['Serial'] + ' ' + "has been updated to" + ' ' + arg_dns1 + ' & ' + arg_dns2)
                print(response)
                time.sleep(1)


            elif mgmt_data['wan1']['usingStaticIp'] == False:
                print("Serial" + ' ' + row['Serial'] + ' ' + "is set to DHCP so no changes will be made!")

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()






