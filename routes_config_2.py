#!/bin/python3
# Author : Jeremy Holodiline

from ipmininet.iptopo import IPTopo
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
from ipmininet.router.config import RouterConfig, STATIC
import jc

def testPing(src, dst, net):
    try:
        resp = jc.parse('ping', net[src].cmd(f"ping -6 -c 1 -W 1 {dst}"))
        if resp["packet_loss_percent"] == 0.0 and len(resp["responses"]) > 0 and resp["responses"][0]["response_ip"] == dst:
            return (0, f"Ping {src}-{dst} success")
        else:
            return (-1, f"Ping {src}-{dst} failed - Packets lost : {(resp['packets_transmitted'] - resp['packets_received'])*100} % ")
    except Exception as e: return (-1, f"Ping {src}-{dst} failed - {e}")

def testTraceroute(src, dst, route, net):
    try:
        resp = jc.parse('traceroute', net[src].cmd(f"traceroute -6 -q 1 -m 5 {dst}"))
        for hop in resp["hops"]:
            if hop["hop"] > len(route):
                return (-1, f"Traceroute {src}-{dst} failed")
            if hop["probes"][0]["ip"] != route[hop["hop"]-1]:
                return (-1, f"Traceroute {src}-{dst} failed - Wrong route")
        return (0, f"Traceroute {src}-{dst} success")
    except Exception as e: return (-1, f"Traceroute {src}-{dst} failed - {e}")

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        h1 = self.addHost("h1", defaultRoute=None)
        h2 = self.addHost("h2", defaultRoute=None)
        r1 = self.addRouter("r1", config=RouterConfig)
        r2 = self.addRouter("r2", config=RouterConfig)
        r3 = self.addRouter("r3", config=RouterConfig)
        r4 = self.addRouter("r4", config=RouterConfig)

        lh1r1 = self.addLink(h1, r1)
        lh1r1[h1].addParams(ip="2001:db8:1341:1::a1/64")
        lh1r1[r1].addParams(ip="2001:db8:1341:1::1a/64")

        lr1r2 = self.addLink(r1, r2)
        lr1r2[r1].addParams(ip="2001:db8:1341:1::12/64")
        lr1r2[r2].addParams(ip="2001:db8:1341:1::21/64")

        lr1r3 = self.addLink(r1, r3)
        lr1r3[r1].addParams(ip="2001:db8:1341:1::13/64")
        lr1r3[r3].addParams(ip="2001:db8:1341:1::31/64")

        lr2r4 = self.addLink(r2, r4)
        lr2r4[r2].addParams(ip="2001:db8:1341:1::24/64")
        lr2r4[r4].addParams(ip="2001:db8:1341:1::42/64")

        lr3r4 = self.addLink(r3, r4)
        lr3r4[r3].addParams(ip="2001:db8:1341:1::34/64")
        lr3r4[r4].addParams(ip="2001:db8:1341:1::43/64")

        lr4h2 = self.addLink(r4, h2)
        lr4h2[r4].addParams(ip="2001:db8:1341:1::4b/64")
        lr4h2[h2].addParams(ip="2001:db8:1341:1::b4/64")

        r1.addDaemon(STATIC, static_routes=[])
        r2.addDaemon(STATIC, static_routes=[])
        r3.addDaemon(STATIC, static_routes=[])
        r4.addDaemon(STATIC, static_routes=[])

        super(MyTopology, self).build(*args, **kwargs)

net = IPNet(topo=MyTopology(), allocate_IPs=False)

try:
    net.start()
    IPCLI(net)

    print(testPing("h1", "2001:db8:1341:1::b4", net)[1])
    print(testPing("h2", "2001:db8:1341:1::a1", net)[1])
    print(testTraceroute("h1", "2001:db8:1341:1::b4", ["2001:db8:1341:1::1a","2001:db8:1341:1::21","2001:db8:1341:1::42","2001:db8:1341:1::b4"], net)[1])
    print(testTraceroute("h2", "2001:db8:1341:1::a1", ["2001:db8:1341:1::4b","2001:db8:1341:1::34","2001:db8:1341:1::13","2001:db8:1341:1::a1"], net)[1])

except Exception as e: print(e)

finally:
    net.stop()
