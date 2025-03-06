import serial, re, os, subprocess, time

def get_sim_iccid():
    try:
        serial_lock_path = '/var/lock/LCK..ttyS0'

        #Switch off serial connection to allow AT commands to be sent.
        subprocess.Popen('sudo poff clipper', shell=True)
        time.sleep(20)

        if os.path.exists(serial_lock_path) == True:
            try:
                os.remove(serial_lock_path)
                print(f"Serial port unlocked.")
            except:
                print(f"Unable to delete serial lock.")

        # Open serial port, and write AT command to get signal strength.
        ser = serial.Serial('/dev/ttyS0', 115200, timeout=5)
        ser.write("AT+CICCID\r".encode())
        response =  ser.readall()
        response_array = re.split(':', str(response))
        iccid = str(response_array[1]).split('\\')

        # Check the signal strength and print the condition.
        if len(str(iccid[0])) == 19 or len(str(iccid[0])) == 20:
            val = iccid[0].replace(" ", "")
            print(f"ICCID is {val}.")
        else:
            val = "ICCID incorrect format."
            print(val)

        ser.close()

        #Switch on serial connection to get IP address and for further functionality.
        subprocess.Popen('sudo pon clipper', shell=True)
        time.sleep(5)

        return val
    except:
        return "Unable to get ICCID."

get_sim_iccid()