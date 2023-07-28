#!/bin/python3
# Author : Jeremy Holodiline

# TODO : Setting the flag saying if the integration to INGInious is used or not
INGINIOUS = False

if INGINIOUS:
    from inginious import feedback, ssh_student

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
            n_rand = 4 - (len(prefix.split(".")) - 1)
            addr = prefix + ".".join(("%s" % random.randint(0, 255) for _ in range(n_rand)))
        elif version == "v6":
            n_rand = 8 - (len(prefix.split(":")) - 1)
            addr = prefix + ":".join(("%s" % "".join(("%s" % random.choice(("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f")) for _ in range(4))) for _ in range(n_rand)))
        else:
            raise ValueError("IP version must be \"v4\" or \"v6\"")
        if addr not in interface_addr.values():
            interface_addr[interface] = addr
            return addr

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        # TODO : Creating the nodes
        # h1 = self.addHost("h1", defaultRoute=None)
        # r1 = self.addRouter("r1", config=RouterConfig)
        # ...

        # TODO : Creating the links between the nodes
        # lh1r1 = self.addLink(h1, r1)
        # lh1r1[h1].addParams(ip = generate_IP_addr("h1-r1", "v6", "2001:db8:1234:1341:") + "/64")
        # lh1r1[r1].addParams(ip = generate_IP_addr("r1-h1", "v6", "2001:db8:1234:1341:") + "/64")
        # ...

        # TODO : Adding empty static routing tables to the routers
        # r1.addDaemon(STATIC, static_routes=[])
        # ...

        super(MyTopology, self).build(*args, **kwargs)

net = IPNet(topo=MyTopology(), allocate_IPs=False)

n_test = 0
n_success_test = 0
message = ""

def ping_test(src_name, dst_interface_name, net):
    n_test += 1
    dst_address = interface_addr[dst_interface_name]
    dst_name = dst_interface_name.split("-")[0]
    dst_IP_version = "6" if ":" in dst_address else "4"
    try:
        output = net[src_name].cmd(f"ping -{dst_IP_version} -c 1 -W 1 {dst_address}")
        if " 0% packet loss" in output or " 0.0% packet loss" in output:
            n_success_test += 1
            message += f"Ping {src_name} -> {dst_name} success\n"
        else:
            message += f"Ping {src_name} -> {dst_name} failed, cannot reach {dst_name} from {src_name} :\n{output}\n"
    except Exception as e:
        message += f"Ping {src_name} -> {dst_name} error :\n{e}\n"

def traceroute_test(src_name, dst_interface_name, route, net):
    n_test += 1
    dst_address = interface_addr[dst_interface_name]
    dst_name = dst_interface_name.split("-")[0]
    dst_IP_version = "6" if ":" in dst_address else "4"
    try:
        output = net[src_name].cmd(f"traceroute -{dst_IP_version} -q 1 {dst_address}")
        hops = []
        for line in output.splitlines()[1:]:
            address = line[line.find("(")+1:line.find(")")]
            hops.append(address)
        if len(hops) != len(route):
            message += f"Traceroute {src_name} -> {dst_name} failed : expected route is {route} but got {hops}\n"
        else:
            for i in range(len(hops)):
                if hops[i] != route[i]:
                    message += f"Traceroute {src_name} -> {dst_name} failed : expected route is {route} but got {hops}\n"
                    return
            n_success_test += 1
            message += f"Traceroute {src_name} -> {dst_name} success\n"
    except Exception as e:
        message += f"Traceroute {src_name} -> {dst_name} error :\n{e}\n"

try:
    net.start()

    # TODO : Adding pre configuration commands before starting the exercice if needed
    # net["h1"].cmd("ip -6 route add default via " + interface_addr["r1-h1"])
    # ...

    IPCLI(net)

    if INGINIOUS:
        ssh_student.ssh_student()

    # TODO : Adding ping tests for the configuration
    # ping_test("h1", "h2-r2", net)
    # ...
 
    # TODO : Adding traceroute tests for the configuration
    # traceroute_test("h1", "h2-r2", [interface_addr["r1-h1"], interface_addr["r2-r1"], interface_addr["h2-r2"]], net)
    # ...

    grade = 100 if n_test == 0 else ((n_success_test / n_test) * 100)

    if INGINIOUS:
        feedback.set_grade(grade)
        feedback.set_global_feedback(message)
        feedback.set_global_result("success") if grade == 100 else feedback.set_global_result("failed")
    else:
        print(f"Grade : {grade}")
        print(f"Feedback : {message}")
        print(f"Result : success") if grade == 100 else print(f"Result : failed")

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