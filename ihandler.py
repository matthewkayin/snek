# An input handler for pygame
# Handles key input in a way that's universal across controllers/keyboards,
# whichallows keybinds to be saved in a config file
# Matt Madden

import os.path


class IHandler():
    def __init__(self, key_names):
        self.names = key_names
        self.map = []
        self.used_inputs = []
        self.states = [False] * len(self.names)
        for i in range(0, len(key_names)):
            if key_names[i].startswith("AXIS "):
                self.states[i] = 0
        self.queue = []
        self.debug = False
        self.map_index = -1

        if os.path.isfile("keyconfig.txt"):
            self.load_mapping(True)
        elif os.path.isfile("keydefault.txt"):
            self.load_mapping(False)
        else:
            print("IHandler Error - No key configs found! Key mapping is empty")

    def key_down(self, key):
        if self.map_index == len(self.map):
            # if we've used the key before or if the key isn't an axis but we're mapping an axis, don't map the key
            if (key in self.used_inputs
                    or (self.names[self.map_index].startswith("AXIS ") and ("x" not in key or "+" in key or "-" in key))
                    or (("+" in key or "-" in key) and key[:-1] in self.used_inputs)):
                return
            self.map.append(key)
            # if input is axis-as-button, save only the axis
            if "x" in key and ("+" in key or "-" in key):
                self.used_inputs.append(key[:-1])
            else:
                self.used_inputs.append(key)
            return
        index = -1
        for i in range(0, len(self.map)):
            if self.map[i] == key:
                index = i
                break
        if index == -1:
            if self.debug:
                print("IHandler Error - Requested handle keydown but key hasn't been mapped")
            return
        if not self.states[index]:
            self.queue.append(index)
            self.states[index] = True

    def key_up(self, key):
        if self.map_index != -1:
            if self.map_index != len(self.map):
                self.map_index += 1
                if self.map_index == len(self.names):
                    self.map_index = -1
                    self.save_mapping()
            return
        index = -1
        for i in range(0, len(self.map)):
            if self.map[i] == key:
                index = i
                break
        if index == -1:
            if self.debug:
                print("IHandler Error - Requested handle keyup but key hasn't been mapped")
            return
        if self.states[index]:
            self.queue.append(-1 * (index + 1))  # all release indexes are negative, but we have to shift them all up one because there is no negative zero
            self.states[index] = False

    def axis_moved(self, key, pos):
        index = -1
        for i in range(0, len(self.map)):
            if self.map[i] == key:
                index = i
                break
        if index == -1:
            print("IHandler Error - Plugged axis request even though there was no such mapped axis (this shouldn't be possible)")
            return
        self.states[index] = pos

    def key_queue(self):
        if len(self.queue) == 0:
            return "EMPTY"
        index = self.queue.pop()
        release = ""
        if index < 0:
            release = " RELEASE"
            index *= -1
            index -= 1
        return self.names[index] + release

    def get_state(self, name):
        index = -1
        for i in range(0, len(self.names)):
            if self.names[i] == name:
                index = i
                break
        if index == -1:
            print("IHandler Error - Requested check key state on a key that isn't in the keyNames. You probably made a typo.")
            return False
        return self.states[index]

    def is_mapped_axis(self, key):
        index = -1
        for i in range(0, len(self.map)):
            if self.map[i] == key:
                index = i
                break
        if index == -1:
            return False
        return not type(self.states[index]) is bool

    def is_mapping(self):
        return self.map_index != -1

    def start_mapping(self):
        if self.map_index != -1:
            print("IHandler Error - Can't begin input mapping, input mapping is already in progress.")
            return
        self.map = []
        self.used_inputs = []
        self.states = [False] * len(self.names)
        for i in range(0, len(self.names)):
            if self.names[i].startswith("AXIS "):
                self.states[i] = 0
        self.map_index = 0

    def to_map(self):
        if self.map_index == -1:
            print("IHandler Error - Can't call to_map when we're not currently keymapping.")
            return "ERROR"
        return self.names[self.map_index]

    def save_mapping(self):
        map_file = open("keyconfig.txt", "w")
        for i in range(0, len(self.names)):
            map_file.write(self.names[i] + "=" + str(self.map[i]) + "\n")
        map_file.close()

    def load_mapping(self, custom):
        self.names = []
        fileName = "keydefaults.txt"
        if custom:
            fileName = "keyconfig.txt"
        map_file = open(fileName, "r")
        for line in map_file.read().splitlines():
            index = line.index("=")
            self.names.append(line[:index])
            self.map.append(line[(index + 1):])
        map_file.close()
        self.states = [False] * len(self.names)
        for i in range(0, len(self.names)):
            if self.names[i].startswith("AXIS "):
                self.states[i] = 0
