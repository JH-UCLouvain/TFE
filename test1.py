#!/bin/python3
# Author : Jeremy Holodiline

from ipmininet.iptopo import IPTopo
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI

import jc

def testPing(src, dst, net):
    resp = net[src].cmd(f"ping -6 -c 1 -W 1 {dst}")
    print(resp)
    try:
        resp = jc.parse('ping', resp)
        print(resp)
        if resp["packet_loss_percent"] == 0.0 and len(resp["responses"]) > 0 and resp["responses"][0]["response_ip"] == dst:
            print("sucess ping")
        else:
            print("error ping")
    except Exception as e: print(e)

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

    # a ip -6 addr 2001:db8:1341:1::a/64 dev a-eth0
    # b ip -6 addr 2001:db8:1341:1::b/64 dev b-eth0

    testPing("a", "2001:db8:1341:1::a", net)
    testPing("b", "2001:db8:1341:1::b", net)

finally:
    net.stop()
