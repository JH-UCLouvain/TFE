#!/bin/python3
# Author : Jeremy Holodiline

from Kathara.manager.Kathara import Kathara
import random
import sys

class Kathara_Exercice:

    def __init__(self, lab, random_seed=None):
        random.seed(random_seed)
        self.lab = lab
        self.n_tests = 0
        self.n_success_tests = 0
        self.feedback = ""
        self.subnet_addr = dict()
        self.intf_addr = dict()
        self.asn = dict()

    def send_feedback(self, grade=None, result=None, feedback=None):
        if grade is None: grade = 100 if self.n_tests == 0 else ((self.n_success_tests / self.n_tests) * 100)
        if result is None: result = "success" if grade == 100 else "failed"
        if feedback is None: feedback = self.feedback
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

    def generate_subnet_addr(self, ranges, mask):
        while True:
            start, end = random.choice(ranges)
            start_bin = self.addr_to_bin(start)
            end_bin = self.addr_to_bin(end)
            addr_bin = ""
            for i in range(len(start_bin)):
                if i > mask-1: addr_bin += "0"
                elif start_bin[i] == end_bin[i]: addr_bin += start_bin[i]
                else: addr_bin += random.choice("01")
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
            n_bits = 32-mask if "." in subnet_addr else 128-mask
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

    def get_asn(self, as_id):
        if as_id not in self.asn:
            random_asn = str(random.randint(1, 99))
            while random_asn in self.asn.values():
                random_asn = str(random.randint(1, 99))
            self.asn[as_id] = random_asn
        return self.asn[as_id]

    def get_router_asn(self, r_name):
        return r_name[2:r_name.find("r")]

    def run_client(self):
        for as_id, as_number in self.asn.items():
            print(f"AS number of {as_id} : {as_number} (as{as_number})")
        for intf, addr in self.intf_addr.items():
            addr_mask = 0
            for sub, mask in self.subnet_addr.items():
                if self.addr_to_bin(sub)[:mask] == self.addr_to_bin(addr)[:mask]: addr_mask = mask
            print(f"IP address of {intf} : {addr}/{addr_mask}")
        print("Enter the router name to connect to it or \"exit\".")
        print("When you are connected to a device, you can enter \"exit\" to return to the main client.")
        while True:
            sys.stdin = open("/dev/tty")
            user_input = input("> ").lower()
            if user_input == "exit":
                return
            m_exists = False
            for m in self.lab.machines.keys():
                if user_input == m: m_exists = True
            if not m_exists:
                print(f"Error : no device named \"{user_input}\"")
            else:
                print(f"Connecting to device \"{user_input}\" ...")
                Kathara.get_instance().connect_tty(user_input, lab_name=self.lab.name)

    def exec_cmd(self, node, cmd):
        try:
            output = ""
            generator = Kathara.get_instance().exec(node, cmd, lab_name=self.lab.name)
            for item in generator:
                if item[0] is not None:
                    output += item[0].decode("utf-8")
                else:
                    output += item[1].decode("utf-8")
            return output
        except Exception as e:
            self.feedback += f"{node} {cmd} error : {e}\n"

    def in_output_test(self, node, cmd, expected, success_msg, failed_msg):
        self.n_tests += 1
        output = self.exec_cmd(node, cmd)
        if expected in output:
            self.n_success_tests += 1
            self.feedback += f"Success : {success_msg}\n"
        else:
            self.feedback += f"Failed : {failed_msg}\n"

    def show_ip_bgp_test(self, node, expected, success_msg, failed_msg):
        self.n_tests += 1
        lines = self.exec_cmd(node, "vtysh -c 'show ip bgp'").strip().split("\n")
        bgp_entries = []
        in_bgp_table = False
        status = ["*", "*>"]
        for l in lines:
            stripped = l.strip()
            for s in status:
                if stripped.startswith(s):
                    bgp_entries.append(stripped)
                    in_bgp_table = True
                    break
                elif in_bgp_table and stripped != "":
                    bgp_entries[-1] += " " + stripped
                    break
                else:
                    in_bgp_table = False
        for entry in bgp_entries:
            ent = [e for e in entry.split() if e.strip()]
            if expected == ent:
                self.n_success_tests += 1
                self.feedback += f"Success : {success_msg}\n"
                return
        self.feedback += f"Failed : {failed_msg}\n"

    def set_daemons(self, daemons):
        settings = [
            'zebra=no',
            'bgpd=no',
            'ospfd=no',
            'ospf6d=no',
            'ripd=no',
            'ripngd=no',
            'isisd=no',
            'pimd=no',
            'ldpd=no',
            'nhrpd=no',
            'eigrpd=no',
            'babeld=no',
            'sharpd=no',
            'staticd=no',
            'pbrd=no',
            'bfdd=no',
            'fabricd=no',
            'vtysh_enable=yes',
            'zebra_options=" -s 90000000 --daemon -A 127.0.0.1"',
            'bgpd_options="   --daemon -A 127.0.0.1"',
            'ospfd_options="  --daemon -A 127.0.0.1"',
            'ospf6d_options=" --daemon -A ::1"',
            'ripd_options="   --daemon -A 127.0.0.1"',
            'ripngd_options=" --daemon -A ::1"',
            'isisd_options="  --daemon -A 127.0.0.1"',
            'pimd_options="  --daemon -A 127.0.0.1"',
            'ldpd_options="  --daemon -A 127.0.0.1"',
            'nhrpd_options="  --daemon -A 127.0.0.1"',
            'eigrpd_options="  --daemon -A 127.0.0.1"',
            'babeld_options="  --daemon -A 127.0.0.1"',
            'sharpd_options="  --daemon -A 127.0.0.1"',
            'staticd_options="  --daemon -A 127.0.0.1"',
            'pbrd_options="  --daemon -A 127.0.0.1"',
            'bfdd_options="  --daemon -A 127.0.0.1"',
            'fabricd_options="  --daemon -A 127.0.0.1"']
        for i in range(17):
            daemon = settings[i].split("=")[0]
            for d in daemons:
                if daemon == d:
                    settings[i] = settings[i].replace("=no", "=yes")
        return settings