#!/bin/python3
# Author : Jeremy Holodiline

from ipmininet.iptopo import IPTopo
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
import jc

def testPing(src, dst, net):
    try:
        resp = jc.parse('ping', net[src].cmd(f"ping -6 -c 1 -W 1 {dst}"))
        if resp["packet_loss_percent"] == 0.0 and len(resp["responses"]) > 0 and resp["responses"][0]["response_ip"] == dst:
            return (0, f"Ping {src}-{dst} success")
        else:
            return (-1, f"Ping {src}-{dst} failed - Packets lost : {(resp['packets_transmitted'] - resp['packets_received'])*100} % ")
    except Exception as e: return (-1, f"Ping {src}-{dst} failed - {e}")

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        h1 = self.addHost("h1", defaultRoute=None)
        h2 = self.addHost("h2", defaultRoute=None)

        self.addLink(h1, h2)

        super(MyTopology, self).build(*args, **kwargs)

net = IPNet(topo=MyTopology(), allocate_IPs=False)

try:
    net.start()
    IPCLI(net)

    print(testPing("h1", "h2", net)[1])
    print(testPing("h2", "h1", net)[1])

except Exception as e: print(e)

finally:
    net.stop()
