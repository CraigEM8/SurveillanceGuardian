import netifaces, requests, serial, re, os, subprocess, time, check_license
from datetime import date, datetime

iccid = "8935711001091680394"
db_address = "https://em8database.com/api"


#Check if interface is live.
def is_interface_up(interface):
    try:
        addr = netifaces.ifaddresses(interface)
        return netifaces.AF_INET in addr
    except:
        return False

#Get IP address of interface parameter.
def get_ip_address(ifname):
    addresses = netifaces.ifaddresses(ifname)
    if addresses:
        return addresses[netifaces.AF_INET][0]['addr']
    else:
        return False
    
#Pass through list of interfaces to check if they're live then to get the IP.
def get_ip_list():
    interfacesList = ['wlan0', 'ppp0']
    interfacesIP = []

    for interface in interfacesList:
        is_up = is_interface_up(interface)
        if is_up:
            ip = get_ip_address(interface)
            interfacesIP.append(ip)
        else:
            interfacesIP.append("0.0.0.0")

    print(interfacesIP)

    return interfacesIP

# Function to get the signal strength of the SIM card.
def get_signal_strength():

    serial_lock_path = '/var/lock/LCK..ttyS0'

    if os.path.exists(serial_lock_path) == True:
        try:
            os.remove(serial_lock_path)
            print(f"Serial port unlocked.")
        except:
            print(f"Unable to delete serial lock.")

    # Open serial port, and write AT command to get signal strength.
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=5)
    ser.write("AT+CSQ\r".encode())
    response =  ser.readall()
    response_array = re.split(': |\,', str(response))
    strength = response_array[1]
    signal_strength = 'Signal condition is Unknown.'

    # Check the signal strength and print the condition.
    if len(strength) == 1 or len(strength) == 2:
        print(f"Signal strength is {strength}.")
        if int(strength) < 10:
            print("Signal condition is Marginal.")
            signal_strength = "Marginal"
        elif int(strength) >= 10 and int(strength) < 15:
            print("Signal condition is OK.")
            signal_strength = "OK"
        elif int(strength) >= 15 and int(strength) < 20:
            print("Signal condition is Good.")
            signal_strength = "Good"
        elif int(strength) >= 20 and int(strength) <= 30:
            print("Signal condition is Excellent.")
            signal_strength = "Excellent"
        else:
            print("Signal condition is Unknown.")
    else:
        print("Signal strength is not available.")

    ser.close()
    return signal_strength

# Function to get the carrier of the SIM card.
def get_sim_carrier():
    # Open serial port, and write AT command to get carrier code.
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=5)
    ser.write("AT+COPS?\r".encode())
    response =  ser.readall()
    response_array = re.split('"', str(response))
    carrier_code = response_array[1]
    sim_carrier = 'Sim carrier is Unknown.'

    # Check the carrier code and print the carrier.
    if len(carrier_code) == 5:
        print(f"Carrier code is {carrier_code}.")
        if int(carrier_code) == 23430:
            print("Sim Carrier is EE.")
            sim_carrier = "EE"
        elif int(carrier_code) == 23410:
            print("Sim Carrier is O2.")
            sim_carrier = "O2"
        elif int(carrier_code) == 23415:
            print("Sim Carrier is Vodafone.")
            sim_carrier = "Vodafone"
        elif int(carrier_code) == 23420:
            print("Sim Carrier is Three.")
            sim_carrier = "Three"
        else:
            print("Sim carrier is Unknown.")
    else:
        print("Sim carrier code is not known.")

    
    ser.close()
    return sim_carrier

#Get current and stored IP data related to Pi and make comparison for changes.
def pi_changelog():

    #Call API to check if system ID exists.
    URL = ("%s/pi/getInfo" % db_address)
    PARAMS = {'iccid' : iccid}
    stored_pi_values = requests.post(url=URL, data=PARAMS).json()

    #Switch off serial connection to allow AT commands to be sent.
    subprocess.Popen('sudo poff clipper', shell=True)
    time.sleep(30)

    sim_carrier = get_sim_carrier()
    sim_signal = get_signal_strength()

    #Switch on serial connection to get IP address and for further functionality.
    subprocess.Popen('sudo pon clipper', shell=True)
    time.sleep(30)

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

    if str(sim_carrier) != str(stored_pi_values[0][2]):

        #Call API to get changelog ID.
        URL = ("%s/changelog/getNewID" % db_address)
        get_new_changelog_id = requests.get(url=URL)
        changelog_id = get_new_changelog_id.text

        #Append changelog entry to array.
        changelog_data.append([changelog_id, 1, "SIM carrier changed", stored_pi_values[0][2], sim_carrier, date.today(), datetime.now().strftime("%H:%M:%S")])
        
        print(f'SIM carrier changed from {stored_pi_values[0][2]} to {sim_carrier} at {datetime.now().strftime("%H:%M:%S")}.')

    if str(sim_signal) != str(stored_pi_values[0][3]):

        #Call API to get changelog ID.
        URL = ("%s/changelog/getNewID" % db_address)
        get_new_changelog_id = requests.get(url=URL)
        changelog_id = get_new_changelog_id.text

        #Append changelog entry to array.
        changelog_data.append([changelog_id, 1, "SIM signal changed", stored_pi_values[0][3], sim_signal, date.today(), datetime.now().strftime("%H:%M:%S")])
        
        print(f'SIM signal changed from {stored_pi_values[0][3]} to {sim_signal} at {datetime.now().strftime("%H:%M:%S")}.')

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
    URL = ("%s/pi/updatePI" % db_address)
    PARAMS = {'iccid' : iccid, 'eth_address' : current_pi_values[0], 'ppp_address' : current_pi_values[1], 'sim_carrier' : sim_carrier, 'sim_signal' : sim_signal, 'check_date' : date.today(), 'check_time' : datetime.now().strftime("%H:%M:%S")}
    request_site = requests.post(url=URL, data=PARAMS)
    print(request_site.text)

#Get data from API of whether the Pi has been activated or is suspended and if to continue with processing. 
if check_license.get_license(iccid) == True:
    #Call function.
    pi_changelog()
else:
    print("Pi not activated or license suspended.")
