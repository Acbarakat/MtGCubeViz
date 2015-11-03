
if __name__ == "__main__":
    import os
    import sys
    import random

    from lxml import etree
    from PyQt5.QtWidgets import QApplication #Required due to card using QPixMap

    fpath, _ = os.path.split(__file__)
    sys.path.append(os.path.join(fpath, ".."))

    from mtg.Database import CardDatabase, CubeDatabase

    app = QApplication(sys.argv)

    card_db = CardDatabase()

    my_cube = CubeDatabase()
    my_cube.fileImport(r"MyCube.xml", card_db)
    print(len(my_cube))
    my_cube.fileImport(r"SampleImport.txt", card_db)
    print(len(my_cube))
    my_cube.fileImport(r"SampleImport.csv", card_db)
    print(len(my_cube))

    data = etree.parse(r"MyCube.xml")

    for analysis in data.xpath(".//analysis/*"):
        if analysis.tag == "count":
            print(analysis.text)
            print(my_cube._filterByNode(analysis))
        elif analysis.tag == "percent":
            print(analysis.xpath(".//name")[0].text)
            numr = my_cube._filterByNode(analysis.xpath(".//numerator")[0])
            print(numr)
            deno = my_cube._filterByNode(analysis.xpath(".//denominator")[0])
            print(deno)

            perc = len(numr) / len(deno)
            perc *= 100.00 

            print( "%.3f" % perc )
        elif analysis.tag == "average_cmc":
            print(analysis.text)
            cards = my_cube._filterByNode(analysis)

            values = [ card.cmc for card in cards ] 

            print(values)

            print( sum(values) / len(values) )