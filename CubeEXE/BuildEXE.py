'''
Created on Oct 29, 2013

@author: acbaraka
'''
import sys
import stat
from PyQt5 import uic
from cx_Freeze import setup, Executable

includes        = [ 'lxml._elementpath', 'json' ] #[ "resources_rc" ]
include_files   = [ ]
excludes        = [ "PyQt5.uic" ]

build_options = {"includes" : includes, 
                 "excludes" : excludes, 
                 "create_shared_zip": False,
                 "append_script_to_exe": True,
                 "include_in_shared_zip": False
                }
    
CubeViz_EXE  = Executable(script=r".\..\Cube\main.py",
                          base= "Win32GUI" if sys.platform == "win32" else None,
                          targetName="CubeViz.exe",
                          appendScriptToExe=True,
                          compress=True,
                          #icon="icon.ico"
                          )

build_options["include_files"] = include_files

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def compileGUI(pyrcc_path=None, uic_path=".\\..\\Cube\\UI\\"):
    if not pyrcc_path:
        head, _ = os.path.split(sys.executable)
        pyrcc_path = os.path.join(head, r"Lib\site-packages\PyQt5\pyrcc5.exe")
    
    if os.path.exists( pyrcc_path ):
        print("Compiling Resources")
        cmd = "%s -o ./resources_rc.py ./resources.qrc -py3" % pyrcc_path
        os.system(cmd)
    else:
        print("Cannot find pyrcc5.exe")
    
    print("\nComping UI files")
    uic.compileUiDir(uic_path, recurse=True)

if __name__ == '__main__':
    import os
    import shutil
    
    sys.argv.append("build")
    
    if os.path.exists(os.path.join(".", "build")):
        shutil.rmtree(os.path.join(".", "build"), onerror=onerror)
    
    compileGUI()
    
    print("\nCompiling CubeViz Binary")
    from common import __version__
    setup(
        name = "CubeViz",
        version = __version__,
        author="Allonte' C. Barakat",
        description = "MtG Cube Visualizer",
        options = {"build_exe" : build_options},
        executables = [ CubeViz_EXE ]
        )
    print("Cube Binary Compile Complete!\n")

    print("Running binary with Example.cube")
    exe_path = os.path.join(CubeViz_EXE.path[0], CubeViz_EXE.targetName)
    cmd = "{binary} {cube_file}".format(binary=exe_path,
                                        cube_file=r"Example.cube")

    print("{}> {}".format(os.getcwd(), cmd))
    os.system(cmd)
