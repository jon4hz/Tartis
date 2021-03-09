import split_message
import regex, os, sys

# pretty print dicts
import json

# sys hacking for tartis import (parent folder)
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import tartis
from texts import *

perc_array = []

def get_percent(text) -> tuple:
    x = regex.split(tartis.regexstrings.REGEX_DETECT_PERCENTAGE, text, flags=regex.I+regex.M)
    if len(x) > 1:
        return x[0], x[1]
    elif len(x) == 1:
        return x[0], None
    else: 
        return None, None

# empty dict for signal
signal = {
    'entry': {
        'point': [],
        'percent': []
    },
    'tp': {
        'point': [],
        'percent': []
    },
    'sl': {
        'point': [],
        'percent': []
    }

}

# split message in entry, tp and sl
splitted_message = split_message.split_message(text4)

# create dict from splitted message
preprocessing = {
    'entry': splitted_message[0],
    'tp': splitted_message[1],
    'sl': splitted_message[2]
}

for i in preprocessing:
    for j in preprocessing.get(i):
        float_in = regex.search(tartis.regexstrings.REGEX_MATCH_FLOAT, j, flags=regex.I+regex.M)
        if float_in:
            point, percent = get_percent(j)
            # remove potential stuff at the end of the target
            clean_string = regex.split(pattern=tartis.regexstrings.REGEX_REMOVE_AFTER_PERCENTAGE, string=point, flags=regex.I+regex.M )[0]
            # get only value
            clean_string_reg = regex.findall(pattern=tartis.regexstrings.REGEX_DETECT_VALUES_SINGLE, string=clean_string, flags=regex.I+regex.M)
            # if value detected, add
            if clean_string_reg:
                signal[i]['point'].append(float(clean_string_reg[0][0]))
                # try to convert percent to float
                if percent:
                    signal[i]['percent'].append(float(percent))
                else:
                    signal[i]['percent'].append(percent)

               
# postprocessing
for i in signal:
    if len(signal[i].get('percent')) != len(signal[i].get('percent')):
        # tmp
        print("Error, could not parse signal")

    # if only 1 target, set percent to 100
    if len(signal[i].get('percent')) == 1:
        signal[i]['percent'] = [100]
    
    # split percent between targets
    elif None in signal[i].get('percent'):
        for k in range(len(signal[i].get('percent'))):
            signal[i]['percent'][k] = (100 / len(signal[i].get('percent')))
    
    # ensure percent total is 100
    else:
        perc_all = 100.
        for j in signal[i].get('percent'):
            perc_all -= j
        # if sum of all percent not 100, add/sub missing to last
        if perc_all != 0:
            signal[i]['percent'][-1] += perc_all


print(json.dumps(signal, indent=4))

## todo check for keywords like "zone" or "between"