import netifaces, requests, check_license
from datetime import date, datetime

iccid = "8935711001091680394"
db_address = "https://em8database.com/api"

#Check if interface is live.
def is_interface_up(interface):
    addr = netifaces.ifaddresses(interface)
    return netifaces.AF_INET in addr

#Get IP address of interface parameter.
def get_ip_address(ifname):
    addresses = netifaces.ifaddresses(ifname)

    if addresses:
        return addresses[netifaces.AF_INET][0]['addr']
    else:
        return "No such interface found."
    
#Pass through list of interfaces to check if they're live then to get the IP.
def get_ip_list():
    interfacesList = ['eth0', 'ppp0']
    interfacesIP = []

    for interface in interfacesList:
        is_up = is_interface_up(interface)
        if is_up:
            ip = get_ip_address(interface)
            interfacesIP.append(ip)
        else:
            interfacesIP.append(ip)

    return interfacesIP

#Get current and stored IP data related to Pi and make comparison for changes.
def pi_changelog():

    #Call API to check if system ID exists.
    URL = ("%s/pi/getInfo" % db_address)
    PARAMS = {'iccid' : iccid}
    stored_pi_values = requests.post(url=URL, data=PARAMS).json()
    current_pi_values = get_ip_list()
    changelog_data = []

    #If Eth/Wlan is not the same as stored in database.
    if str(current_pi_values[0]) != str(stored_pi_values[0][0]):

        #Call API to get changelog ID.
        URL = ("%s/changelog/getNewID" % db_address)
        get_new_changelog_id = requests.get(url=URL)
        changelog_id = get_new_changelog_id.text

        #Append changelog entry to array.
        changelog_data.append([changelog_id, 1, "Eth address changed", stored_pi_values[0][0], current_pi_values[0], date.today(), datetime.now().strftime("%H:%M:%S")])
        
        print(f'ethernet address changed from {stored_pi_values[0][0]} to {current_pi_values[0]} at {datetime.now().strftime("%H:%M:%S")}.')
    
    #If PPP address is not the same as stored in database.
    if str(current_pi_values[1]) != str(stored_pi_values[0][1]):

        #Call API to get changelog ID.
        URL = ("%s/changelog/getNewID" % db_address)
        get_new_changelog_id = requests.get(url=URL)
        changelog_id = get_new_changelog_id.text

        #Append changelog entry to array.
        changelog_data.append([changelog_id, 1, "PPP address changed", stored_pi_values[0][1], current_pi_values[1], date.today(), datetime.now().strftime("%H:%M:%S")])
        
        print(f'LTE address changed from {stored_pi_values[0][1]} to {current_pi_values[1]} at {datetime.now().strftime("%H:%M:%S")}.')

        #Check if any changes are to be made.
    if len(changelog_data) > 0:
        for i in range(len(changelog_data)):
            #Call API to insert any changelogs.
            URL = ("%s/changelog/insertLog" % db_address)
            PARAMS = {'changelog_id' : changelog_data[i][0], 'device_id' : changelog_data[i][1], 'changelog_desc' : changelog_data[i][2], 'previous_status' : changelog_data[i][3], 'current_status' : changelog_data[i][4], 'changelog_date' : changelog_data[i][5], 'changelog_time' : changelog_data[i][6]}
            request_site = requests.post(url=URL, data=PARAMS)
            print(request_site.text)
    else:
        print("No changes to be made.")
    
    #Update record in database.
    URL = ("%s/pi/updateIP" % db_address)
    PARAMS = {'iccid' : iccid, 'eth_address' : current_pi_values[0], 'ppp_address' : current_pi_values[1], 'check_date' : date.today(), 'check_time' : datetime.now().strftime("%H:%M:%S")}
    request_site = requests.post(url=URL, data=PARAMS)
    print(request_site.text)

    #print(changelog_data)

#Get data from API of whether the Pi has been activated or is suspended and if to continue with processing. 
if check_license.get_license(iccid) == True:
    #Call function.
    pi_changelog()
else:
    print("Pi not activated or license suspended.")
