import regex

__markets = ['USDT', 'BTC', 'ETH', 'BUSD', 'USD', 'BNB', 'TRX', 'XRP']

REGEX_CRYPTO_PAIR = r"(\w+[\S\s]{0,3}?(?:" + '|'.join(__markets) + r")(?![\S\s]?(?:" + '|'.join(__markets) + r")))"
# ex. (\w+[\S\s]{0,3}?(?:USDT|BTC|ETH|BUSD|USD|BNB|TRX|XRP)(?![\S\s]?(?:USDT|BTC|ETH|BUSD|USD|BNB|TRX|XRP)))

REGEX_CRYPTO_PAIR_SPECIAL = r"([\W]|_)"

REGEX_CRYPTO_PAIR_SLASH = r"([\w]+(" + '|'.join(__markets) + r"))"
# ex. [\w]+(USDT|BTC|ETH|BUSD|USD|BNB|TRX|XRP)

REGEX_DETECT_SIGNAL_VALUES = r"(?:^|(?<=[-:)\ ][\ \W]?))([0-9]+([.][0-9]*)?|[.][0-9]+)$"

REGEX_DETECT_PERCENTAGE = r"([0-9]+([.][0-9]*)?|[.][0-9]+)%"

REGEX_MATCH_FLOAT = r"([0-9]+([.][0-9]*)?|[.][0-9]+)"

REGEX_REMOVE_AFTER_PERCENTAGE = r"[\W\D]*[\s]*$"

REGEX_MATCH_ZONE = r"(between|zone)"