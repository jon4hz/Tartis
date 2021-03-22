import psycopg2
import decimal

conn = psycopg2.connect(dsn='postgres://tartis:tmppassword@localhost:5432/tartis')

cur = conn.cursor()

cur.execute(
    '''
    SELECT trades.id, symbol, direction, exchange, entries.price, entries.percent, entries.filled, tps.price, tps.percent, tps.filled, sls.price, sls.percent, sls.filled, telegram_message_id FROM trades

    LEFT OUTER JOIN entries ON trades.id=entries.trade_id
    LEFT OUTER JOIN tps ON trades.id=tps.trade_id
    LEFT OUTER JOIN sls ON trades.id=sls.trade_id

    WHERE   close_time IS NULL AND 
            channel_trade = TRUE AND 
            symbol = 'XMR/USDT'
    '''
)
data = cur.fetchall()
trades = {}
for i in data:
    try:
        offset = 0
        for j in ['entries', 'tps', 'sls']:
            if sum(trades[i[0]][j]['percent']) != 100:
                trades[i[0]][j]['point'].append(i[4+offset])
                trades[i[0]][j]['percent'].append(i[5+offset])
                trades[i[0]][j]['filled'].append(i[6+offset])
            offset += 3

    except KeyError:
        trades[i[0]] = {
            'symbol': i[1],
            'direction': i[2],
            'exchange': i[3],
            'entries': {
                'point': [],
                'percent': [],
                'filled': []
            },
            'tps': {
                'point': [],
                'percent': [],
                'filled': []
            },
            'sls': {
                'point': [],
                'percent': [],
                'filled': []
            },
        }

price = 1000
print(trades)
for trade in trades:
    for target_type in ['entries', 'tps', 'sls']:
        for i in range(len(trades[trade][target_type]['point'])):
            if not trades[trade][target_type]['filled'][i]:
                if target_type == 'entries' and price > trades[trade][target_type]['point'][i]:
                    print(f'Entry target {i+1} reached')
                    # update database
                elif target_type == 'tps' and price > trades[trade][target_type]['point'][i]:
                    print(f'TP target {i+1} reached')
                    # update database
                elif target_type == 'sls' and price > trades[trade][target_type]['point'][i]:
                    print(f'TP target {i+1} reached')
                    # update database