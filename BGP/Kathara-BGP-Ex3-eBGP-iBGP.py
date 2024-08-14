#!/bin/python3
# Author : Jeremy Holodiline

# LAB SETUP
from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab
lab = Lab("Kathara BGP - Ex3 Enable iBGP/eBGP")

import sys
sys.path.append('..')
from Common.kathara_exercices import Kathara_Exercice

ex = None
if len(sys.argv) > 2:
    print("Error: too many arguments, usage : python3 script.py [argument]")
    print("The optional argument is the seed used for the random number generation")
    sys.exit(1)
elif len(sys.argv) == 2:
    ex = Kathara_Exercice(lab=lab, random_seed=sys.argv[1])
else:
    ex = Kathara_Exercice(lab=lab)

# TOPOLOGY SETUP
asAr1 = lab.new_machine(f"as{ex.get_asn('A')}r1", **{"image": "kathara/frr"})
asAr2 = lab.new_machine(f"as{ex.get_asn('A')}r2", **{"image": "kathara/frr"})
asAr3 = lab.new_machine(f"as{ex.get_asn('A')}r3", **{"image": "kathara/frr"})

asBr1 = lab.new_machine(f"as{ex.get_asn('B')}r1", **{"image": "kathara/frr"})
asBr2 = lab.new_machine(f"as{ex.get_asn('B')}r2", **{"image": "kathara/frr"})
asBr3 = lab.new_machine(f"as{ex.get_asn('B')}r3", **{"image": "kathara/frr"})

lab.connect_machine_to_link(asAr1.name, "A", 0)
lab.connect_machine_to_link(asAr2.name, "A", 0)

lab.connect_machine_to_link(asAr1.name, "B", 1)
lab.connect_machine_to_link(asAr3.name, "B", 0)

lab.connect_machine_to_link(asAr2.name, "C", 1)
lab.connect_machine_to_link(asAr3.name, "C", 1)

lab.connect_machine_to_link(asBr1.name, "D", 0)
lab.connect_machine_to_link(asBr2.name, "D", 0)

lab.connect_machine_to_link(asBr1.name, "E", 1)
lab.connect_machine_to_link(asBr3.name, "E", 0)

lab.connect_machine_to_link(asBr2.name, "F", 1)
lab.connect_machine_to_link(asBr3.name, "F", 1)

lab.connect_machine_to_link(asAr1.name, "G", 2)
lab.connect_machine_to_link(asBr1.name, "G", 2)

ranges = [("10.0.0.0","10.255.255.255"), ("172.16.0.0","172.31.255.255"), ("192.168.0.0","192.168.255.255")]

lo_mask = 32
asAr1_lo_addr = ex.generate_intf_addr(f"{asAr1.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)
asAr2_lo_addr = ex.generate_intf_addr(f"{asAr2.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)
asAr3_lo_addr = ex.generate_intf_addr(f"{asAr3.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)
asBr1_lo_addr = ex.generate_intf_addr(f"{asBr1.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)
asBr2_lo_addr = ex.generate_intf_addr(f"{asBr2.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)
asBr3_lo_addr = ex.generate_intf_addr(f"{asBr3.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)

mask = 24
asAr1_asBr1_subnet = ex.generate_subnet_addr(ranges, mask)
asAr1_asBr1_addr = ex.generate_intf_addr(f"{asAr1.name}-{asBr1.name}", asAr1_asBr1_subnet, mask)
asBr1_asAr1_addr = ex.generate_intf_addr(f"{asBr1.name}-{asAr1.name}", asAr1_asBr1_subnet, mask)

# ROUTER ASAR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr1_lo_addr}/{ex.subnet_addr[asAr1_lo_addr]} dev lo",
    f"ip addr add {asAr1_lo_addr}/{ex.subnet_addr[asAr1_lo_addr]} dev eth0",
    f"ip addr add {asAr1_lo_addr}/{ex.subnet_addr[asAr1_lo_addr]} dev eth1",
    f"ip addr add {asAr1_asBr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]} dev eth2",
    "systemctl start frr"
], f"{asAr1.name}.startup")

asAr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('A')}",
    "no bgp ebgp-requires-policy",
    "exit",
    "interface eth0",
    "ip ospf network point-to-point",
    "exit",
    "interface eth1",
    "ip ospf network point-to-point",
    "exit",
    "router ospf",
    f"network {asAr1_lo_addr}/{ex.subnet_addr[asAr1_lo_addr]} area 0.0.0.0"
], "/etc/frr/frr.conf")

asAr1.create_file_from_list(ex.set_daemons(["zebra","bgpd","ospfd","ospf6d"]), "/etc/frr/daemons")
asAr1.create_file_from_list(["service integrated-vtysh-config", f"hostname {asAr1.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASAR2 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr2_lo_addr}/{ex.subnet_addr[asAr2_lo_addr]} dev lo",
    f"ip addr add {asAr2_lo_addr}/{ex.subnet_addr[asAr2_lo_addr]} dev eth0",
    f"ip addr add {asAr2_lo_addr}/{ex.subnet_addr[asAr2_lo_addr]} dev eth1",
    "systemctl start frr"
], f"{asAr2.name}.startup")

asAr2.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('A')}",
    "no bgp ebgp-requires-policy",
    "exit",
    "interface eth0",
    "ip ospf network point-to-point",
    "exit",
    "interface eth1",
    "ip ospf network point-to-point",
    "exit",
    "router ospf",
    f"network {asAr2_lo_addr}/{ex.subnet_addr[asAr2_lo_addr]} area 0.0.0.0"
], "/etc/frr/frr.conf")

asAr2.create_file_from_list(ex.set_daemons(["zebra","bgpd","ospfd","ospf6d"]), "/etc/frr/daemons")
asAr2.create_file_from_list(["service integrated-vtysh-config", f"hostname {asAr2.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASAR3 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr3_lo_addr}/{ex.subnet_addr[asAr3_lo_addr]} dev lo",
    f"ip addr add {asAr3_lo_addr}/{ex.subnet_addr[asAr3_lo_addr]} dev eth0",
    f"ip addr add {asAr3_lo_addr}/{ex.subnet_addr[asAr3_lo_addr]} dev eth1",
    "systemctl start frr"
], f"{asAr3.name}.startup")

asAr3.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('A')}",
    "no bgp ebgp-requires-policy",
    "exit",
    "interface eth0",
    "ip ospf network point-to-point",
    "exit",
    "interface eth1",
    "ip ospf network point-to-point",
    "exit",
    "router ospf",
    f"network {asAr3_lo_addr}/{ex.subnet_addr[asAr3_lo_addr]} area 0.0.0.0"
], "/etc/frr/frr.conf")

asAr3.create_file_from_list(ex.set_daemons(["zebra","bgpd","ospfd","ospf6d"]), "/etc/frr/daemons")
asAr3.create_file_from_list(["service integrated-vtysh-config", f"hostname {asAr3.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASBR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asBr1_lo_addr}/{ex.subnet_addr[asBr1_lo_addr]} dev lo",
    f"ip addr add {asBr1_lo_addr}/{ex.subnet_addr[asBr1_lo_addr]} dev eth0",
    f"ip addr add {asBr1_lo_addr}/{ex.subnet_addr[asBr1_lo_addr]} dev eth1",
    f"ip addr add {asBr1_asAr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]} dev eth2",
    "systemctl start frr"
], f"{asBr1.name}.startup")

asBr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('B')}",
    "no bgp ebgp-requires-policy",
    "exit",
    "interface eth0",
    "ip ospf network point-to-point",
    "exit",
    "interface eth1",
    "ip ospf network point-to-point",
    "exit",
    "router ospf",
    f"network {asBr1_lo_addr}/{ex.subnet_addr[asBr1_lo_addr]} area 0.0.0.0"
], "/etc/frr/frr.conf")

asBr1.create_file_from_list(ex.set_daemons(["zebra","bgpd","ospfd","ospf6d"]), "/etc/frr/daemons")
asBr1.create_file_from_list(["service integrated-vtysh-config", f"hostname {asBr1.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASBR2 SETUP
lab.create_file_from_list([
    f"ip addr add {asBr2_lo_addr}/{ex.subnet_addr[asBr2_lo_addr]} dev lo",
    f"ip addr add {asBr2_lo_addr}/{ex.subnet_addr[asBr2_lo_addr]} dev eth0",
    f"ip addr add {asBr2_lo_addr}/{ex.subnet_addr[asBr2_lo_addr]} dev eth1",
    "systemctl start frr"
], f"{asBr2.name}.startup")

asBr2.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('B')}",
    "no bgp ebgp-requires-policy",
    "exit",
    "interface eth0",
    "ip ospf network point-to-point",
    "exit",
    "interface eth1",
    "ip ospf network point-to-point",
    "exit",
    "router ospf",
    f"network {asBr2_lo_addr}/{ex.subnet_addr[asBr2_lo_addr]} area 0.0.0.0"
], "/etc/frr/frr.conf")

asBr2.create_file_from_list(ex.set_daemons(["zebra","bgpd","ospfd","ospf6d"]), "/etc/frr/daemons")
asBr2.create_file_from_list(["service integrated-vtysh-config", f"hostname {asBr2.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASBR3 SETUP
lab.create_file_from_list([
    f"ip addr add {asBr3_lo_addr}/{ex.subnet_addr[asBr3_lo_addr]} dev lo",
    f"ip addr add {asBr3_lo_addr}/{ex.subnet_addr[asBr3_lo_addr]} dev eth0",
    f"ip addr add {asBr3_lo_addr}/{ex.subnet_addr[asBr3_lo_addr]} dev eth1",
    "systemctl start frr"
], f"{asBr3.name}.startup")

asBr3.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('B')}",
    "no bgp ebgp-requires-policy",
    "exit",
    "interface eth0",
    "ip ospf network point-to-point",
    "exit",
    "interface eth1",
    "ip ospf network point-to-point",
    "exit",
    "router ospf",
    f"network {asBr3_lo_addr}/{ex.subnet_addr[asBr3_lo_addr]} area 0.0.0.0"
], "/etc/frr/frr.conf")

asBr3.create_file_from_list(ex.set_daemons(["zebra","bgpd","ospfd","ospf6d"]), "/etc/frr/daemons")
asBr3.create_file_from_list(["service integrated-vtysh-config", f"hostname {asBr3.name}-frr"], "/etc/frr/vtysh.conf")

try:
    # STARTING THE LAB + RUN CLIENT
    print("Starting lab ...")
    Kathara.get_instance().deploy_lab(lab=lab)
    ex.run_client()

    ex.exec_cmd(asAr1.name, f"vtysh -c 'configure terminal' -c 'router bgp {ex.get_asn('A')}' -c 'network {asAr1_asBr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]}' -c 'neighbor {asBr1_asAr1_addr} remote-as {ex.get_asn('B')}' -c 'redistribute ospf' -c 'neighbor {asAr2_lo_addr} remote-as {ex.get_asn('A')}' -c 'neighbor {asAr2_lo_addr} update-source lo' -c 'neighbor {asAr2_lo_addr} next-hop-self' -c 'neighbor {asAr3_lo_addr} remote-as {ex.get_asn('A')}' -c 'neighbor {asAr3_lo_addr} update-source lo' -c 'neighbor {asAr3_lo_addr} next-hop-self' -c 'exit' -c 'exit' -c 'write memory'")
    ex.exec_cmd(asAr2.name, f"vtysh -c 'configure terminal' -c 'router bgp {ex.get_asn('A')}' -c 'neighbor {asAr1_lo_addr} remote-as {ex.get_asn('A')}' -c 'neighbor {asAr1_lo_addr} update-source lo' -c 'neighbor {asAr1_lo_addr} next-hop-self' -c 'neighbor {asAr3_lo_addr} remote-as {ex.get_asn('A')}' -c 'neighbor {asAr3_lo_addr} update-source lo' -c 'neighbor {asAr3_lo_addr} next-hop-self' -c 'exit' -c 'exit' -c 'write memory'")
    ex.exec_cmd(asAr3.name, f"vtysh -c 'configure terminal' -c 'router bgp {ex.get_asn('A')}' -c 'neighbor {asAr1_lo_addr} remote-as {ex.get_asn('A')}' -c 'neighbor {asAr1_lo_addr} update-source lo' -c 'neighbor {asAr1_lo_addr} next-hop-self' -c 'neighbor {asAr2_lo_addr} remote-as {ex.get_asn('A')}' -c 'neighbor {asAr2_lo_addr} update-source lo' -c 'neighbor {asAr2_lo_addr} next-hop-self' -c 'exit' -c 'exit' -c 'write memory'")
    ex.exec_cmd(asBr1.name, f"vtysh -c 'configure terminal' -c 'router bgp {ex.get_asn('B')}' -c 'network {asBr1_asAr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]}' -c 'neighbor {asAr1_asBr1_addr} remote-as {ex.get_asn('A')}' -c 'redistribute ospf' -c 'neighbor {asBr2_lo_addr} remote-as {ex.get_asn('B')}' -c 'neighbor {asBr2_lo_addr} update-source lo' -c 'neighbor {asBr2_lo_addr} next-hop-self' -c 'neighbor {asBr3_lo_addr} remote-as {ex.get_asn('B')}' -c 'neighbor {asBr3_lo_addr} update-source lo' -c 'neighbor {asBr3_lo_addr} next-hop-self' -c 'exit' -c 'exit' -c 'write memory'")
    ex.exec_cmd(asBr2.name, f"vtysh -c 'configure terminal' -c 'router bgp {ex.get_asn('B')}' -c 'neighbor {asBr1_lo_addr} remote-as {ex.get_asn('B')}' -c 'neighbor {asBr1_lo_addr} update-source lo' -c 'neighbor {asBr1_lo_addr} next-hop-self' -c 'neighbor {asBr3_lo_addr} remote-as {ex.get_asn('B')}' -c 'neighbor {asBr3_lo_addr} update-source lo' -c 'neighbor {asBr3_lo_addr} next-hop-self' -c 'exit' -c 'exit' -c 'write memory'")
    ex.exec_cmd(asBr3.name, f"vtysh -c 'configure terminal' -c 'router bgp {ex.get_asn('B')}' -c 'neighbor {asBr1_lo_addr} remote-as {ex.get_asn('B')}' -c 'neighbor {asBr1_lo_addr} update-source lo' -c 'neighbor {asBr1_lo_addr} next-hop-self' -c 'neighbor {asBr2_lo_addr} remote-as {ex.get_asn('B')}' -c 'neighbor {asBr2_lo_addr} update-source lo' -c 'neighbor {asBr2_lo_addr} next-hop-self' -c 'exit' -c 'exit' -c 'write memory'")
    ex.run_client()

    # EXERCICE EVALUATION
    ex.show_ip_bgp_test(asAr2.name, [f"*>i{asBr2_lo_addr}/{ex.subnet_addr[asBr2_lo_addr]}", f"{asAr1_lo_addr}", ex.to_ignore, ex.to_ignore, ex.to_ignore, f"{ex.get_asn('B')}", "?"], True,
        f"the {asAr2.name} route to {asBr2.name} is correct",
        f"the {asAr2.name} route to {asBr2.name} does not exixts or is incorrect, please check the configurations of eBGP and iBGP")

    ex.show_ip_bgp_test(asAr2.name, [f"*>i{asBr3_lo_addr}/{ex.subnet_addr[asBr3_lo_addr]}", f"{asAr1_lo_addr}", ex.to_ignore, ex.to_ignore, ex.to_ignore, f"{ex.get_asn('B')}", "?"], True,
        f"the {asAr2.name} route to {asBr3.name} is correct",
        f"the {asAr2.name} route to {asBr3.name} does not exixts or is incorrect, please check the configurations of eBGP and iBGP")

    ex.show_ip_bgp_test(asAr3.name, [f"*>i{asBr2_lo_addr}/{ex.subnet_addr[asBr2_lo_addr]}", f"{asAr1_lo_addr}", ex.to_ignore, ex.to_ignore, ex.to_ignore, f"{ex.get_asn('B')}", "?"], True,
        f"the {asAr3.name} route to {asBr2.name} is correct",
        f"the {asAr3.name} route to {asBr2.name} does not exixts or is incorrect, please check the configurations of eBGP and iBGP")

    ex.show_ip_bgp_test(asAr3.name, [f"*>i{asBr3_lo_addr}/{ex.subnet_addr[asBr3_lo_addr]}", f"{asAr1_lo_addr}", ex.to_ignore, ex.to_ignore, ex.to_ignore, f"{ex.get_asn('B')}", "?"], True,
        f"the {asAr3.name} route to {asBr3.name} is correct",
        f"the {asAr3.name} route to {asBr3.name} does not exixts or is incorrect, please check the configurations of eBGP and iBGP")

    ex.show_ip_bgp_test(asBr2.name, [f"*>i{asAr2_lo_addr}/{ex.subnet_addr[asAr2_lo_addr]}", f"{asBr1_lo_addr}", ex.to_ignore, ex.to_ignore, ex.to_ignore, f"{ex.get_asn('A')}", "?"], True,
        f"the {asBr2.name} route to {asAr2.name} is correct",
        f"the {asBr2.name} route to {asAr2.name} does not exixts or is incorrect, please check the configurations of eBGP and iBGP")

    ex.show_ip_bgp_test(asBr2.name, [f"*>i{asAr3_lo_addr}/{ex.subnet_addr[asAr3_lo_addr]}", f"{asBr1_lo_addr}", ex.to_ignore, ex.to_ignore, ex.to_ignore, f"{ex.get_asn('A')}", "?"], True,
        f"the {asBr2.name} route to {asAr3.name} is correct",
        f"the {asBr2.name} route to {asAr3.name} does not exixts or is incorrect, please check the configurations of eBGP and iBGP")

    ex.show_ip_bgp_test(asBr3.name, [f"*>i{asAr2_lo_addr}/{ex.subnet_addr[asAr2_lo_addr]}", f"{asBr1_lo_addr}", ex.to_ignore, ex.to_ignore, ex.to_ignore, f"{ex.get_asn('A')}", "?"], True,
        f"the {asBr3.name} route to {asAr2.name} is correct",
        f"the {asBr3.name} route to {asAr2.name} does not exixts or is incorrect, please check the configurations of eBGP and iBGP")

    ex.show_ip_bgp_test(asBr3.name, [f"*>i{asAr3_lo_addr}/{ex.subnet_addr[asAr3_lo_addr]}", f"{asBr1_lo_addr}", ex.to_ignore, ex.to_ignore, ex.to_ignore, f"{ex.get_asn('A')}", "?"], True,
        f"the {asBr3.name} route to {asAr3.name} is correct",
        f"the {asBr3.name} route to {asAr3.name} does not exixts or is incorrect, please check the configurations of eBGP and iBGP")

    # SHOW FEEDBACK
    ex.send_feedback()

except Exception as e:
    ex.send_feedback(0, "crash", f"Error from the Kathara script : {e}")

finally:
    # STOPPING THE LAB
    Kathara.get_instance().undeploy_lab(lab=lab)