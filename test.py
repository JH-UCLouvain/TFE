#!/bin/python3
import random

interface_addr = dict()

def generate_IP_addr(interface, version, prefix):
    while True:
        addr = ""
        if version == "v4":
            if prefix != "" and prefix[-1] != ".": prefix += "."
            n_rand = 4 - (len(prefix.split(".")) - 1)
            addr = prefix + ".".join(("%s" % random.randint(0, 255) for _ in range(n_rand)))
            addr = addr.rstrip(".")
        elif version == "v6":
            if prefix != "" and prefix[-1] != ":": prefix += ":"
            n_rand = 8 - (len(prefix.split(":")) - 1)
            for _ in range(n_rand):
                hex_num = ""
                for _ in range(4):
                    hex_num += random.choice(("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"))
                prefix += hex_num.lstrip("0") + ":"
            addr = prefix
            addr = addr.rstrip(":")
        else: raise ValueError("IP version must be \"v4\" or \"v6\"")
        if addr not in interface_addr.values():
            interface_addr[interface] = addr
            return addr
    
        
def generate_IP_addr(interface, version, prefix):
    while True:
        addr = ""
        if version == "v4":
            if prefix != "" and prefix[-1] != ".": prefix += "."
            n_rand = 4 - (len(prefix.split(".")) - 1)
            addr = prefix + ".".join(("%s" % random.randint(0, 255) for _ in range(n_rand)))
            addr = addr.rstrip(".")
        elif version == "v6":
            if prefix != "" and prefix[-1] != ":": prefix += ":"
            n_rand = 8 - (len(prefix.split(":")) - 1)
            for _ in range(n_rand):
                hex_num = ""
                for _ in range(4):
                    hex_num += random.choice(("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"))
                prefix += hex_num.lstrip("0") + ":"
            addr = prefix
            addr = addr.rstrip(":")
        else: raise ValueError("IP version must be \"v4\" or \"v6\"")
        if addr not in interface_addr.values():
            interface_addr[interface] = addr
            return addr