#!/bin/bash

shopt -s extglob
# list of preffered executables for some games
exef=`ls $1/@(duke3d.exe|DOOM.EXE)`

if [ -z "$exef" ]; then
dosbox -exit $1/@(*.exe|*.EXE); # Run the firts exe
else
dosbox -exit "$exef";   # Run a preffered exe
fi

