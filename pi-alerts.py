# -*- coding: utf-8 -*-
"""
Copyright (C) 2020  Doga Ozesmi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

Last Updated Thu Jul 18 2020
"""
import json
import requests
import time
from twilio.rest import Client
from collections import defaultdict

FEED = 'feed.json'
URL = "https://www.predictit.org/api/marketdata/all"

#Change these based on your twilio number and your phone number
SENDING_NUMBER = '+1xxxxxxxxxx'
RECEIVING_NUMBER = '+1xxxxxxxxxx'

#minutes between redundant notifications
COOLDOWN = 30

cooldown_dict = {}

#enter alerts here for now, will be parsed from a config file later
alert_dict = {"NY-16 Dem. primary margin of victory?" : {"12% to 14%" : {"option": "bestBuyYesCost", "direction" : ">", "price" : 0.99, "triggered" : False},
                                                         "14% to 16%" : {"option": "bestBuyNoCost", "direction" : "<", "price" : 0.00, "triggered" : False}}}

def download():
    response = requests.get(URL)
    with open(FEED, 'wb') as f: 
        f.write(response.content)
        

def check_price_alerts():
    global data
    for item in data['markets']:
        if(item['shortName'] in alert_dict):
            for contract in item['contracts']:
                if(contract['shortName'] in alert_dict[item['shortName']]):
                    alert = alert_dict[item['shortName']][contract['shortName']]
                    message = "Check " + item['shortName'] + " " + contract['shortName']
                    #print(alert_spec)
                    if(alert['direction'] == "<" and alert['triggered'] == False):
                        if (float(contract[alert['option']]) < alert['price']):
                            client.messages.create(from_=SENDING_NUMBER,
                               to=RECEIVING_NUMBER,
                               body=message)
                            alert['triggered'] = True
                    if(alert['direction'] == ">" and alert['triggered'] == False):
                        if (float(contract[alert['option']]) > alert['price']):
                            client.messages.create(from_=SENDING_NUMBER,
                               to=RECEIVING_NUMBER,
                               body=message)
                            alert['triggered'] = True
                    
                        
def find_negative_risk():
    global cooldown_dict
    global data
    for item in data['markets']:
        payout = 0
        for contract in  item['contracts']:
            if(contract['bestBuyNoCost'] != None):
                payout += 1-float(contract['bestBuyNoCost'])
            
        if(payout >= 1.09):
            print("************")
            print(item['name'])
            print("{:.2f}".format(payout))
        if(payout >= 1.13 and cooldown_dict[item['name']] >= COOLDOWN):
            client.messages.create(from_=SENDING_NUMBER,
                       to=RECEIVING_NUMBER,
                       body=item['shortName'] + " - " + "{:.2f}".format(payout))
            cooldown_dict.update({item['name'] : 0})

        cooldown_dict.update({item['name'] : min(COOLDOWN, cooldown_dict[item['name']] + 1)})
    
def loop():
    starttime = time.time()
    global alert_triggered
    
    while True:
        print("============")
        download()
        find_negative_risk()
        check_price_alerts()
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))
        

if __name__ == '__main__':
    global client
    global data
    
    client = Client()
    f = open(FEED,encoding="utf8")
    data = json.load(f)
    cooldown_dict = defaultdict(lambda:COOLDOWN,cooldown_dict)
    loop()
    
