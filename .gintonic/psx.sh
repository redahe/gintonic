#!/bin/bash

shopt -s extglob
retroarch -L /usr/lib/libretro/pcsx_rearmed_libretro.so $1/@(*.img|*.cue)
