import emoji, regex
from . import regexstrings as rs
from . import error

class messageParser(object):
    
    def __init__(self):
        pass
    
    @staticmethod
    def __remove_emojis(text):
        """
        remove all emojis from a text, returns str
        """
        try:
            return emoji.get_emoji_regexp().sub(r'', text.decode('utf8'))
        except AttributeError:
            return emoji.get_emoji_regexp().sub(r'', text)

    @staticmethod
    def __find_pair(text):
        """
        Finds the trading pair from a string. Supported markets are defined in the regex strings. 
        Returns str, ex BTC/USDT
        """
        try:
            # Match pair
            pair = regex.findall(rs.REGEX_CRYPTO_PAIR, text)[0]
            # remove special chars
            pair = regex.sub(rs.REGEX_CRYPTO_PAIR_SPECIAL, '', pair)
            # remove "\ufe0f" - bug?
            pair = regex.sub(r"\ufe0f", '', pair)
            # add slash to pair
            pair = regex.split(rs.REGEX_CRYPTO_PAIR_SLASH, pair)
            pair = list(filter(None, pair))
            pair = pair[0].split(pair[1])[0] + '/' + pair[1]


            return pair
        except IndexError:
            raise error.NoPairFound

    @staticmethod
    def __get_percent(text):
        """
        Checks if message comes with a predefined % value
        """
        x = regex.split(rs.REGEX_DETECT_PERCENTAGE, text, flags=regex.I+regex.M)
        if len(x) > 1:
            return x[0], x[1]
        elif len(x) == 1:
            return x[0], None
        else: 
            return None, None

    @staticmethod
    def __split_message(text):
        """
        Split the message to three arrays. Splitting is based on keywords for entry, tp and sl
        """      
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
            if regex.search(keywords.get('ENTRY'), i, regex.I+regex.M):
                active_list = 'ENTRY'
            elif regex.search(keywords.get('TP'), i, regex.I+regex.M):
                active_list = 'TP'
            elif regex.search(keywords.get('SL'), i, regex.I+regex.M):
                active_list = 'SL'

            if active_list == 'ENTRY':
                ENTRY.append(i)
            elif active_list == 'TP':
                TP.append(i)
            elif active_list == 'SL':
                SL.append(i)

        return ENTRY, TP, SL

    @staticmethod
    def __get_values_from_message(text):
        """
        Get all the important values from the signal after splitting the message
        """

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
        splitted_message = messageParser.__split_message(text)

        # create dict from splitted message
        preprocessing = {
            'entry': splitted_message[0],
            'tp': splitted_message[1],
            'sl': splitted_message[2]
        }

        for i in preprocessing:
            for j in preprocessing.get(i):
                # checks if keyword zone is in - Zone + % isn't supported
                is_zone = regex.search(rs.REGEX_MATCH_ZONE, j, flags=regex.I+regex.M)
                # ensures element contains float
                float_in = regex.search(rs.REGEX_MATCH_FLOAT, j, flags=regex.I+regex.M)
                
                if is_zone:
                    # match first two numbers in zone call
                    ### debug
                    zone_start, zone_end, *_ = regex.findall(rs.REGEX_MATCH_FLOAT, j)
                    # add zone as one point but with keyword "-" and percent 100
                    signal[i]['point'] = [f'{zone_start[0]}-{zone_end[0]}']
                    signal[i]['percent'] = [100]
                
                elif float_in:
                    point, percent = messageParser.__get_percent(j)
                    # remove potential stuff at the end of the target
                    clean_string = regex.split(pattern=rs.REGEX_REMOVE_AFTER_PERCENTAGE, string=point, flags=regex.I+regex.M )[0]
                    # get only value
                    clean_string_reg = regex.findall(pattern=rs.REGEX_DETECT_VALUES_SINGLE, string=clean_string, flags=regex.I+regex.M)
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
                raise error.ParseError

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
                    raise error.NoEntryFound
                elif i == 'tp':
                    raise error.NoTakeProfitFound

        return signal
        

    def parse_message(self, text):
        """
        Parses the message, returns signal for trader
        """
        self.text = messageParser.__remove_emojis(text).upper()

        self.pair = messageParser.__find_pair(text)

        self.signal = messageParser.__get_values_from_message(text)

        self.signal['pair'] = self.pair
        
        return self.signal