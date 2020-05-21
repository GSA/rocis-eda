import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser
import xmltodict
import requests
import io
import matplotlib as plt        
from collections import MutableMapping 

def get_404(x):
    try:
        x = str(x).strip()
    except AttributeError as e:
        return e
    try:
        status = requests.get(x, timeout=2.0).status_code
        return status
    except:
        return 'error'


def convert_flatten(d, parent_key ='', sep ='_'): 
    items = [] 
    for k, v in d.items(): 
        new_key = parent_key + sep + k if parent_key else k 
  
        if isinstance(v, MutableMapping): 
            items.extend(convert_flatten(v, new_key, sep = sep).items()) 
        else: 
            items.append((new_key, v)) 
    return dict(items) 

def dict_depth(dic, level = 1): 
      
    if not isinstance(dic, dict) or not dic: 
        return level 
    return max(dict_depth(dic[key], level + 1) 
                               for key in dic) 
  

def sum_recursive(current_number, accumulated_sum):
    # Base case
    # Return the final state
    if current_number == 11:
        return accumulated_sum

    # Recursive case
    # Thread the state through the recursive call
    else:
        return sum_recursive(current_number + 1, accumulated_sum + current_number)

def get_url_list(root):

    url_list = []

    for i in root.iter():
        if i.tag == 'URL':
            url_list.append(i.text)
        else:
            pass
    
    return url_list