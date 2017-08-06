# gintonic

gintonic - is a lightweight game launcher, that works in a terminal. It is designed to be fast, to be comfortable for keyboard users and to work through ssh.

![Alt text](screen_shot.png?raw=true "gintonic")

## Features

  * Support of VIM-style keys
  * Search history
  * Script based confguration
  * Preview of thumbnails

## Requirements

* python
* w3m-img (optional, for images previews)

## Installation

* Download gintonic
* Place a config file named config into ~/.gintonic

Example:
```
[CONFIG]
path_to_games = /home/user/games
run_dos = ./dos.sh {0}
```
path_to_games - is a path to games. 

Directory with the games should have the following structure:
```
System1
      |- Game1
      |- Game2
             |-thumbnails
      |- Game3
System2
      |- Game1
             |-thumbnails
```
Where: 
  SystemX - is the name of a system (DOS, NES, etc).<br>
  GameX - is the name of a game.<br>
  thumbnails - is an optional subfolder with images.<br>
<br>
run_system - specifies a command to run a game on a particular system. {0} is substituted by an absolute path of a game.

## Run

* python gintonic.py
<br>
If you use gintonic over ssh, run ssh with -X param to have images.
For exit - press q. 

