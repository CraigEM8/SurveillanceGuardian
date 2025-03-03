import requests

iccid = "8935711001091680394"
db_address = "https://em8database.com/api"

#Before any computation takes place, check if the Pi ICCID license is active.
def get_license(iccid):

    #Call API to get Pi licensing data.
    URL = ("%s/pi/getLicense" % db_address)
    PARAMS = {'iccid' : iccid}
    pi_values = requests.post(url=URL, data=PARAMS).json()
    pi_active_status = pi_values[0][0]
    pi_suspend_status = pi_values[0][1]

    #Return value of whether to continue with script. 
    if pi_suspend_status == 1:
        print("Pi license suspended.")
        return False
    elif pi_active_status == 0:
        print("Pi not activated.")
        return False
    else:
        print("Pi and license active.")
        return True