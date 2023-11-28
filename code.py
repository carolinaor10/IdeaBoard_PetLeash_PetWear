# Referencia para DHT11
# SPDX-FileCopyrightText: 2017 Limor Fried for Adafruit Industries
# Modificado por Jefry Valverde y Gabriela Urbina
# Universidad CENFOTEC
#
# Referencia para SI1145
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 Carter Nelson for Adafruit Industries
# SPDX-License-Identifier: Unlicense

import ssl
import time
import keypad
import adafruit_dht
import board
from ideaboard import IdeaBoard
from adafruit_rtttl import play
import adafruit_requests as requests
import socketpool
import wifi
import sys
import adafruit_si1145

password = "rokica30"

#**********WIFI*************
socket = socketpool.SocketPool(wifi.radio)
https = requests.Session(socket, ssl.create_default_context())

print("Connecting...")	
wifi.radio.connect("Ortiz ", password) #redes de 2.4G
print("Connected to Wifi!")
print("")

#***************************

ib = IdeaBoard()
dht = adafruit_dht.DHT11(board.IO32)
keys=keypad.Keys((board.IO33,),value_when_pressed=False)
estado=False
i2c = board.I2C() # uses board.SCL and board.SDA
si1145 = adafruit_si1145.SI1145(i2c)

#*********CODE************

print("---PETS INN IDEABOARD BY PETWEAR---")
print("")

while True:
    try:
        
        temperature = dht.temperature
        humidity = dht.humidity
        event = keys.events.get()
        song = "itchy:d=8,o=6,b=160:c,a5,4p,c,a,4p,c,a5,c,a5,c,a,4p,p,c,d,e,p,e,f,g,4p,d,c,4d,f,4a#,4a,2c7"
        uv_index = si1145.uv_index
        
        
        #BUTTON
        if event:
            if event.pressed:
                estado= not estado
                if estado:
                    ib.pixel=(255, 0, 255)
                    play(board.IO18, "end:d=8,o=6,b=160:c,a5")
                    print("")
                    print("Good bye!")
                    ib.pixel=(0,0,0)
                    sys.exit()
                    
        #**********REPL***********
        print("Temp: {:.1f} *C \t Humidity: {}%".format(temperature, humidity))
        print("UV Index = {}".format(uv_index))
        time.sleep(10)
        
        
        #***********POST**********
        URL_POST = "https://webapi20231003203317.azurewebsites.net/api/IDEA/Create"
        
        data = {'id': 0,
                'idPet': 223, 
                'temperature': temperature,
                'humidity': humidity,
                'ultraViolet': si1145.uv_index,
                }
        
        result = https.post(URL_POST, json = data)
        print("RESULTADO_POST", result.json())
        
        
        #*******VALIDATION********
        if not (-90 <= temperature <= 60 and 0 <= humidity <= 100): #60 100
            ib.pixel = (255, 0, 0)
            play(board.IO18, song)
            time.sleep(2)
        
        #ULTRAVIOLET VALIDATION
        if not (0 <= uv_index <= 5): #BAJO 0-2, MODERADO 3-5, ALTO 6-7, MUY ALTO 8-10, EXTREMO 11+
            ib.pixel = (255, 0, 0)
            play(board.IO18, song)
            time.sleep(2)
                    
    
    except RuntimeError as e:
        # Reading doesn't always work! Just print error and we'll try again
        print("Reading from DHT failure: ", e.args)

    time.sleep(1)