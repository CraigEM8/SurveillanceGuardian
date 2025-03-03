import requests, xmltodict, random, mysql.connector, check_license
from datetime import date, datetime

#Temporary variables for testing.
ipAddress = "192.168.1.73"
username = "admin"
password = "Concept1"
iccid = "8935711001091680394"
db_address = "https://em8database.com/api"

mydb = mysql.connector.connect(
        host = "em8database.com",
        user = "em8database_em8database",
        password = "K108dls2506!",
        database = "em8database_SurveillanceGuardian"
        )


#Get a random value in maximum integer range for the video log ID.
def get_random_number():
    random_number = random.randint(1, 2147483646)
    return random_number

def storage_changelog():
    #Request url.
    request_url = ("http://%s/ISAPI/ContentMgmt/Storage/hdd" % ipAddress)
    auth = requests.auth.HTTPDigestAuth(username, password)
    response = requests.get(request_url, auth=auth)

    #Get Site ID from API.
    URL = ("%s/sites/getSiteID" % db_address)
    PARAMS = {'iccid' : iccid}
    request_site = requests.post(url=URL, data=PARAMS)
    site_id = request_site.text

    #Response code check.
    if response.status_code == 200:

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_hdd = json_data["hddList"]["hdd"]

        #MAKE COMPARISON BETWEEN LAST LOGGED RECORD AND NEW ONE IF ONE EXISTS, WRITE CHANGES TO CHANGELOG.
        hdd_id = json_hdd["id"]
        storage_id = (f"siteID_{site_id}_storage_{hdd_id}")
        current_storage_data = [storage_id, json_hdd["hddName"], json_hdd["status"]]
        stored_storage_data = []
        changelog_data = []

        #Call API to check if storage ID exists.
        URL = ("%s/storage/getStorage" % db_address)
        PARAMS = {'storage_id' : storage_id}
        storage_records = requests.post(url=URL, data=PARAMS)
        storage_values = storage_records.json()

        #If query returns results, loop through and save found values to an array for comparison. 
        if len(storage_values) > 0:
            stored_storage_data.append([storage_values["id"], storage_values["name"], storage_values["status"]])
        else:
            #If first entry input null value.
            stored_storage_data.append(["null", "null", "null"])
        
        #Iterate through and compare data from API to database array, provided a database entry exists.
        for i in range(len(stored_storage_data)):
            #Check if storage ID is the same.
            if str(current_storage_data[0]) == str(stored_storage_data[i][0]):
                #Check if storage status is different.
                if str(current_storage_data[2]) != str(stored_storage_data[i][2]):
                    #Call API to get changelog ID.
                    URL = ("%s/changelog/getNewID" % db_address)
                    get_new_changelog_id = requests.get(url=URL)
                    changelog_id = get_new_changelog_id.text

                    #Append changelog entry to array.
                    changelog_data.append([changelog_id, 1, "status changed", stored_storage_data[i][2], current_storage_data[2], date.today(), datetime.now().strftime("%H:%M:%S")])
                    
                    print(f'{current_storage_data[0]} status changed from output {stored_storage_data[i][2]} to {current_storage_data[2]} at {datetime.now().strftime("%H:%M:%S")}.')
                else:
                    print(f'{current_storage_data[1]} is showing no changes at {datetime.now().strftime("%H:%M:%S")}.')

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

    insert_storage_log() 


def insert_storage_log():
    #Request url.
    request_url = ("http://%s/ISAPI/ContentMgmt/Storage/hdd" % ipAddress)
    auth = requests.auth.HTTPDigestAuth(username, password)
    response = requests.get(request_url, auth=auth)

    #Response code check.
    if response.status_code == 200:

        #Get Site ID from API.
        URL = ("%s/sites/getSiteID" % db_address)
        PARAMS = {'iccid' : iccid}
        request_site = requests.post(url=URL, data=PARAMS)
        site_id = request_site.text

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_hdd = json_data["hddList"]["hdd"]

        storage_id = "siteID_" + str(site_id) + "_storage_" + str(json_hdd["id"])

        #Get video data from API call and store in dictionary.
        PARAMS = {'storage_id': storage_id, 'device_id': 1, 'storage_name': json_hdd["hddName"], 'storage_status': json_hdd["status"], 'check_date': datetime.now().strftime("%Y-%m-%d"), 'check_time': datetime.now().strftime("%H:%M:%S")}

        #Define URL for API call to post acquired storage data for insertion into database.
        URL = ("%s/storage/inputStorageLog" % db_address)
        
        r = requests.post(url=URL, data=PARAMS)
        print(r.text)

    else:
        print(response.status_code)


#Check storage status and update database if status has changed.
def check_storage_status():
    #Request url.
    request_url = ("http://%s/ISAPI/ContentMgmt/Storage/hdd" % ipAddress)
    auth = requests.auth.HTTPDigestAuth(username, password)
    response = requests.get(request_url, auth=auth)

    #Response code check.
    if response.status_code == 200:

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_hdd = json_data["hddList"]["hdd"]

        #NEED TO GET STORAGE ID FROM DATABASE. TESTING WITH 1 FOR NOW.
        storage_id = 1


        mycursor = mydb.cursor()

        #Check if storage ID is already in the database.
        mycursor.execute("SELECT * FROM storage WHERE storage_id = %s AND storage_status != %s", (storage_id,json_hdd["status"]))
            
        myresult = mycursor.fetchall()

        #Get prior status of storage device from database to put into changelog.
        for data in myresult:
            previous_status = data[3]
            current_status = data[4]
        
        #If the storage ID is already in the database and the status has changed, update the database.
        if len(myresult) > 0:

            #Generate changeLogID and check if it already exists, if so to call the main function again.
            changelog_id = get_random_number()

            mycursor.execute(f"SELECT * FROM `changelog` WHERE `changelog_id` = '{changelog_id}'")

            changeLogResult = mycursor.fetchall()

            if len(changeLogResult) > 0:
                
                check_storage_status()

            else:

                #Get video data from API call and store in dictionary.
                PARAMS = {'storage_id': storage_id, 'changelog_id' : changelog_id, 'storage_status': json_hdd["status"], 'previous_status' : previous_status, 'current_status' : current_status, 'changelog_date': datetime.now().strftime("%Y-%m-%d"), 'changelog_time': datetime.now().strftime("%H:%M:%S")}

                #Define URL for API call to post changed storage data and update the database.
                URL = "http://127.0.0.1:5000/storageLogs/updateStorageLog"
                
                requests.post(url=URL, data=PARAMS)

                print("Storage status has changed.")

        else:
            print("Storage status has not changed or ID not found.")

    
#Get data from API of whether the Pi has been activated or is suspended and if to continue with processing. 
if check_license.get_license(iccid) == True:
    #Insert or update storage records in the database. Insert any changes into changelog table.
    storage_changelog()  
else:
    print("Pi not activated or license suspended.")