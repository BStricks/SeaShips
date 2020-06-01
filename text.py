# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 12:46:57 2020

@author: benjamin.strickson
"""
import re
import json
import pandas as pd
from geotext import GeoText
from dateparser.search import search_dates

def no_dash(tweets):
    """remove '-' from vessel code"""
    return re.sub("-", " ", tweets).lower()


def find_vessels(tweets):
    """match vessels from U.S. Navy list"""
    vessels = pd.read_excel(r"src\services\USA_NAVY.xlsx", header=0, encoding='UTF-8')
    vessels['name'] = [x.replace(u'\xa0', u' ') for x in vessels['name']]
    name = []
    code = []
    shipType = []
    tweets2 = no_dash(tweets)
    for i in range(0,len(vessels)):
        cell_c = no_dash(vessels.iloc[i]['code'])
        cell_n = no_dash(vessels.iloc[i]['name'])
        if cell_c in tweets2 or cell_n in tweets2:
            code.append(cell_c)
            name.append(cell_n)
            shipType.append(vessels.iloc[i]["type"])
    if len(name) > 0:        
        return name[0], code[0], shipType[0]
    return None, None, None


def find_action(tweets):
    """search text for direction of ship travel"""
    in_list = ["entering", "into", "inbound", "arriving", "anchoring"]
    out_list = ["leaving", "outbound"]
    for i in in_list:
        if i in tweets:
            return "in"
    for i in out_list:
        if i in tweets:
            return "out"
    return None

def find_dates(tweets):
    """search text for dates and filter by correct format"""
    mod_string = re.sub("\#[\w\_]+","",tweets)
    mod_string = re.sub("[\(\[].*?[\)\]]","",mod_string)
    date = search_dates(mod_string)
    if date:
      date = [x[1] for x in date][0]
      return date
    return None


def find_locations(tweets):
    """search text for places"""
    places = GeoText(tweets).cities
    places2 = [x for x in places if x in [
        "San Diego", "Norfolk"]]   
    if len(places2) > 0:
        return places2[0]
    return None


def text_extraction(tweet):
    """function to extract entities and return JSON object"""
    vessel_dictionary = {"LOCATION":None, "DATE":None, "VESSEL_NAME":None,
                            "VESSEL_CODE":None, "VESSEL_TYPE": None, "VESSEL_DIRECTION":None}
    vessel_dictionary["LOCATION"] = find_locations(tweet)
    vessel_dictionary["DATE"] = find_dates(tweet)
    vessel_dictionary["VESSEL_DIRECTION"] = find_action(tweet)
    try:
        vessel = find_vessels(tweet)
        vessel_dictionary["VESSEL_NAME"] = vessel[0]
        vessel_dictionary["VESSEL_CODE"] = vessel[1]
        vessel_dictionary["VESSEL_TYPE"] = vessel[2]
    except:
        pass

    return vessel_dictionary