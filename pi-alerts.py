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

FEED = 'feed.json'
URL = "https://www.predictit.org/api/marketdata/all"

def download():
    response = requests.get(URL)
    with open(FEED, 'wb') as f: 
        f.write(response.content) 
        
def findNegativeRisk():
    f = open(FEED,encoding="utf8")
    data = json.load(f)
    
    for item in data['markets']:
        payout = 0
        for contract in  item['contracts']:
            if(contract['bestBuyNoCost'] != None):
                payout += 1-float(contract['bestBuyNoCost'])
            
        if(payout > 1.08):
            print("************")
            print(item['name'])
            print("{:.2f}".format(payout))
    
def loop():
    
    starttime = time.time()
    while True:
        print("============")
        download()
        findNegativeRisk()
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))


if __name__ == '__main__':
    loop()
    