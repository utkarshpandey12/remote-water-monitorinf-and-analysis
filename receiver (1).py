 # Python script to read and send data from sensor and updating
# the values to the parse server
import serial
import time
import jsonlib,http.client
import datetime
from collections import deque
ser = serial.Serial('/dev/ttyACM0',115200)
data = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct",
        "nov","dec"]
print(ser.name)
month = 0
#LAST 7 DAYS USAGE ARRAY INITIALISE 
for i in range(7):
    weekly.append(0)
for i in range(30):
    monthly.append(0)
# Data placeholder to be created which store the data like usage , monthly, weekly , yearly  of all the users
# to be sent to the server. This runs only once so make sure you have updated the project table before installation
users={}
connection = http.client.HTTPConnection('18.217.240.250', 80)
connection.connect()
connection.request('GET', '/parse/classes/LANDTUSAGE', '', {
       "X-Parse-Application-Id": "0bfc45c8be2b2e93f018041ff949fe6d09233c0a",
       "X-Parse-REST-API-Key": "avbs"
     })
result = jsonlib.loads(connection.getresponse().read())
for keys,values in result.items():
    for i in values:
        users[i["objectId"]] = {"deviceID":i["deviceID"],"kitchen":i["Kitchen"],
                              "bathroom":i["Bathroom"],"others":i["Misc"],
                              "week":i["week"],"yearly":i["yearly"][0],
                              "monthly":i["monthly"]}
for key,value in users.items():
    for keys,values in value.items():
        if keys=="week" or keys=="monthly":
            for i in range(len(values)):
                values[i] = float(values[i])
        elif keys=="yearly":
            for keyed,valued in values.items():
                valued[0] = float(valued[0])        
# Main loop begins    
while True:
    x = datetime.datetime.now()
    # When year changes then refresh the yearly usage json 
    if x.month==1 and x.day==1 and x.hour==0 and x.minute==0 and x.second in [0,1,2,3,4,5,6,7,8,9,10]:
        for keys,values in user.items():
            for key,value in values.items():
                if key=="yearly":
                    value = {"jan":[0],"feb":[0],"mar":[0],"apr":[0],"may":[0],"jun":[0],
                             "jul":[0],"aug":[0],"sep":[0],"oct":[0],"nov":[0],"dec":[0]}
    #checking if its time to reset the usage variable and other parameters while co-ordinator is in IDLE state 
    if x.hour in [11] and x.minute in [59] and x.second in [0,1,2,3,4,5,6,7,8,9,10]:    
        for keys,values in users.items():
            for key,value in values.items():
                if key=="kitchen" or key=="bathroom" or key=="others":
                    value = 0
                elif key=="week" or key=="monthly":
                    value.pop(0)
                    value.append(0)
                    
    # If data comes to co-ordinator then read it from serial and update the server
    while ser.in_waiting:
        if x.month==1 and x.day==1 and x.hour==0 and x.minute==0 and x.second in [0,1,2,3,4,5,6,7,8,9,10]:
        for keys,values in user.items():
            for key,value in values.items():
                if key=="yearly":
                    value = {"jan":[0],"feb":[0],"mar":[0],"apr":[0],"may":[0],"jun":[0],
                             "jul":[0],"aug":[0],"sep":[0],"oct":[0],"nov":[0],"dec":[0]}
        # Server url building for project class            
        request_address = "/parse/classes/LANDTUSAGE/"
        # Checking if its time to reset the usage variables and other paaameters while co-ordinator is reading the data 
        if (datetime.datetime.now().hour in [11]) and (datetime.datetime.now().minute in [59]) and (datetime.datetime.now().second in [0,1,2,3,4,5,6,7,8,9,10]):
            for keys,values in users.items():
                for key,value in values.items():
                    if key=="kitchen" or key=="bathroom" or key=="others":
                        value = 0
                    elif key=="week" or key=="monthly":
                        value.pop(0)
                        value.append(0)
        # serial data 
        data = ser.readline().strip()
        strcmp = str(data.decode('utf8'))
        device_id = strcmp[0:11]
        inlet = int(strcmp[12:])
        #comment the next line. Used for debugging
        print(device_id,inlet)
        # Checking the source of data i.e whether kitchen  , bathroom or other source
        if device_id[-1]=="K":
            users[device_id[:-1]]["kitchen"] = users[device_id[:-1]]["kitchen"]+ inlet
            print(users[device_id[:-1]]["kitchen"])
        elif device_id[-1]=="B":
            users[device_id[:-1]]["bathroom"] = users[device_id[:-1]]["bathroom"]+ inlet
            print(users[device_id[:-1]]["bathroom"])
        elif device_id[-1]=="M":
            users[device_id[:-1]]["others"] = users[device_id[:-1]]["others"]+ inlet
            print(users[device_id[:-1]]["others"])
        try:
            # Building url for rest api according the device id 
            request_address = request_address + device_id[:-1]
            if device_id[-1]=="K":
                # Server url and port and establishing connection with the server to update values using rest api
                connection = http.client.HTTPConnection('18.217.240.250',80)
                connection.connect()
                connection.request('PUT', request_address, jsonlib.dumps({"Kitchen":users[device_id[:-1]]["kitchen"] }), {"X-Parse-Application-Id": "0bfc45c8be2b2e93f018041ff949fe6d09233c0a","X-Parse-REST-API-Key": "avbs","Content-Type": "application/json"})
                result = jsonlib.loads(connection.getresponse().read())
            elif device_id[-1] == "B":
                connection = http.client.HTTPConnection('18.217.240.250',80)
                connection.connect()
                connection.request('PUT', request_address, jsonlib.dumps({"Bathroom": users[device_id[:-1]]["bathroom"]}), {"X-Parse-Application-Id": "0bfc45c8be2b2e93f018041ff949fe6d09233c0a","X-Parse-REST-API-Key": "avbs","Content-Type": "application/json"})
                result = jsonlib.loads(connection.getresponse().read())
            elif device_id[-1] == "M":
                connection = http.client.HTTPConnection('18.217.240.250',80)
                connection.connect()
                connection.request('PUT', request_address, jsonlib.dumps({"Misc": users[device_id[:-1]]["others"]}), {"X-Parse-Application-Id": "0bfc45c8be2b2e93f018041ff949fe6d09233c0a","X-Parse-REST-API-Key": "avbs","Content-Type": "application/json"})
                result = jsonlib.loads(connection.getresponse().read())
            # Check if the connection was successfull or not which can also be tested from the try and catch block which is implemented
            # to check if the internet is available or not.
            for key,value in result.items():
                if key=="updatedAt":
                    print("Daily usage data updated")
                else:
                    print('Some Error occured while updating the server with daily usage data')
                    print(result)
                    
            users[device_id[:-1]]["week"][-1] = (users[device_id[:-1]]["kitchen"]+users[device_id[:-1]]["bathroom"]+users[device_id[:-1]]["others"])/1000     
            #weekly[-1] = (per_day_usage_kitchen + per_day_usage_bathroom + per_day_usage_misc)/1000
            users[device_id[:-1]]["monthly"][-1] = (users[device_id[:-1]]["kitchen"]+users[device_id[:-1]]["bathroom"]+users[device_id[:-1]]["others"])/1000 
            #monthly[-1] = (per_day_usage_kitchen + per_day_usage_bathroom + per_day_usage_misc)/1000
            month = datetime.datetime.now().month
            value = data[month-1]
            users[device_id[:-1]]["yearly"][value][0] = users[device_id[:-1]]["yearly"][value][0] + (inlet)/1000
            #yearly[value][0] = yearly[value][0] + (inlet)/1000
            connection = http.client.HTTPConnection('18.217.240.250', 80)
            connection.connect()
            connection.request('PUT', request_address, jsonlib.dumps({"week":users[device_id[:-1]]["week"]}), {
                                "X-Parse-Application-Id": "0bfc45c8be2b2e93f018041ff949fe6d09233c0a",
                                "X-Parse-REST-API-Key": "avbs","Content-Type": "application/json"})
            result = jsonlib.loads(connection.getresponse().read())
            for key,value in result.items():
                if key=="updatedAt":
                    print("weekly usage data updated")
                else:
                    print('Some Error occured while updating the server with weekly usage data')
                    print(result)
            connection = http.client.HTTPConnection('18.217.240.250', 80)
            connection.connect()
            connection.request('PUT', request_address, jsonlib.dumps({"monthly":users[device_id[:-1]]["monthly"]}), {
                                "X-Parse-Application-Id": "0bfc45c8be2b2e93f018041ff949fe6d09233c0a",
                                "X-Parse-REST-API-Key": "avbs","Content-Type": "application/json"})
            result = jsonlib.loads(connection.getresponse().read())
            for key,value in result.items():
                if key=="updatedAt":
                    print("monthly usage data updated")
                else:
                    print("Some error occured while updating the server with monthly usage data")
                    print(result)
            connection = http.client.HTTPConnection('18.217.240.250', 80)
            connection.connect()
            connection.request('PUT', request_address, jsonlib.dumps({"yearly":[users[device_id[:-1]]["yearly"]]}), {
                                "X-Parse-Application-Id": "0bfc45c8be2b2e93f018041ff949fe6d09233c0a",
                                "X-Parse-REST-API-Key": "avbs","Content-Type": "application/json"})
            result = jsonlib.loads(connection.getresponse().read())
            for keys,values in result.items():
                if keys=="updatedAt":
                    print("yearly usage data updated")
                else:
                    print("Some error occured while updating server with yearly usage data")
                    print(result)
            
        except Exception as e:
            #WRITE YOOR LOGIC HERE IN CASE INTERNET CONNECTION FAILS OR IS UNAVAILABLE 
            print(e.message)
            
                
