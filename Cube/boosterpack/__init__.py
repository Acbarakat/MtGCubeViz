
class BoosterPack(object):
    def __init__(self, xmldata):
        self.xmldata = xmldata

    def __repr__(self):
        return "<BoostPack (%s, %s Cards)>" % (self.name, self.count)

    @property
    def name(self):
        return self.xmldata.attrib["name"]

    @property
    def count(self):
        return int(self.xmldata.xpath("count(.//item)"))

    def _getMatches(self, dblist, xml_item):
        if "rarity" in xml_item.attrib:
            rarity = xml_item.attrib["rarity"]

            dblist = dblist.filterByRarity(rarity)

        if "type" in xml_item.attrib:
            cardtype = xml_item.attrib["type"]

            dblist = dblist.filterByType(cardtype)

        return dblist

    def generatePackSlotFromPool(self, slot, card_pool):
        #print("Cube Len : %3d" % len(card_pool))

        item = self.xmldata.xpath("(.//item)[%d]" % (slot+ 1))
        
        if not item:
            raise Exception("Slot %s is undefined" % slot)

        item = item[0]

        matches = self._getMatches(card_pool, item)
        
        flex_items = item.xpath(".//flex_item")

        if flex_items:
            temp_matches = []

            for flex_item in flex_items:
                flex_amount = int( flex_item.attrib["flex"] )
                for i in range(0, flex_amount):
                    flex_card = self._getMatches(matches, flex_item)
                    flex_card = random.choice(flex_card)

                    temp_matches.append( flex_card )

            print(temp_matches)

            matches = temp_matches

        card = None

        if matches:
            #print("Match len %3d" % len(matches))

            card = random.choice(matches)

            idx = card_pool.index(card)

            #print(idx)

            popd = card_pool.pop(idx)

            #print(popd)

        return card

    def generatePackFromPool(self, card_pool):
        result = [ self.generatePackSlotFromPool(i, card_pool) for i in range(self.count) ]

        return result


if __name__ == "__main__":
    import os
    import sys
    import random

    from lxml import etree
    from PyQt5.QtWidgets import QApplication #Required due to card using QPixMap

    fpath, _ = os.path.split(__file__)
    sys.path.append(os.path.join(fpath, ".."))

    from mtg.Database import CardDatabase

    app = QApplication(sys.argv)

    db = CardDatabase()

    data = etree.parse(r"MyCube.xml")

    cards = data.xpath(".//grouping/cards/card")

    main_cubedb = db.filterInNameList([card.text for card in cards])
    main_cubedb = main_cubedb.sort(key = lambda card: card.name.lower())
    main_cubedb = main_cubedb.filterDuplicates()

    for pack in data.xpath(".//booster/pack"):
        pack = BoosterPack(pack)

        print(pack)

        for p in range(0, 10):
            pack_list = pack.generatePackFromPool(main_cubedb)

            print(p)
            for i, card in enumerate(pack_list):
                print("Slot %2d: %s" % (i, card) )

            print("")