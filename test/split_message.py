import re

text='''
⚡️⚡️WAVESUSDT⚡️⚡️ 
Exchange: Binance Futures 
Leverage: Isolated(10x) 

Entry Orders: 
9.5161 

Take Profit Orders: 
1)9.55892 
2)9.60174 
3)9.65408 
4)9.89674 
5)10.46771 

Stop-loss Orders:  
9.23062 

Direction: Long
'''


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

print(ENTRY)
print(TP)
print(SL)