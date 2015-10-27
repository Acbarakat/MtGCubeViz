import os
from json import loads
import codecs

try:
    from mtg import *
    from mtg.Card import Card
    from common import urlopen
except ImportError:
    from Card import Card
    from __init__ import *

    import sys
    fpath, _ = os.path.split(__file__)
    sys.path.append(os.path.join(fpath, ".."))
    from common import urlopen

class CardDatabase(list):
    """description of class"""

    def __init__(self, uri="AllSets.json", data=None):
        if data:
            self.extend(data)
            return

        card_database = None
        if os.path.isfile(uri):
            if os.path.exists(uri):
                with codecs.open(uri, "r", "utf-8") as f:
                    card_database = f.read()
            else:
                print("Cannot find %s" % uri)
        
        if not card_database:
            card_database = urlopen(ALL_SETS_JSON).read()
            card_database = card_database.decode("utf8")
        
        card_database = loads(card_database, encoding = "utf8")

        for k,v in card_database.items():
            if "cards" in v:
                for i in v["cards"]:
                    i["printings"] = [ k ]
                    self.append( Card(i) )
            else:
                self.append( Card(v) )

    def sort(self, key=None, reverse=False):
        data = sorted(self, key = key, reverse = reverse)
        return CardDatabase(data=data)

    def findByName(self, cardname):
        #return list(filter(lambda card: card.name == cardname.encode('utf-8'), self))
        data = list(filter(lambda card: card.name == cardname, self))
        return CardDatabase(data=data)

    def filterDuplicates(self):
        data = []
        names = []

        for card in self:
            if card.name in names:
                continue

            data.append(card)
            names.append(card.name)
        
        return CardDatabase(data=data) 

    def filterInNameList(self, cardname_list):
        data = list(filter(lambda card: card.name in cardname_list, self))
        return CardDatabase(data=data)

    def filterMultiColorOnly(self):
        data = list(filter(lambda card: len(card.colors) > 1, self))
        return CardDatabase(data=data)

    def filterByColor(self, color):
        data = list(filter(lambda card: color in card.colors, self))
        return CardDatabase(data=data)

    def filterByNotColor(self, color):
        data = list(filter(lambda card: color not in card.colors, self))
        return CardDatabase(data=data)

    def filterByRarity(self, rarity):
        data = list(filter(lambda card: rarity == card.rarity, self))
        return CardDatabase(data=data)


if __name__ == "__main__":
    import sys
    from pprint import pprint
    from PyQt5.QtGui import QApplication

    app = QApplication(sys.argv)
    x = CardDatabase()
    print(len(x))
    x = x.filterMultiColorOnly()
    print(len(x))
    x = x.filterByColor("Red")
    x = x.filterByColor("White")
    x = x.filterByColor("Black")
    x = x.filterByNotColor("Green")
    x = x.filterByNotColor("Blue")
    pprint(x)