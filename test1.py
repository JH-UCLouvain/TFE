#!/bin/python3
# Author : Jeremy Holodiline

from ipmininet.iptopo import IPTopo
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI

import jc

def testPing(src, dst, net):
    resp = net[src].cmd(f"ping -6 -c 1 -W 1 {dst}")
    try:
        resp = jc.parse('ping', resp)
        if resp["packet_loss_percent"] == 0.0 and len(resp["responses"]) > 0 and resp["responses"][0]["response_ip"] == dst:
            print("sucess ping")
        else:
            print("error ping")
    except:
        print("error jc parsing")

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        a = self.addHost("a", defaultRoute=None)
        b = self.addHost("b", defaultRoute=None)

        self.addLink(a, b)

        super(MyTopology, self).build(*args, **kwargs)
            

net = IPNet(topo=MyTopology(), allocate_IPs=False)
try:
    net.start()
    IPCLI(net)

    commandA = input("Configure host a :\n") # a ip -6 addr 2001:db8:1341:1::a/64 dev a-eth0
    commandB = input("Configure host b :\n") # b ip -6 addr 2001:db8:1341:1::b/64 dev b-eth0
    net["a"].cmd(commandA)
    net["b"].cmd(commandB)
    testPing("a", "2001:db8:1341:1::a", net)
    testPing("b", "2001:db8:1341:1::b", net)

finally:
    net.stop()