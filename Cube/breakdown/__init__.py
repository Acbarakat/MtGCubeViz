
if __name__ == "__main__":
    import os
    import sys
    import random
    from pprint import pprint

    from lxml import etree
    from PyQt5.QtWidgets import QApplication #Required due to card using QPixMap

    fpath, _ = os.path.split(__file__)
    sys.path.append(os.path.join(fpath, ".."))

    from mtg.Database import CardDatabase, CubeDatabase

    app = QApplication(sys.argv)

    card_db = CardDatabase()
    print(len(card_db))

    my_cube = CubeDatabase()
    my_cube.fileImport(r"MyCube.xml", card_db)
    my_cube.fileImport(r"SampleImport.txt", card_db)
    my_cube.fileImport(r"SampleImport.csv", card_db)
    print(len(my_cube))
    my_cube = my_cube.filterDuplicates()
    print(len(my_cube))

    data = etree.parse(r"MyCube.xml")

    for analysis in data.xpath(".//analysis/*"):
        if analysis.tag == "count":
            name = analysis.text
            cards = my_cube._filterByNode(analysis)
            if name in ["Mythics", "Rares"]:
                pprint(cards)
            value = len(cards)
        elif analysis.tag == "percent":
            name = analysis.xpath(".//name")[0].text

            numr = my_cube._filterByNode(analysis.xpath(".//numerator")[0])
            deno = my_cube._filterByNode(analysis.xpath(".//denominator")[0])

            perc = len(numr) / len(deno)
            perc *= 100.00

            value = "%.3f" % perc
        elif analysis.tag == "average_cmc":
            name = analysis.text
            cards = my_cube._filterByNode(analysis)

            values = [ card.cmc for card in cards ] 

            value = sum(values) / len(values)
        else:
            raise Exception("Unhandled analysis type (%s)" % analysis.tag)

        text = "{name}:\t{value}".format(name=name, value=value)
        print(text)