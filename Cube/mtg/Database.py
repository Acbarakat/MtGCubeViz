import os
import csv
import codecs
from json import loads
from lxml import etree

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
        if data != None:
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
                    #print(i)
                    if "multiverseid" not in i:
                        continue

                    i["printings"] = [ k ]
                    self.append( Card(i) )
            else:
                self.append( Card(v) )

    def _filterByNode(self, xml_item):
        dblist = self

        if "rarity" in xml_item.attrib:
            rarity = xml_item.attrib["rarity"]

            dblist = dblist.filterByRarity(rarity)

        if "type" in xml_item.attrib:
            cardtype = xml_item.attrib["type"]

            dblist = dblist.filterByType(cardtype)

        if "color" in xml_item.attrib:
            colors = xml_item.attrib["color"]
            colors = colors.split(",")

            if colors == ['']:
                colors = []
                xml_item.attrib["color_match"] = "exact"

            for color in colors:
                dblist = dblist.filterByColor(color)

            if "color_match" in xml_item.attrib:
                match_type = xml_item.attrib["color_match"]

                if match_type == "exact":
                    dblist = dblist.filterByExactColorCount(len(colors))

        return dblist

    def sort(self, key=None, reverse=False):
        data = sorted(self, key = key, reverse = reverse)
        return CardDatabase(data=data)

    def findByName(self, cardname):
        #return list(filter(lambda card: card.name == cardname.encode('utf-8'), self))
        data = list(filter(lambda card: card.name == cardname, self))
        return CardDatabase(data=data)

    def filterDuplicates(self):
        data  = []
        names = []

        for card in self:
            if card.name in names:
                continue

            data.append(card)
            names.append(card.name)
        
        print( [ card.name for card in self ] )
        print( names )

        return CardDatabase(data=data) 

    def filterByExactColorCount(self, i):
        data = list(filter(lambda card: len(card.colors) == i, self))
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

    def filterByType(self, cardtype):
        data = list(filter(lambda card: cardtype in card.types, self))
        return CardDatabase(data=data)

    def filterByPrinting(self, printing):
        data = list(filter(lambda card: printing in card.printings, self))
        return CardDatabase(data=data)

    def distinctRarity(self):
        data = []

        for rarity in ("Mythic", "Rare", "Uncommon", "Common"):
            temp_data = self.filterByRarity(rarity)

            if temp_data:
                data.append( temp_data[0] )

        return CardDatabase(data=data)


class CubeDatabase(CardDatabase):
    FORMAT_TEXT_FILE = "txt"
    FORMAT_CSV_FILE  = "csv"
    FORMAT_CUBE_FILE = "cube"
    FORMAT_XML_FILE  = "xml"

    def __init__(self):
        pass

    def _importXML(self, fpath, carddb):
        data = etree.parse(fpath)

        cards = data.xpath(".//cards/card")
        
        for card in cards:
            main_cubedb = carddb.filterInNameList( [card.text] )
            
            if len(main_cubedb) > 1:
                main_cubedb = main_cubedb.distinctRarity()

                if len(main_cubedb) > 1:
                    print(main_cubedb)

            if "printing" in card.attrib:
                main_cubedb = main_cubedb.filterByPrinting( card.attrib["printing"] )
        
        main_cubedb = main_cubedb.sort(key = lambda card: card.name.lower())
        main_cubedb = main_cubedb.filterDuplicates()

        self.extend(main_cubedb)

    def _importTXT(self, fpath, carddb):
        with open(fpath) as f:
            cards = f.readlines()

        cards = [card.strip() for card in cards]

        main_cubedb = carddb.filterInNameList(cards)
        main_cubedb = main_cubedb.sort(key = lambda card: card.name.lower())
        main_cubedb = main_cubedb.filterDuplicates()

        self.extend(main_cubedb)

    def _importCSV(self, fpath, carddb):
        with open(fpath, "r") as f:
            reader = csv.reader(f)
            cards = [ cell[0].strip() for cell in reader ]

        main_cubedb = carddb.filterInNameList(cards)
        main_cubedb = main_cubedb.sort(key = lambda card: card.name.lower())
        main_cubedb = main_cubedb.filterDuplicates()

        self.extend(main_cubedb)

    def fileImport(self, fpath, carddb, force_format=None):
        if not force_format:
            head, force_format = os.path.splitext(fpath)
            force_format = force_format.replace(".","").lower()

        if force_format in [self.FORMAT_CUBE_FILE, self.FORMAT_XML_FILE]:
            self._importXML(fpath, carddb)
        elif force_format == self.FORMAT_TEXT_FILE:
            self._importTXT(fpath, carddb)
        elif force_format == self.FORMAT_CSV_FILE:
            self._importCSV(fpath, carddb)
        else:
            raise Exception("Unhandled file format (%s)" % force_format)

    def fileExport(self, fpath, force_format=None):
        if format == self.FORMAT_TEXT_FILE:
            self._exportTXT(fpath)
        elif format == self.FORMAT_CSV_FILE:
            self._exportCSV(fpath)
        elif format == self.FORMAT_CUBE_FILE:
            self._exportCUBE(fpath)
        else:
            raise Exception("Unhandled format (%s)" % format)

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