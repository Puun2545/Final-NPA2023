#######################################################################################
# FirstName/Surname: Puun Vachangngern
# Student ID: 64070184
# Github repository URL: https://github.com/Puun2545/Netper-2024
#######################################################################################
# Instruction
# Reads README.md in https://github.com/chotipat/NPA2023-Final-Example for more information.
#######################################################################################
 
#######################################################################################
# 1. Import libraries for API requests, JSON formatting, and time.

import requests
import json
import time

#######################################################################################
# 2. Assign the Webex hard-coded access token to the variable accessToken.

accessToken = "Bearer MWRkYWU5N2UtZjk4MS00ODZhLTg1N2YtMWRhY2MxZDg1ODI5YWIxOTFlMDYtZmE0_P0A1_a61a0b2b-feba-43a3-8a20-e8cc10a43c9a" 

#######################################################################################
# 3. Prepare GetParameters to get the latest message for messages API.

# Defines a variable that will hold the webx roomId 
roomIdToGetMessages = "Y2lzY29zcGFyazovL3VzL1JPT00vZjBkZjY0NDAtYWU5Yi0xMWVlLTg5MGMtMGQzNjUwOTJlMmUy" # ID ห้องที่จะให้รับข้อความ

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    GetParameters = {
                            "roomId": roomIdToGetMessages,
                            "max": 1 #get message มา 1 อัน
                        }

#######################################################################################
# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get("https://webexapis.com/v1/messages",
                         params = GetParameters,
                         headers = {"Authorization": accessToken}
                    )
    # verify if the retuned HTTP status code is 200/OK Get API ได้มั้ย
    if not r.status_code == 200:
        raise Exception( "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
    
    # get the JSON formatted returned data แปลงข้อมูลที่ได้มาเป็น json
    json_data = r.json()
    # check if there are any messages in the "items" array มีข้อความมั้ย
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")  #ถ้าไม่มีข้อความในห้องให้แสดงข้อความว่าไม่มีข้อความในห้อง
    
    # store the array of messages
    messages = json_data["items"] #เก็บข้อความที่ได้มา

    # store the text of the first message in the array
    message = messages[0]["text"] #เก็บข้อความตัวแรกที่ได้มา
    
    # Print the received message to verify the values แสดงข้อความที่ได้มา
    print("Received message: " + message)
    
    # check if the text of the message starts with the magic character "/" and yourname followed by a location name
    # e.g.  "/chotipat San Jose"
    # /puun LA
    space = message.find(" ") #หาช่องว่าง ไอนี่กูเล่นเอง
    
    if message.find("/") == 0:
        # extract name of a location (city) where we check for GPS coordinates using the OpenWeather Geocoding API
        # Enter code below to hold city name in location variable.
        # For example location should be "San Jose" if the message is "/chotipat San Jose".
        name = message[1:space] #เอาชื่อมาเก็บ
        location = message[space+1:] #เอาชื่อเมืองมาเก็บ
        # Debug print
        print("Location: " + location)


#######################################################################################     
# 5. Prepare openweather Geocoding APIGetParameters..
        # Openweather Geocoding API GET parameters:
        # - "q" is the the location to lookup
        # - "limit" is always 1
        # - "key" is the openweather API key, https://home.openweathermap.org/api_keys
        apiKey = "72afa9302b8758eb760d48c03122eddd" #ใส่ api key ของ openweather

        # Set the openweatherGeoAPIGetParameters with the location and the API key 
        # ใส่ค่าที่ได้มาจากข้อ 4 และ api key ของ openweather
        openweatherGeoAPIGetParameters = {
            "q": location,
            "limit": 1,
            "appid": apiKey,
        }
        # Debug print
        print(openweatherGeoAPIGetParameters)
        
#######################################################################################       
# 6. Provide the URL to the OpenWeather Geocoding address API.
        # Get location information using the OpenWeather Geocoding API geocode service using the HTTP GET method
        # ใช้คำสั่ง get ของ requests ไปที่ url ของ openweather และใส่ค่าที่ได้มาจากข้อ 5
        r = requests.get("http://api.openweathermap.org/geo/1.0/direct", 
                             params = openweatherGeoAPIGetParameters
                        )
        # Verify if the returned JSON data from the OpenWeather Geocoding API service are OK
        json_data = r.json()
        # check if the status key in the returned JSON data is "0"
        if not r.status_code == 200:
            raise Exception("Incorrect reply from OpenWeather Geocoding API. Status code: {status} | Message: {message} ".format(status=r.status_code, message=r.text))
        
        # Validate if the returned JSON data from the OpenWeather Geocoding API service are EMPTY
        # Location not found
        if len(json_data) == 0:
            requests.post("https://webexapis.com/v1/messages",
                          headers = {"Authorization": accessToken, "Content-Type": "application/json"},
                          data = json.dumps({"roomId": roomIdToGetMessages, "text": "Location: {location} not found! \nPlease try others".format(location=location)})
                         )
            continue


#######################################################################################
# 7. Provide the OpenWeather Geocoding key values for latitude and longitude.
        # Set the lat and lng key as retuned by the OpenWeather Geocoding API in variables
        # ใส่ค่าที่ได้มาจากข้อ 6 ในตัวแปร locationLat และ locationLng
        locationLat = json_data[0].get("lat") #เป็นการ get ค่าจาก json ที่ได้มาโดยใช้ key ที่เราต้องการ
        locationLng = json_data[0].get("lon") #เป็นการ get ค่าจาก json ที่ได้มาโดยใช้ key ที่เราต้องการ

#######################################################################################
# 8. Prepare openweatherAPIGetParameters for OpenWeather API, https://openweathermap.org/api; current weather data for one location by geographic coordinates.
        # Use current weather data for one location by geographic coordinates API service in Openweathermap
        # ใส่ค่าที่ได้มาจากข้อ 7 และ api key ของ openweather
        openweatherAPIGetParameters = {
                                "lat" : locationLat,
                                "lon" : locationLng,
                                "appid": apiKey,
                            }
        # Debug print
        print(openweatherAPIGetParameters)

#######################################################################################
# 9. Provide the URL to the OpenWeather API; current weather data for one location.
        # Get current weather data for one location by geographic coordinates 
        # using the OpenWeather API service using the HTTP GET method
        rw = requests.get("https://api.openweathermap.org/data/2.5/weather"
                          , params = openweatherAPIGetParameters
                        )
        json_data_weather = rw.json()

        if not "weather" in json_data_weather:
            raise Exception("Incorrect reply from openweathermap API. Status code: {}. Text: {}".format(rw.status_code, rw.text))

#######################################################################################
# 10. Complete the code to get weather description and weather temperature
        # ใส่ค่าที่ได้มาจากข้อ 9 ในตัวแปร weather_desc และ weather_temp
        weather_desc = json_data_weather["weather"][0]["description"] #เป็นการ get ค่าจาก json ที่ได้มาโดยใช้ key ที่เราต้องการ
        weather_temp = json_data_weather["main"]["temp"] - 273.15 #เป็นการ get ค่าจาก json ที่ได้มาโดยใช้ key ที่เราต้องการ และทำการแปลงค่าจาก K เป็น C

#######################################################################################
# 11. Complete the code to format the response message.
        # Example responseMessage result: In Austin, Texas (latitude: 30.264979, longitute: -97.746598), the current weather is clear sky and the temperature is 12.61 degree celsius.
        responseMessage = "Dear {name}, \n In {location} (latitude: {locationLat}, longitute: {locationLng}), the current weather is {weather_desc} and the temperature is {weather_temp:.2f} degree celsius.\n" \
            .format(name=name,location=location, locationLat=locationLat, locationLng=locationLng, weather_desc=weather_desc, weather_temp=weather_temp)

#######################################################################################
# 12. Complete the code to post the message to the Webex Teams room.         
        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        HTTPHeaders = { 
                             "Authorization": accessToken,
                             "Content-Type": "application/json"
                           }

        # The Webex Teams POST JSON data
        # - "roomId" is is ID of the selected room
        # - "text": is the responseMessage assembled above
        PostData = {
                            "roomId": roomIdToGetMessages,
                            "text": responseMessage
                        }
        # Post the call to the Webex Teams message API.
        # ใช้คำสั่ง post message ไปที่ url ของ webex และใส่ค่าที่ได้มาจากข้อ 11
        r = requests.post( "https://webexapis.com/v1/messages", 
                              data = json.dumps(PostData), 
                              headers = HTTPHeaders
                         )
        
        # Verify if the returned JSON data from the Webex Teams API service are OK
        if not r.status_code == 200:
            raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
