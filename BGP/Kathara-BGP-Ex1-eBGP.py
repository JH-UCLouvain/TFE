#!/bin/python3
# Author : Jeremy Holodiline

# LAB SETUP
from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab
lab = Lab("Kathara BGP - Ex1 Enable eBGP")

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
asBr1 = lab.new_machine(f"as{ex.get_asn('B')}r1", **{"image": "kathara/frr"})

lab.connect_machine_to_link(asAr1.name, "A", 0)
lab.connect_machine_to_link(asBr1.name, "A", 0)

ranges = [("10.0.0.0","10.255.255.255"), ("172.16.0.0","172.31.255.255"), ("192.168.0.0","192.168.255.255")]

lo_mask = 32
asAr1_lo_addr = ex.generate_intf_addr(f"{asAr1.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)
asBr1_lo_addr = ex.generate_intf_addr(f"{asBr1.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)

mask = 24
asAr1_asBr1_subnet = ex.generate_subnet_addr(ranges, mask)
asAr1_asBr1_addr = ex.generate_intf_addr(f"{asAr1.name}-{asBr1.name}", asAr1_asBr1_subnet, mask)
asBr1_asAr1_addr = ex.generate_intf_addr(f"{asBr1.name}-{asAr1.name}", asAr1_asBr1_subnet, mask)

# ROUTER ASAR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr1_lo_addr}/{ex.subnet_addr[asAr1_lo_addr]} dev lo",
    f"ip addr add {asAr1_asBr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]} dev eth0",
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

# ROUTER ASBR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asBr1_lo_addr}/{ex.subnet_addr[asBr1_lo_addr]} dev lo",
    f"ip addr add {asBr1_asAr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]} dev eth0",
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

try:
    # STARTING THE LAB + RUN CLIENT
    print("Starting lab ...")
    Kathara.get_instance().deploy_lab(lab=lab)
    ex.run_client()
    
    ex.exec_cmd("as62r1", "vtysh -c 'configure terminal' -c 'router bgp 62' -c 'network 172.17.186.17/24' -c 'network 192.168.112.6/32' -c 'neighbor 172.17.186.19 remote-as 6' -c 'exit' -c 'exit' -c 'write memory'")
    ex.exec_cmd("as6r1", "vtysh -c 'configure terminal' -c 'router bgp 6' -c 'network 172.17.186.19/24' -c 'network 172.31.5.45/32' -c 'neighbor 172.17.186.17 remote-as 62' -c 'exit' -c 'exit' -c 'write memory'")
    ex.run_client()

    # EXERCICE EVALUATION
    for a in lab.machines.keys():
        for b in lab.machines.keys():
            if a != b:
                b_a_addr = ex.intf_addr[f"{b}-{a}"]
                b_lo = ex.intf_addr[f"{b}-lo"]

                ex.in_output_test(a, f"vtysh -c 'show ip bgp neighbors {b_a_addr}'",
                    f"BGP neighbor is {b_a_addr}, remote AS {ex.get_router_asn(b)}, local AS {ex.get_router_asn(a)}, external link",
                    f"{a} has {b} as neighbor in his BGP database",
                    f"{a} has not {b} as neighbor in his BGP database, make sure you have announced {b} as a neighbor with the correct subnet address and AS number")

                ex.show_ip_bgp_test(a, ["*>", f"{b_lo}/{ex.subnet_addr[b_lo]}", f"{b_a_addr}", ex.to_ignore, ex.to_ignore, f"{ex.get_router_asn(b)}", "i"], True,
                    f"{a} knows {b} loopback address in his BGP routing table",
                    f"{a} does not know {b} loopback address in his BGP routing table, make sure you have announced {b} loopback address to the network")

    # SHOW FEEDBACK
    ex.send_feedback()

except Exception as e:
    ex.send_feedback(0, "crash", f"Error from the Kathara script : {e}")

finally:
    # STOPPING THE LAB
    Kathara.get_instance().undeploy_lab(lab=lab)