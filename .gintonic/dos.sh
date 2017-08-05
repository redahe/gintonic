#!/bin/bash

shopt -s extglob
# list of preffered executables for some games
exef=`ls $1/@(duke3d.exe|DOOM.EXE)`

if [ -z "$exef" ]; then
dosbox $1/@(*.exe|*.EXE) -exit -fullscreen; # Run the firts exe
else
dosbox "$exef" -exit -fullscreen;   # Run a preffered exe
fi

