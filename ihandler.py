#An input handler for pygame
#Handles key input in a way that's universal across controllers/keyboards, allows keybinds to be saved in a config file
#Matt Madden

import pygame
import os.path

class IHandler():
    def __init__(self, keyNames):
        self.names = keyNames
        self.map = []
        self.states = [False] * len(self.names)
        self.queue = []
        self.debug = False
        self.currentMapIndex = -1

        if os.path.isfile("keyconfig.txt"):
            self.loadMapping(True)
        elif os.path.isfile("keydefault.txt"):
            self.loadMapping(False)
        else:
            print("IHandler Error - No key configs found! Key mapping is empty")

    def keyDown(self, key):
        if self.currentMapIndex == len(self.map):
            self.map.append(key)
            return

        index = -1
        for i in range(0, len(self.map)):
            if self.map[i] == key:
                index = i
                break
        if index == -1 and self.debug:
            print("IHandler Error - Requested handle keydown but key hasn't been mapped")
            return
        self.queue.append(index)
        self.states[index] = True

    def keyUp(self, key):
        if self.currentMapIndex != -1:
            if self.currentMapIndex != len(self.map):
                self.currentMapIndex += 1
                if self.currentMapIndex == len(self.names):
                    self.currentMapIndex = -1
                    self.saveMapping()
            return

        index = -1
        for i in range(0, len(self.map)):
            if self.map[i] == key:
                index = i
                break
        if index == -1 and self.debug:
            print("IHandler Error - Requested handle keyup but key hasn't been mapped")
            return
        self.queue.append(-1*(index + 1)) #all release indexes are negative, but we have to shift them all up one because there is no negative zero
        self.states[index] = False

    def keyQueue(self):
        if len(self.queue) == 0:
            return "EMPTY"

        index = self.queue.pop()
        release = ""
        if index < 0:
            release = " RELEASE"
            index *= -1
            index -= 1
        return self.names[index] + release

    def isKeyDown(self, name):
        index = -1
        for i in range(0, len(self.names)):
            if self.names[i] == name:
                index = i
                break
        if index == -1:
            print("IHandler Error - Requested check key state on a key that isn't in the keyNames. You probably made a typo.")
            return False
        return self.state[index]

    def isMapping(self):
        return self.currentMapIndex != -1

    def startMapping(self):
        if self.currentMapIndex != -1:
            print("IHandler Error - Can't begin input mapping, input mapping is already in progress.")
            return
        self.map = []
        self.currentMapIndex = 0

    def keyToMap(self):
        if self.currentMapIndex == -1:
            print("IHandler Error - Can't call keyToMap when we're not currently keymapping.")
            return "ERROR"
        return self.names[self.currentMapIndex]

    def saveMapping(self):
        mapFile = open("keyconfig.txt", "w")
        for i in range(0, len(self.names)):
            mapFile.write(self.names[i] + "=" + str(self.map[i]) + "\n")
        mapFile.close()

    def loadMapping(self, custom):
        self.names = []
        fileName = "keydefaults.txt"
        if custom:
            fileName = "keyconfig.txt"
        mapFile = open(fileName, "r")
        for line in mapFile:
            index = line.index("=")
            self.names.append(line[:index])
            self.map.append(int(line[(index+1):]))
        mapFile.close()
        self.states = [False] * len(self.names)

