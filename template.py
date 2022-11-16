#!/bin/python3
# Author : Jeremy Holodiline

from ipmininet.iptopo import IPTopo
from ipmininet.router.config import RouterConfig, STATIC
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
import random
import jc

ADDR_TAKEN = set()

def generateIPaddr(version):
    while True:
        if version == "v4":
            addr = ".".join(("%s" % random.randint(0, 255) for _ in range(4))) + "/64"
        elif version == "v6":
            addr = "2001:0db8:" + ":".join(("%s" % "".join(("%s" % random.choice(("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f")) for _ in range(4))) for _ in range(6))) + "/64"
        else:
            raise ValueError("IP version must be \"v4\" or \"v6\"")
        if addr not in ADDR_TAKEN:
            ADDR_TAKEN.add(addr)
            return addr

def testPing(src, dst, net):
    resp = net[src].cmd(f"ping -6 -c 1 -W 1 {dst}")
    try:
        resp = jc.parse('ping', resp)
        if resp["packet_loss_percent"] == 0.0 and len(resp["responses"]) > 0 and resp["responses"][0]["response_ip"] == dst:
            return 0
        else:
            return -1
    except Exception as e: print(e)

def testTraceroute(src, dst, route, net):
    resp = net[src].cmd(f"traceroute -6 -q 1 -m 5 {dst}")
    try:
        resp = jc.parse('traceroute', resp)
        for hop in resp["hops"]:
            if hop["hop"] > len(route):
                return -1
            if hop["probes"][0]["ip"] != route[hop["hop"]-1]:
                return -1
        return 0
    except Exception as e: print(e)

def testStaticRoutingTable(router,table,net):
    #TODO
    return 0

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        h1 = self.addHost("h1", defaultRoute=None)
        h2 = self.addHost("h2", defaultRoute=None)
        h3 = self.addHost("h3", defaultRoute=None)
        r1 = self.addRouter("r1", config=RouterConfig)
        r2 = self.addRouter("r2", config=RouterConfig)
        r3 = self.addRouter("r3", config=RouterConfig)

        lh1r1 = self.addLink(h1, r1)
        lh1r1[h1].addParams(ip=generateIPaddr("v6"))
        lh1r1[r1].addParams(ip=generateIPaddr("v6"))

        lr1r2 = self.addLink(r1, r2)
        lr1r2[r1].addParams(ip=generateIPaddr("v6"))
        lr1r2[r2].addParams(ip=generateIPaddr("v6"))

        lr2r3 = self.addLink(r2, r3)
        lr2r3[r2].addParams(ip=generateIPaddr("v6"))
        lr2r3[r3].addParams(ip=generateIPaddr("v6"))

        lr3h3 = self.addLink(r3, h3)
        lr3h3[r3].addParams(ip=generateIPaddr("v6"))
        lr3h3[h3].addParams(ip=generateIPaddr("v6"))

        lr2h2 = self.addLink(r2, h2)
        lr2h2[r2].addParams(ip=generateIPaddr("v6"))
        lr2h2[h2].addParams(ip=generateIPaddr("v6"))
        
        r1.addDaemon(STATIC, static_routes=[])
        r2.addDaemon(STATIC, static_routes=[])
        r3.addDaemon(STATIC, static_routes=[])

        super(MyTopology, self).build(*args, **kwargs)

net = IPNet(topo=MyTopology(), allocate_IPs=False)
try:
    net.start()
    IPCLI(net)

    print(testPing("a", "b", net))
    print(testPing("b", "a", net))
    print(testPing("a", "c", net))
    print(testPing("c", "a", net))
    print(testPing("b", "c", net))
    print(testPing("c", "b", net))

finally:
    net.stop()
