#! /bin/bash
UI=ui/
SRC=src/

pyrcc5 $SRC/src.qrc -o src_rc.py
pyuic5 $SRC/main.ui -o $UI/main.py
pyuic5 $SRC/region.ui -o $UI/region.py