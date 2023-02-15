#!/bin/python3
# Author : Jeremy Holodiline

from inginious import feedback, ssh_student
from ipmininet.iptopo import IPTopo
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
import jc
import random

addresses = dict()

def generateIPaddr(interface, version):
    while True:
        if version == "v4":
            addr = ".".join(("%s" % random.randint(0, 255) for _ in range(4)))
        elif version == "v6":
            addr = "2001:0db8:" + ":".join(("%s" % "".join(("%s" % random.choice(("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f")) for _ in range(4))) for _ in range(6)))
        else:
            raise ValueError("IP version must be \"v4\" or \"v6\"")
        if addr not in addresses.values():
            addresses[interface] = addr
            return addr

def testPing(src, dst, net):
    try:
        resp = jc.parse('ping', net[src].cmd(f"ping -6 -c 1 -W 1 {dst}"))
        if resp["packet_loss_percent"] == 0.0 and len(resp["responses"]) > 0 and resp["responses"][0]["response_ip"] == dst:
            return (50, f"Ping {src}-{dst} success")
        else:
            return (0, f"Ping {src}-{dst} failed : the destination hasn't the right address on his interface")
    except Exception as e: return (0, f"Ping {src}-{dst} failed : {e}")

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        h1 = self.addHost("h1", defaultRoute=None)
        h2 = self.addHost("h2", defaultRoute=None)

        self.addLink(h1, h2)

        generateIPaddr("h1h2", "v6")
        generateIPaddr("h2h1", "v6")

        super(MyTopology, self).build(*args, **kwargs)

net = IPNet(topo=MyTopology(), allocate_IPs=False)

try:
    net.start()

    h1h2 = addresses["h1h2"]
    h2h1 = addresses["h2h1"]
    print("The ip address of interface h1-eth0 must be : " + h1h2)
    print("The ip address of interface h2-eth0 must be : " + h2h1)

    IPCLI(net)
    ssh_student.ssh_student()

    grade = 0
    message = ""

    ping1 = testPing("h1", h2h1, net)
    grade += ping1[0]
    message += ping1[1] + "\n"

    ping2 = testPing("h2", h1h2, net)
    grade += ping2[0]
    message += ping2[1] + "\n"

    feedback.set_grade(grade)
    feedback.set_global_feedback(message)
    if grade == 100:
        feedback.set_global_result("success")
    else:
        feedback.set_global_result("failed")
    
except Exception as e:
    feedback.set_grade(0)
    feedback.set_global_feedback(f"{e}")
    feedback.set_global_result("failed")

finally:
    net.stop()