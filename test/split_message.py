import re

def split_message(text):
    keywords = {
        'ENTRY': r"(entry|open)",
        'TP': r"(Take Profit|TP[\d]+|Take-Profit|Target)",
        'SL': r"(stop|stoploss|stop-loss|SL)"
    }

    ENTRY = []
    TP = []
    SL = []
    active_list = ''

    for i in text.split('\n'):
        if re.search(keywords.get('ENTRY'), i, re.I+re.M):
            active_list = 'ENTRY'
        elif re.search(keywords.get('TP'), i, re.I+re.M):
            active_list = 'TP'
        elif re.search(keywords.get('SL'), i, re.I+re.M):
            active_list = 'SL'

        if active_list == 'ENTRY':
            ENTRY.append(i)
        elif active_list == 'TP':
            TP.append(i)
        elif active_list == 'SL':
            SL.append(i)

    return ENTRY, TP, SL