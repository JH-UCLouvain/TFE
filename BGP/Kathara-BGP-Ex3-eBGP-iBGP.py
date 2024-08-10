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

asAr1_lo_addr = ex.generate_intf_addr(f"{asAr1.name}-lo", ex.generate_subnet_addr(ranges, 32), 32)
asAr2_lo_addr = ex.generate_intf_addr(f"{asAr2.name}-lo", ex.generate_subnet_addr(ranges, 32), 32)
asAr3_lo_addr = ex.generate_intf_addr(f"{asAr3.name}-lo", ex.generate_subnet_addr(ranges, 32), 32)

asBr1_lo_addr = ex.generate_intf_addr(f"{asBr1.name}-lo", ex.generate_subnet_addr(ranges, 32), 32)
asBr2_lo_addr = ex.generate_intf_addr(f"{asBr2.name}-lo", ex.generate_subnet_addr(ranges, 32), 32)
asBr3_lo_addr = ex.generate_intf_addr(f"{asBr3.name}-lo", ex.generate_subnet_addr(ranges, 32), 32)

mask = 24
asAr1_asBr1_subnet = ex.generate_subnet_addr(ranges, mask)
asAr1_asBr1_addr = ex.generate_intf_addr(f"{asAr1.name}-{asBr1.name}", asAr1_asBr1_subnet, mask)
asBr1_asAr1_addr = ex.generate_intf_addr(f"{asBr1.name}-{asAr1.name}", asAr1_asBr1_subnet, mask)

# ROUTER ASAR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr1_lo_addr}/{ex.subnet_addr[asAr1_lo_addr]} dev lo",
    f"ip unnumbered dev eth0",
    f"ip unnumbered dev eth1",
    f"ip addr add {asAr1_asBr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]} dev eth2",
    "systemctl start frr"
], f"{asAr1.name}.startup")

asAr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('A')}",
    "no bgp ebgp-requires-policy"
], "/etc/frr/frr.conf")

asAr1.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asAr1.create_file_from_list(["service integrated-vtysh-config", f"hostname {asAr1.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASAR2 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr2_lo_addr}/{ex.subnet_addr[asAr2_lo_addr]} dev lo",
    f"ip unnumbered dev eth0",
    f"ip unnumbered dev eth1",
    "systemctl start frr"
], f"{asAr2.name}.startup")

asAr2.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('A')}",
    "no bgp ebgp-requires-policy"
], "/etc/frr/frr.conf")

asAr2.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asAr2.create_file_from_list(["service integrated-vtysh-config", f"hostname {asAr2.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASAR3 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr3_lo_addr}/{ex.subnet_addr[asAr3_lo_addr]} dev lo",
    f"ip unnumbered dev eth0",
    f"ip unnumbered dev eth1",
    "systemctl start frr"
], f"{asAr3.name}.startup")

asAr3.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('A')}",
    "no bgp ebgp-requires-policy"
], "/etc/frr/frr.conf")

asAr3.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asAr3.create_file_from_list(["service integrated-vtysh-config", f"hostname {asAr3.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASBR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asBr1_lo_addr}/{ex.subnet_addr[asBr1_lo_addr]} dev lo",
    f"ip unnumbered dev eth0",
    f"ip unnumbered dev eth1",
    f"ip addr add {asBr1_asAr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]} dev eth2",
    "systemctl start frr"
], f"{asBr1.name}.startup")

asBr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('B')}",
    "no bgp ebgp-requires-policy"
], "/etc/frr/frr.conf")

asBr1.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asBr1.create_file_from_list(["service integrated-vtysh-config", f"hostname {asBr1.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASBR2 SETUP
lab.create_file_from_list([
    f"ip addr add {asBr2_lo_addr}/{ex.subnet_addr[asBr2_lo_addr]} dev lo",
    f"ip unnumbered dev eth0",
    f"ip unnumbered dev eth1",
    "systemctl start frr"
], f"{asBr2.name}.startup")

asBr2.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('B')}",
    "no bgp ebgp-requires-policy"
], "/etc/frr/frr.conf")

asBr2.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asBr2.create_file_from_list(["service integrated-vtysh-config", f"hostname {asBr2.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASBR3 SETUP
lab.create_file_from_list([
    f"ip addr add {asBr3_lo_addr}/{ex.subnet_addr[asBr3_lo_addr]} dev lo",
    f"ip unnumbered dev eth0",
    f"ip unnumbered dev eth1",
    "systemctl start frr"
], f"{asBr3.name}.startup")

asBr3.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('B')}",
    "no bgp ebgp-requires-policy"
], "/etc/frr/frr.conf")

asBr3.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asBr3.create_file_from_list(["service integrated-vtysh-config", f"hostname {asBr3.name}-frr"], "/etc/frr/vtysh.conf")

try:
    # STARTING THE LAB + RUN CLIENT
    print("Starting lab ...")
    Kathara.get_instance().deploy_lab(lab=lab)
    ex.run_client()

    # EXERCICE EVALUATION
    for a in lab.machines.keys():
        for b in lab.machines.keys():
            if a != b:
                b_lo = ex.intf_addr[f"{b}-lo"]
                asn_a = ex.get_router_asn(a)
                asn_b = ex.get_router_asn(b)

                if "r1" in a and "r1" in b:
                    b_a_addr = ex.intf_addr[f"{b}-{a}"]

                    ex.in_output_test(a, f"vtysh -c 'show ip bgp neighbors {b_a_addr}'",
                        f"BGP neighbor is {b_a_addr}, remote AS {ex.get_router_asn(b)}, local AS {ex.get_router_asn(a)}, external link",
                        f"{a} has {b} as neighbor in his BGP database",
                        f"{a} has not {b} as neighbor in his BGP database, make sure you have announced {b} as a neighbor with the correct subnet address and AS number")

                    ex.show_ip_bgp_test(a, ["*>", f"{b_lo}/{ex.subnet_addr[b_lo]}", f"{b_a_addr}", "0", "0", f"{ex.get_router_asn(b)}", "i"],
                        f"{a} knows {b} loopback address in his BGP routing table",
                        f"{a} does not know {b} loopback address in his BGP routing table, make sure you have announced {b} loopback address to the network")
                
                if asn_a == asn_b:
                    ex.in_output_test(a, f"vtysh -c 'show ip bgp neighbors {b_lo}'",
                        f"BGP neighbor is {b_lo}, remote AS {asn_a}, local AS {asn_a}, internal link",
                        f"{a} has {b} as neighbor in his BGP database",
                        f"{a} has not {b} as neighbor in his BGP database, make sure you have announced {b} as a neighbor with the correct loopback address")

                    ex.in_output_test(a, f"vtysh -c 'show ip bgp neighbors {b_lo}'",
                        f"Update source is lo",
                        f"{a} has his loopback address set as source for his neighbor {b}",
                        f"{a} has not his loopback address set as source for his neighbor {b}, make sure you have set the update-source parameter")

                    ex.in_output_test(a, f"vtysh -c 'show ip bgp neighbors {b_lo}'",
                        f"NEXT_HOP is always this router",
                        f"{a} is set as next hop for his neighbor {b}",
                        f"{a} is not set as next hop for his neighbor {b}, make sure you have set the next-hop-self parameter")

    # SHOW FEEDBACK
    ex.send_feedback()

except Exception as e:
    ex.send_feedback(0, "crash", f"Error from the Kathara script : {e}")

finally:
    # STOPPING THE LAB
    Kathara.get_instance().undeploy_lab(lab=lab)