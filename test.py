#!/bin/python3

INGINIOUS = True

if INGINIOUS:
    from inginious import feedback

from ipmininet.iptopo import IPTopo
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
from ipmininet.router.config import RouterConfig, STATIC

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
            addr = prefix + ":".join(("%s" % "".join(("%s" % random.choice(("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f")) for _ in range(4))) for _ in range(n_rand)))
            addr = addr.rstrip(":")
        else: raise ValueError("IP version must be \"v4\" or \"v6\"")
        if addr not in interface_addr.values():
            interface_addr[interface] = addr
            return addr

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        h1 = self.addHost("h1", defaultRoute=None)
        h2 = self.addHost("h2", defaultRoute=None)

        lh1h2 = self.addLink(h1, h2)
        lh1h2[h1].addParams(ip = generate_IP_addr("h1-h2", "v6", "2001:db8:1341:1:") + "/64")
        lh1h2[h2].addParams(ip = generate_IP_addr("h2-h1", "v6", "2001:db8:1341:1:") + "/64")

        super(MyTopology, self).build(*args, **kwargs)

net = IPNet(topo=MyTopology(), allocate_IPs=False)

try:
    net.start()
    
    IPCLI(net)

    if INGINIOUS:
        feedback.set_grade(100)
        feedback.set_global_feedback(f"Success")
        feedback.set_global_result("success")
    else:
        print(f"Grade : 100")
        print(f"Feedback : Success")
        print(f"Result : success")

except Exception as e:
    if INGINIOUS:
        feedback.set_grade(0)
        feedback.set_global_feedback(f"Error : {e}")
        feedback.set_global_result("failed")
    else:
        print(f"Grade : 0")
        print(f"Feedback : Error : {e}")
        print(f"Result : failed")

finally:
    net.stop()

def store_feedback(grade, feedback, result):
    file = open("student/scripts/grade","w")
    file.write(str(grade))
    file.close()
    file = open("student/scripts/feedback","w")
    file.write(feedback)
    file.close()
    file = open("student/scripts/result","w")
    file.write(result)
    file.close()

f = open("student/scripts/grade", "r")
feedback.set_grade(float(f.read()))
f.close()
f = open("student/scripts/feedback", "r")
feedback.set_global_feedback(f.read())
f.close()
f = open("student/scripts/result", "r")
feedback.set_global_result(f.read())
f.close()