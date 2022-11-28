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
        r4 = self.addRouter("r3", config=RouterConfig)

        self.addLink(h1, r1)
        self.addLink(r1, r2)
        self.addLink(r1, r3)
        self.addLink(r2, r4)
        self.addLink(r3, r4)
        self.addLink(r4, h2)

        r1.addDaemon(STATIC, static_routes=[])
        r2.addDaemon(STATIC, static_routes=[])
        r3.addDaemon(STATIC, static_routes=[])
        r4.addDaemon(STATIC, static_routes=[])

        super(MyTopology, self).build(*args, **kwargs)

net = IPNet(topo=MyTopology(), use_v4=False)

try:
    net.start()
    IPCLI(net)

    print(testPing("h1", "h2", net)[1])
    print(testPing("h2", "h1", net)[1])
    print(testTraceroute("h1", "h2", ["h1","r1","r2","r4","h2"], net)[1])
    print(testTraceroute("h2", "h1", ["h2","r4","r3","r1","h1"], net)[1])

except Exception as e: print(e)

finally:
    net.stop()
