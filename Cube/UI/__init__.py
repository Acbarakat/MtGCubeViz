import sys
import os

def compile():
    if getattr(sys, 'frozen', False):
        return

    from PyQt4 import uic

    print("Compiling all files unders %s" % os.path.abspath("."))
    uic.compileUiDir(".", recurse=True)

if __name__ == '__main__':
    print("Comping UI files")
    compile()
