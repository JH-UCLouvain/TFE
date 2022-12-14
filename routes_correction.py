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
        r5 = self.addRouter("r5", config=RouterConfig)
        r6 = self.addRouter("r6", config=RouterConfig)

        lh1r1 = self.addLink(h1, r1)
        lh1r1[h1].addParams(ip="2001:db8:1341:1::a1/64")
        lh1r1[r1].addParams(ip="2001:db8:1341:1::1a/64")

        lr1r2 = self.addLink(r1, r2)
        lr1r2[r1].addParams(ip="2001:db8:1341:1::12/64")
        lr1r2[r2].addParams(ip="2001:db8:1341:1::21/64")

        lr2r3 = self.addLink(r2, r3)
        lr2r3[r2].addParams(ip="2001:db8:1341:1::23/64")
        lr2r3[r3].addParams(ip="2001:db8:1341:1::32/64")

        lr4r5 = self.addLink(r4, r5)
        lr4r5[r4].addParams(ip="2001:db8:1341:1::45/64")
        lr4r5[r5].addParams(ip="2001:db8:1341:1::54/64")

        lr5r6 = self.addLink(r5, r6)
        lr5r6[r5].addParams(ip="2001:db8:1341:1::56/64")
        lr5r6[r6].addParams(ip="2001:db8:1341:1::65/64")

        lr6h2 = self.addLink(r6, h2)
        lr6h2[r6].addParams(ip="2001:db8:1341:1::6b/64")
        lr6h2[h2].addParams(ip="2001:db8:1341:1::b6/64")

        lr1r4 = self.addLink(r1, r4)
        lr1r4[r1].addParams(ip="2001:db8:1341:1::14/64")
        lr1r4[r4].addParams(ip="2001:db8:1341:1::41/64")

        lr2r5 = self.addLink(r2, r5)
        lr2r5[r2].addParams(ip="2001:db8:1341:1::25/64")
        lr2r5[r5].addParams(ip="2001:db8:1341:1::52/64")

        lr3r6 = self.addLink(r3, r6)
        lr3r6[r3].addParams(ip="2001:db8:1341:1::36/64")
        lr3r6[r6].addParams(ip="2001:db8:1341:1::63/64")

        r1.addDaemon(STATIC, static_routes=[])
        r2.addDaemon(STATIC, static_routes=[])
        r3.addDaemon(STATIC, static_routes=[])
        r4.addDaemon(STATIC, static_routes=[])
        r5.addDaemon(STATIC, static_routes=[])
        r6.addDaemon(STATIC, static_routes=[])

        super(MyTopology, self).build(*args, **kwargs)

net = IPNet(topo=MyTopology(), allocate_IPs=False)

try:
    net.start()

    net["h1"].cmd("ip -6 route add default via 2001:db8:1341:1::1a")
    net["h2"].cmd("ip -6 route add default via 2001:db8:1341:1::6b")
    net["r1"].cmd("ip -6 route add default via 2001:db8:1341:1::21")
    net["r2"].cmd("ip -6 route add default via 2001:db8:1341:1::52")
    net["r5"].cmd("ip -6 route add default via 2001:db8:1341:1::45")
    net["r4"].cmd("ip -6 route add default via 2001:db8:1341:1::14")
    net["r3"].cmd("ip -6 route add default via 2001:db8:1341:1::63")
    net["r6"].cmd("ip -6 route add default via 2001:db8:1341:1::56")
    net["r6"].cmd("ip -6 route add 2001:db8:1341:1::b6/64 via 2001:db8:1341:1::b6")

    IPCLI(net)

    print(testPing("h1", "2001:db8:1341:1::b6", net)[1])
    print(testPing("h2", "2001:db8:1341:1::a1", net)[1])

except Exception as e: print(e)

finally:
    net.stop()
