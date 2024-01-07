#!/bin/python3
# Author : Jeremy Holodiline

import random

class IPMininet_Exercice:

    def __init__(self, ip_version, store_fdbk=True):
        self.ip_version = ip_version
        self.store_fdbk = store_fdbk
        self.n_tests = 0
        self.n_success_tests = 0
        self.feedback = ""
        self.subnet_addr = dict()
        self.intf_addr = dict()
        self.intf_names = dict()
        self.correct_answer = ""
        self.student_answer = ""

    def send_feedback(self, grade=None, result=None, feedback=None):
        if grade is None: grade = 100 if self.n_tests == 0 else ((self.n_success_tests / self.n_tests) * 100)
        if result is None: result = "success" if grade == 100 else "failed"
        if feedback is None: feedback = self.feedback
        if self.store_fdbk:
            with open("tmp/student/feedback.txt", "w") as f:
                f.write(str(grade) + "\n")
                f.write(result + "\n")
                f.write(feedback)
        else:
            print(f"Grade : {grade}")
            print(f"Result : {result}")
            print(f"Feedback : {feedback}")

    def addr_to_bin(self, addr):
        addr_bin = ""
        if "." in addr: addr_bin = "".join(format(int(x), "08b") for x in addr.split("."))
        else: addr_bin = "".join(format(int(x, 16), "016b") for x in addr.split(":"))
        return addr_bin

    def bin_to_addr(self, addr_bin):
        addr = ""
        if len(addr_bin) == 32: addr = ".".join(str(int(addr_bin[i:i+8], 2)) for i in range(0, 32, 8))
        else: addr = ":".join(format(int(addr_bin[i:i+16], 2), "x") for i in range(0, 128, 16))
        return addr

    def generate_subnet_addr(self, mask):
        while True:
            addr_bin = "".join(random.choice("01") for _ in range(mask))
            n_bits = 32-mask if self.ip_version == 4 else 128-mask
            if n_bits > 0: addr_bin = addr_bin + "".join("0" for _ in range(n_bits))
            is_new = True
            for sub_addr, sub_mask in self.subnet_addr.items():
                sub_addr_bin = self.addr_to_bin(sub_addr)
                if addr_bin[:mask] == sub_addr_bin[:mask] or addr_bin[:sub_mask] == sub_addr_bin[:sub_mask]: is_new = False
            if is_new:
                addr = self.bin_to_addr(addr_bin)
                self.subnet_addr[addr] = mask
                return addr

    def generate_intf_addr(self, intf, subnet_addr, mask):
        while True:
            addr = ""
            n_bits = 32-mask if self.ip_version == 4 else 128-mask
            if n_bits > 0:
                addr_bin = self.addr_to_bin(subnet_addr)
                fixed = addr_bin[:-n_bits]
                generated = "".join(random.choice("01") for _ in range(n_bits))
                addr_bin = fixed + generated
                addr = self.bin_to_addr(addr_bin)
            else : addr = subnet_addr
            if addr not in self.intf_addr.values():
                self.intf_addr[intf] = addr
                return addr

    def generate_intf_name(self, intf):
        while True:
            intf_name = f"{intf.split('-')[0]}-eth{random.randint(0, 99)}"
            if intf_name not in self.intf_names:
                self.intf_names[intf] = intf_name
                return intf_name

    def create_link(self, iptopo_obj, node1, node2, mask):
        subnet = self.generate_subnet_addr(mask)
        name1 = node1.node
        name2 = node2.node
        link = iptopo_obj.addLink(node1, node2, intfName1=self.generate_intf_name(f"{name1}-{name2}"), intfName2=self.generate_intf_name(f"{name2}-{name1}"))
        link[node1].addParams(ip=self.generate_intf_addr(f"{name1}-{name2}", subnet, mask) + f"/{mask}")
        link[node2].addParams(ip=self.generate_intf_addr(f"{name2}-{name1}", subnet, mask) + f"/{mask}")

    def create_link_switch(self, iptopo_obj, node1, node2):
        iptopo_obj.addLink(node1, node2, intfName1=self.generate_intf_name(f"{node1}-{node2}"), intfName2=self.generate_intf_name(f"{node2}-{node1}"))

    def get_address(self, node, intf, net):
        output = ""
        intf_name = self.intf_names[intf]
        try:
            output = net[node].cmd(f"ip -{self.ip_version} addr show dev {intf_name}")
        except Exception as e:
            raise ValueError(f"{node} ip -{self.ip_version} addr show dev {intf_name} error : {e}")
        address = ""
        for line in output.splitlines():
            inet = "inet" if self.ip_version == "4" else "inet6"
            if inet in line and "scope global" in line:
                address = line.split()[1]
                break
        return address

    def ping_test(self, src, dst_intf, net):
        self.n_tests += 1
        dst_addr = self.intf_addr[dst_intf]
        dst_name = dst_intf.split("-")[0]
        output = ""
        try:
            output = net[src].cmd(f"ping -{self.ip_version} -c 1 -W 1 {dst_addr}")
        except Exception as e:
            self.feedback += f"Ping {src} -> {dst_name} error : {e}\n"
            return
        if " 0% packet loss" in output or " 0.0% packet loss" in output:
            self.n_success_tests += 1
            self.feedback += f"Ping {src} -> {dst_name} success\n"
        else:
            self.feedback += f"Ping {src} -> {dst_name} failed : {output}\n"

    def traceroute_test(self, src, dst_intf, expected_route, net):
        self.n_tests += 1
        dst_addr = self.intf_addr[dst_intf]
        dst_name = dst_intf.split("-")[0]
        output = ""
        try:
            output = net[src].cmd(f"traceroute -{self.ip_version} -q 1 {dst_addr}")
        except Exception as e:
            self.feedback += f"Traceroute {src} -> {dst_name} error : {e}\n"
            return
        real_route = []
        lines_list = output.splitlines()[1:]
        for line in lines_list:
            real_route.append(line.split()[1])
        if lines_list[0].split()[0] != "1":
            self.feedback += f"Traceroute {src} -> {dst_name} failed : {output}\n"
        elif len(real_route) != len(expected_route):
            self.feedback += f"Traceroute {src} -> {dst_name} failed : expected route is {expected_route} but got {real_route}\n"
        else:
            for i in range(len(real_route)):
                if real_route[i] != expected_route[i]:
                    self.feedback += f"Traceroute {src} -> {dst_name} failed : expected route is {expected_route} but got {real_route}\n"
                    return
            self.n_success_tests += 1
            self.feedback += f"Traceroute {src} -> {dst_name} success\n"

    def output_test(self, node, cmd, expected, success_msg, failed_msg, net):
        self.n_tests += 1
        output = ""
        try:
            output = net[node].cmd(cmd)
        except Exception as e:
            self.feedback += f"{node} {cmd} error : {e}\n"
            return
        if expected in output:
            self.n_success_tests += 1
            self.feedback += f"Success : {success_msg}\n"
        else:
            self.feedback += f"Failed : {failed_msg}\n"

    def route_test(self, src, dst_addr, way, expected, net):
        self.n_tests += 1
        output = ""
        try:
            output = net[src].cmd(f"ip -{self.ip_version} route")
        except Exception as e:
            self.feedback += f"Ip route {src} error : {e}\n"
            return
        route = f"{dst_addr} via {way}"
        route_is_there = True if route in output else False
        if route_is_there and expected:
            self.n_success_tests += 1
            self.feedback += f"Ip route {route} is in the {src} routing table : success\n"
        elif (not route_is_there) and expected:
            self.feedback += f"Ip route {route} is not in the {src} routing table : failed : it must be added\n"
        elif route_is_there and (not expected):
            self.feedback += f"Ip route {route} is in the {src} routing table : failed : it must be removed\n"
        elif (not route_is_there) and (not expected):
            self.n_success_tests += 1
            self.feedback += f"Ip route {route} is not in the {src} routing table : success\n"

    def compare_answer_test(self):
        self.n_tests += 1
        if self.student_answer == self.correct_answer:
            self.n_success_tests += 1
            self.feedback += "Success\n"
        else:
            student_str = "no answer" if self.student_answer == "" else self.student_answer
            self.feedback += f"Failed : the correct answer was {self.correct_answer} but got {student_str}\n"

def run_ipmininet_exercice():
    from inginious_container_api import feedback, ssh_student

    ssh_student.ssh_student(memory_limit=512)

    lines = []
    with open("student/kvm/feedback.txt", "r") as f:
        lines = f.readlines()

    feedback.set_grade(float(lines[0].strip()))
    feedback.set_global_result(lines[1].strip())
    feedback.set_global_feedback("\n".join(lines[2:]))