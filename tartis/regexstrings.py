import re

__markets = ['USDT', 'BTC', 'ETH', 'BUSD', 'USD', 'BNB', 'TRX', 'XRP']

REGEX_CRYPTO_PAIR = r"(\w+[\S\s]{0,3}?(?:" + '|'.join(__markets) + ")(?![\S\s]?(?:" + '|'.join(__markets) + ")))"
# ex. (\w+[\S\s]{0,3}?(?:USDT|BTC|ETH|BUSD|USD|BNB|TRX|XRP)(?![\S\s]?(?:USDT|BTC|ETH|BUSD|USD|BNB|TRX|XRP)))

REGEX_CRYPTO_PAIR_SPECIAL = r"([\W]|_)"

REGEX_CRYPTO_PAIR_SLASH = r"([\w]+(" + '|'.join(__markets) + "))"
# ex. [\w]+(USDT|BTC|ETH|BUSD|USD|BNB|TRX|XRP)