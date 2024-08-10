from ipmininet.iptopo import IPTopo
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI
from ipmininet.router.config import BorderRouterConfig, ebgp_session

#import sys
#sys.path.insert(1, '/course/common/student/')
from ipmininet_exercices import IPMininet_Exercice
ex = IPMininet_Exercice(4, False)

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        r1 = self.addRouter("r1", config=BorderRouterConfig)
        r2 = self.addRouter("r2", config=BorderRouterConfig)

        l = self.addLink(r1, r2)
        l[r1].addParams(ip="193.10.11.1/24")
        l[r2].addParams(ip="193.10.11.2/24")

        self.addAS(1, (r1,))
        self.addAS(2, (r2,))

        ebgp_session(self, r1, r2)

        super(MyTopology, self).build(*args, **kwargs)

net = IPNet(topo=MyTopology(), allocate_IPs=False)

try:
    net.start()

    #net["r1"].cmd(f"vtysh -c 'configure terminal' -c 'router bgp 1' -c 'exit' -c 'exit' -c 'write memory'")
    #net["r2"].cmd(f"vtysh -c 'configure terminal' -c 'router bgp 2' -c 'exit' -c 'exit' -c 'write memory'")
    #net["r1"].cmd(f"vtysh -c 'configure terminal' -c 'router bgp 1' -c 'no bgp ebgp-requires-policy' -c 'neighbor 193.10.11.2 remote-as 2' -c 'network 195.11.14.0/24' -c 'exit' -c 'exit' -c 'write memory'")
    #net["r2"].cmd(f"vtysh -c 'configure terminal' -c 'router bgp 2' -c 'no bgp ebgp-requires-policy' -c 'neighbor 193.10.11.1 remote-as 1' -c 'network 200.1.1.0/24' -c 'exit' -c 'exit' -c 'write memory'")

    IPCLI(net)

    ex.send_feedback()

except Exception as e:
    ex.send_feedback(0, "crash", f"Error from the ipmininet script : {e}")

finally:
    net.stop()