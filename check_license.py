import requests, credentials

#Before any computation takes place, check if the Pi ICCID license is active.
def get_license(iccid):

    #Call API to get Pi licensing data.
    URL = ("%s/pi/getLicense" % credentials.db_address)
    PARAMS = {'iccid' : iccid}
    pi_values = requests.post(url=URL, data=PARAMS)

    #Check if server returns internal error code.
    if pi_values.status_code != 500 and pi_values.text != "No ICCID found.":
        #If server responds, get active and suspend status from response.
        pi_values_json = pi_values.json()
        pi_active_status = pi_values_json[0][0]
        pi_suspend_status = pi_values_json[0][1]

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
    else:
        return False