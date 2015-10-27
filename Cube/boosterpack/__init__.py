
def getMatches(dblist, xml_item):
    if "rarity" in xml_item.attrib:
        rarity = xml_item.attrib["rarity"]

        dblist = dblist.filterByRarity(rarity)

    return dblist

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

    cubedb = db.filterInNameList([card.text for card in cards])
    cubedb = cubedb.sort(key = lambda card: card.name.lower())
    cubedb = cubedb.filterDuplicates()
    #print(cubedb)

    booster = data.xpath(".//booster/pack")[0]

    print(booster.attrib["name"])
    items = booster.xpath(".//item")

    for p in range(0, 10):
        print(p)

        for item in items:
            matches = getMatches(cubedb, item)
        
            flex_items = item.xpath(".//flex_item")

            if flex_items:
                temp_matches = []

                for flex_item in flex_items:
                    flex_amount = int( flex_item.attrib["flex"] )
                    for i in range(0, flex_amount):
                        temp_matches += getMatches(matches, flex_item)

                matches = temp_matches

            slots = item.attrib["slot"].split(",")

            for i in slots:
                if "-" in i:
                    start, stop = i.split("-")
                    for j in range(int(start), int(stop)+1):
                        card = random.choice(matches)

                        matches.pop(matches.index(card))
                        cubedb.pop(cubedb.index(card))

                        print("Slot %2d: %s" % (int(j), card) )

                    continue

                card = random.choice(matches)

                matches.pop(matches.index(card))
                cubedb.pop(cubedb.index(card))

                print("Slot %2d: %s" % (int(i), card ) )

        print("")