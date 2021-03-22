import split_message
import regex, os, sys

# pretty print dicts
import json

# sys hacking for tartis import (parent folder)
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
second_parentdir = os.path.dirname(parentdir)
sys.path.append(parentdir)
sys.path.append(second_parentdir)

# pylint: disable=import-error
import tartis
# pylint: enable=import-error
from texts import *

def get_percent(text) -> tuple:
    x = regex.split(tartis.REGEX_DETECT_PERCENTAGE, text, flags=regex.I+regex.M)
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
splitted_message = split_message.split_message(text2)

# create dict from splitted message
preprocessing = {
    'entry': splitted_message[0],
    'tp': splitted_message[1],
    'sl': splitted_message[2]
}

for i in preprocessing:
    for j in preprocessing.get(i):
        # checks if keyword zone is in - Zone + % isn't supported
        is_zone = regex.search(tartis.REGEX_MATCH_ZONE, j, flags=regex.I+regex.M)
        # ensures element contains float
        float_in = regex.search(tartis.REGEX_MATCH_FLOAT, j, flags=regex.I+regex.M)
        
        if is_zone:
            # match first two numbers in zone call
            zone_start, zone_end, *_ = regex.findall(tartis.REGEX_MATCH_FLOAT, j)
            # add zone as one point but with keyword "-" and percent 100
            signal[i]['point'] = [f'{zone_start[0]}-{zone_end[0]}']
            signal[i]['percent'] = [100]
        
        elif float_in:
            point, percent = get_percent(j)
            # remove potential stuff at the end of the target
            clean_string = regex.split(pattern=tartis.REGEX_REMOVE_AFTER_PERCENTAGE, string=point, flags=regex.I+regex.M )[0]
            # get only value
            clean_string_reg = regex.findall(pattern=tartis.REGEX_DETECT_SIGNAL_VALUES, string=clean_string, flags=regex.I+regex.M)
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
    if len(signal[i].get('point')) != len(signal[i].get('percent')):
        # tmp
        raise tartis.error.ParseError

    if signal[i].get('point'):
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
    else:
        # check if i == entry or tp
        if i == 'entry':
            raise tartis.error.NoEntryFound
        elif i == 'tp':
            raise tartis.error.NoTakeProfitFound

print(json.dumps(signal, indent=4))