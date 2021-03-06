import emoji, re
from .regexstrings import *

class messageParser(object):
    
    def __init__(self):
        pass

    # remove potential emojis from the message
    def remove_emojis(self, text):
        try:
            return emoji.get_emoji_regexp().sub(r'', text.decode('utf8'))
        except AttributeError:
            return emoji.get_emoji_regexp().sub(r'', text)


    def find_pair(self, text):
        try:
            # Match pair
            self.pair = re.findall(REGEX_CRYPTO_PAIR, text)[0]
            # remove special chars
            self.pair = ''.join(re.split(REGEX_CRYPTO_PAIR_SPECIAL, self.pair))
            # add slash to pair
            self.pair = re.split(REGEX_CRYPTO_PAIR_SLASH, self.pair)
            self.pair = list(filter(None, self.pair))
            self.pair = self.pair[0].split(self.pair[1])[0] + '/' + self.pair[1]


            return self.pair
        except IndexError:
            print("Error: Could not determine trading pair")
                

    def parse_message(self, text):
        
        self.text = self.remove_emojis(text).upper()

        self.pair = self.find_pair(text)

        return self.pair

        #return entry, take_profit, stop_loss