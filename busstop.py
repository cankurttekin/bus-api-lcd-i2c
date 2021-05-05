#!/usr/bin python3
# -*- coding: utf-8 -*-

# 12/02/2020 bus stop passenger information screen

import time
import datetime
import requests
import json
import I2C_LCD_driver
from gpiozero import CPUTemperature
cpu = CPUTemperature()
mylcd = I2C_LCD_driver.lcd()

# turkish "Ç" character.
turkcec = [
    [0b01110,
     0b10001,
     0b10000,
     0b10000,
     0b10000,
     0b10001,
     0b01110,
     0b00100],
]

mylcd.lcd_display_string("INT BAGLANTISI", 1)
mylcd.lcd_display_string("KURULDU", 2)
time.sleep(1.5)
mylcd.lcd_clear()

def get_otobus(durak):
    parsed = None
    url = "https://service.kentkart.com//api/bus/closest?accuracy=0&authType=1&busStopId=" + durak + "&lang=tr&lat=0&lng=0&nfcSupport=0&region=007&token='PERSONAL TOKEN HERE'&version=WEB_4.0_2"
    response = requests.get(url)
    data = response.text
    parsed = json.loads(data)
    otobusler = []
    for i in range(len(parsed["busList"])):  # appends buses to .
        if parsed["busList"][i]["disabledPerson"] == 0:  # checks if it can carry disabled passenger.
            otobusler.append(
                str(parsed["busList"][i]["displayRouteCode"]) + " " + parsed["busList"][i]["stopDiff"] + "drk " +
                parsed["busList"][i]["timeDiff"] + "dk " + "E")
        else:
            otobusler.append(
                str(parsed["busList"][i]["displayRouteCode"]) + " " + parsed["busList"][i]["stopDiff"] + "drk " +
                parsed["busList"][i]["timeDiff"] + "dk")
    return otobusler

while True:
    try:
        while True:
            kentkart = get_otobus("BUS STOP ID HERE")
            starttime = time.time()
            while len(kentkart) > 0:
                for x in range(0, len(kentkart), 2):
                    mylcd.lcd_clear()
                    # first line of lcd
                    if kentkart[x][0] == "Ç": # all of the bus ids start with 'Ç' here so no need to check actually
                        mylcd.lcd_load_custom_chars(turkcec)
                        mylcd.lcd_write(0x80)
                        mylcd.lcd_write_char(0)
                        mylcd.lcd_display_string(kentkart[x][1:], 1, 1)
                    else:
                        mylcd.lcd_display_string(kentkart[x], 1)
                    if x == len(kentkart) - 1:
                        time.sleep(11)
                        break
                    # second line of lcd
                    if kentkart[x + 1][0] == "Ç": 
                        mylcd.lcd_load_custom_chars(turkcec)
                        mylcd.lcd_write(0xc0)
                        mylcd.lcd_write_char(0)
                        mylcd.lcd_display_string(kentkart[x + 1][1:], 2, 1)
                    else:
                        mylcd.lcd_display_string(kentkart[x + 1], 2)
                    time.sleep(11)

                if (
                        time.time() - starttime) >= 11.0:  # api refreshes busses location every 11seconds so to update we check if its been 11secs.
                    starttime = time.time()
                    kentkart = get_otobus("BUS STOP ID HERE")
            else:
                mylcd.lcd_clear()
                while True: # display date, time and cpu temp while theres no bus to show.
                    kentkart = get_otobus("BUS STOP ID HERE")
                    mylcd.lcd_display_string(time.strftime("%d/%m/%Y"), 1,3)
                    mylcd.lcd_display_string(time.strftime("%H:%M:%S" + " T:" + "{:.1f}".format(cpu.temperature)), 2)
                    mylcd.lcd_write_char(223,1)
                    time.sleep(1)
                    if len(kentkart) > 0:
                        break
                continue

    except requests.exceptions.ConnectionError:
        mylcd.lcd_display_string("INTERNET        ", 1)
        mylcd.lcd_display_string("BAGLANTISI YOK  ", 2)
        continue
    except:
        mylcd.lcd_display_string("BIR SORUN OLDU  ", 1)
        mylcd.lcd_display_string("AMA NE BILMIYORM", 2)
        continue
