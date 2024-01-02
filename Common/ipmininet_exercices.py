#!/bin/python3
# Author : Jeremy Holodiline

import random

class IPMininet_Exercice:

    def __init__(self, ip_version, store_fdbk=True):
        self.ip_version = ip_version
        self.store_fdbk = store_fdbk
        self.subnet_addr = set()
        self.intf_addr = dict()
        self.intf_names = dict()
        self.n_tests = 0
        self.n_success_tests = 0
        self.feedback = ""

    def store_feedback(self, grade, result, feedback):
        if self.store_fdbk:
            with open("tmp/student/feedback.txt", "w") as f:
                f.write(str(grade) + "\n")
                f.write(result + "\n")
                f.write(feedback)
        else:
            print(f"Grade : {grade}")
            print(f"Result : {result}")
            print(f"Feedback : {feedback}")

    def addr_to_bin(addr):
        addr_bin = ""
        if "." in addr: addr_bin = "".join(format(int(x), "08b") for x in addr.split("."))
        else: addr_bin = "".join(format(int(x, 16), "016b") for x in addr.split(":"))
        return addr_bin

    def bin_to_addr(addr_bin):
        addr = ""
        if len(addr_bin) == 32: addr = ".".join(str(int(addr_bin[i:i+8], 2)) for i in range(0, 32, 8))
        else: addr = ":".join(format(int(addr_bin[i:i+16], 2), "x") for i in range(0, 128, 16))
        return addr

    def generate_subnet_addr(self, mask):
        while True:
            addr_bin = "".join(random.choice("01") for _ in range(mask))
            n_bits = 32-mask if self.ip_version == 4 else 128-mask
            addr_bin = addr_bin + "".join("0" for _ in range(n_bits))
            is_new = True
            for sub_addr in self.subnet_addr:
                if addr_bin[:mask] == self.addr_to_bin(sub_addr)[:mask]: is_new = False
            if is_new:
                addr = self.bin_to_addr(addr_bin)
                self.subnet_addr.add(addr)
                return addr

    def generate_intf_addr(self, intf, subnet_addr, mask):
        while True:
            addr_bin = self.addr_to_bin(subnet_addr)
            n_bits = 32-mask if self.ip_version == 4 else 128-mask
            fixed = addr_bin[:-n_bits]
            generated = "".join(random.choice("01") for _ in range(n_bits))
            addr_bin = fixed + generated
            addr = self.bin_to_addr(addr_bin)
            if addr not in self.intf_addr.values():
                self.intf_addr[intf] = addr
                return addr

    def generate_intf_name(self, intf):
        while True:
            intf_name = f"{intf.split('-')[0]}-eth{random.randint(0, 99)}"
            if intf_name not in self.intf_names:
                self.intf_names[intf] = intf_name
                return intf_name

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

def run_ipmininet_exercice():
    from inginious_container_api import feedback, ssh_student

    ssh_student.ssh_student(memory_limit=512)

    lines = []
    with open("student/kvm/feedback.txt", "r") as f:
        lines = f.readlines()

    feedback.set_grade(float(lines[0].strip()))
    feedback.set_global_result(lines[1].strip())
    feedback.set_global_feedback("\n".join(lines[2:]))

"""
import sys
sys.path.insert(1, '/course/common/student/')
from ipmininet_exercices import run_ipmininet_exercice
run_ipmininet_exercice()

def generate_IP_addr_OLD(interface, version, prefix):
    while True:
        addr = ""
        if version == "v4":
            if prefix != "" and prefix[-1] != ".": prefix += "."
            n_rand = 4 - (len(prefix.split(".")) - 1)
            addr = prefix + ".".join(("%s" % random.randint(0, 255) for _ in range(n_rand)))
            addr = addr.rstrip(".")
        elif version == "v6":
            if prefix != "" and prefix[-1] != ":": prefix += ":"
            n_rand = 8 - (len(prefix.split(":")) - 1)
            addr = prefix + ":".join(("%s" % format(random.randint(0, 0xffff), "x") for _ in range(n_rand)))
            addr = addr.rstrip(":")
        else: raise ValueError("IP version must be \"v4\" or \"v6\"")
        if addr not in interface_addr.values():
            interface_addr[interface] = addr
            return addr
"""