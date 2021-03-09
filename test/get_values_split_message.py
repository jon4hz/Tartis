import split_message
import re, os, sys

# sys hacking for tartis import (parent folder)
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import tartis
from texts import *

def get_percent(text):
    print(re.findall(r"([\d])", j))

for i in split_message.split_message(text3):
    for j in i:
        print(j)
        #print(re.findall(r"([\d])", j))