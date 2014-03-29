# Memory Game

## Description

Authors: Mireya Andres, Nina Quiazon, and Andie Rabino.

Machine Problem for CS 145. This is a networking memory game that uses a client-server model. Only two clients may connect to the server and start the game at any given time. The game is written in Python using the pyglet module.

version1 contains the game logic.
version2 implements game states and scoring.
version3 implements the client-server model for networking. Currently a work in progress.

## Requirements and Specifications

[x] Client identifier (distinct; use of thread name; threads also have threadID)
[ ] Option for players to have their own username (may be the same)
[x] Send messages to all or selected users
[x] Receive messages from all
[ ] Option to share other kinds of information (score)
[x] Voluntary disconnect
[ ] Notification when other user disconnects

## Dependencies

Download eventlet. For Unix:

```bash
$ sudo apt-get install python-eventlet
```
For Windows you may download from here: http://pypi.python.org/packages/source/e/eventlet/eventlet-0.9.14.tar.gz

Eventlet can also be found here: https://bitbucket.org/eventlet/eventlet/