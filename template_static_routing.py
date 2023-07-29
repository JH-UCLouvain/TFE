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

def generate_IP_addr(interface_name, IP_version, prefix):
    while True:
        addr = ""
        if IP_version == "v4":
            if prefix[-1] != ".": prefix += "."
            n_rand = 4 - (len(prefix.split(".")) - 1)
            addr = prefix + ".".join(("%s" % random.randint(0, 255) for _ in range(n_rand)))
        elif IP_version == "v6":
            if prefix[-1] != ":": prefix += ":"
            n_rand = 8 - (len(prefix.split(":")) - 1)
            addr = prefix + ":".join(("%s" % "".join(("%s" % random.choice(("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f")) for _ in range(4))) for _ in range(n_rand)))
        else:
            raise ValueError("IP version must be \"v4\" or \"v6\"")
        if addr not in interface_addr.values():
            interface_addr[interface_name] = addr
            return addr

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        # TODO : Creating the nodes
        # h1 = self.addHost("h1", defaultRoute=None)
        # r1 = self.addRouter("r1", config=RouterConfig)
        # ...

        # TODO : Creating the links between the nodes
        # lh1r1 = self.addLink(h1, r1)
        # lh1r1[h1].addParams(ip = generate_IP_addr("h1-r1", "v6", "2001:db8:1341:1:") + "/64")
        # lh1r1[r1].addParams(ip = generate_IP_addr("r1-h1", "v6", "2001:db8:1341:1:") + "/64")
        # ...

        # TODO : Adding empty static routing tables to the routers
        # r1.addDaemon(STATIC, static_routes=[])
        # ...

        super(MyTopology, self).build(*args, **kwargs)

class Test:

    def __init__(self):
        self.n_test = 0
        self.n_success_test = 0
        self.feedback = ""

    def __addresses_are_equals(self, address1, address2):
        addr1_list = address1.split(":") if ":" in address1 else address1.split(".")
        addr2_list = address2.split(":") if ":" in address2 else address2.split(".")
        if len(addr1_list) != len(addr2_list): return False
        for i in range(len(addr1_list)):
            if addr1_list[i].lstrip('0').lower() != addr2_list[i].lstrip('0').lower(): return False
        return True

    def ping_test(self, src_name, dst_interface_name, net):
        self.n_test += 1
        dst_address = interface_addr[dst_interface_name]
        dst_name = dst_interface_name.split("-")[0]
        dst_IP_version = "6" if ":" in dst_address else "4"
        try:
            output = net[src_name].cmd(f"ping -{dst_IP_version} -c 1 -W 1 {dst_address}")
            if " 0% packet loss" in output or " 0.0% packet loss" in output:
                self.n_success_test += 1
                self.feedback += f"Ping {src_name} -> {dst_name} success\n"
            else:
                self.feedback += f"Ping {src_name} -> {dst_name} failed, cannot reach {dst_name} from {src_name} :\n{output}\n"
        except Exception as e:
            self.feedback += f"Ping {src_name} -> {dst_name} error :\n{e}\n"

    def traceroute_test(self, src_name, dst_interface_name, expected_route, net):
        self.n_test += 1
        dst_address = interface_addr[dst_interface_name]
        dst_name = dst_interface_name.split("-")[0]
        dst_IP_version = "6" if ":" in dst_address else "4"
        try:
            output = net[src_name].cmd(f"traceroute -{dst_IP_version} -q 1 {dst_address}")
            real_route = []
            for line in output.splitlines()[1:]:
                address = line[line.find("(")+1:line.find(")")]
                real_route.append(address)
            if len(real_route) != len(expected_route):
                self.feedback += f"Traceroute {src_name} -> {dst_name} failed : expected route is {expected_route} but got {real_route}\n"
            else:
                for i in range(len(real_route)):
                    if not self.__addresses_are_equals(real_route[i], expected_route[i]):
                        self.feedback += f"Traceroute {src_name} -> {dst_name} failed : expected route is {expected_route} but got {real_route}\n"
                        return
                self.n_success_test += 1
                self.feedback += f"Traceroute {src_name} -> {dst_name} success\n"
        except Exception as e:
            self.feedback += f"Traceroute {src_name} -> {dst_name} error :\n{e}\n"
    
    def send_feedback(self):
        grade = 100 if self.n_test == 0 else ((self.n_success_test / self.n_test) * 100)
        if INGINIOUS:
            feedback.set_grade(grade)
            feedback.set_global_feedback(self.feedback)
            feedback.set_global_result("success") if grade == 100 else feedback.set_global_result("failed")
        else:
            print(f"Grade : {grade}")
            print(f"Feedback : {self.feedback}")
            print(f"Result : success") if grade == 100 else print(f"Result : failed")

try:
    net = IPNet(topo=MyTopology(), allocate_IPs=False)
    net.start()

    # TODO : Adding pre configuration commands before starting the exercice if needed
    # net["h1"].cmd("ip -6 route add default via " + interface_addr["r1-h1"])
    # net["r1"].cmd("ip -6 route add " + interface_addr["h3-r3"] + "/64 via " + interface_addr["r3-r1"])
    # ...

    IPCLI(net)

    if INGINIOUS:
        ssh_student.ssh_student()

    test = Test()

    # TODO : Adding network configuration tests
    # test.ping_test("h1", "h2-r2", net)
    # test.traceroute_test("h1", "h2-r2", [interface_addr["r1-h1"], interface_addr["r2-r1"], interface_addr["h2-r2"]], net)
    # ...

    test.send_feedback()

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
