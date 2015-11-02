
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

    cards = data.xpath(".//cards/card")

    main_cubedb = db.filterInNameList([card.text for card in cards])
    main_cubedb = main_cubedb.sort(key = lambda card: card.name.lower())
    main_cubedb = main_cubedb.filterDuplicates()

    for analysis in data.xpath(".//analysis/*"):
        print(analysis)
        if analysis.tag == "count":
            print(analysis.text)
            print(main_cubedb._filterByNode(analysis))
        elif analysis.tag == "percent":
            print(analysis.xpath(".//name")[0].text)
            numr = main_cubedb._filterByNode(analysis.xpath(".//numerator")[0])
            print(numr)
            deno = main_cubedb._filterByNode(analysis.xpath(".//denominator")[0])
            print(deno)

            perc = len(numr) / len(deno)
            perc *= 100.00 

            print( "%.3f" % perc )
        elif analysis.tag == "average_cmc":
            print(analysis.text)
            cards = main_cubedb._filterByNode(analysis)

            values = [ card.cmc for card in cards ] 

            print(values)

            print( sum(values) / len(values) )