#!/bin/python3
# Author : Jeremy Holodiline

# LAB SETUP
from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab
lab = Lab("Kathara BGP - Ex2 Enable iBGP")

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

lab.connect_machine_to_link(asAr1.name, "A", 0)
lab.connect_machine_to_link(asAr2.name, "A", 0)

lab.connect_machine_to_link(asAr1.name, "B", 1)
lab.connect_machine_to_link(asAr3.name, "B", 0)

lab.connect_machine_to_link(asAr2.name, "C", 1)
lab.connect_machine_to_link(asAr3.name, "C", 1)

ranges = [("10.0.0.0","10.255.255.255"), ("172.16.0.0","172.31.255.255"), ("192.168.0.0","192.168.255.255")]

lo_mask = 32
asAr1_lo_addr = ex.generate_intf_addr(f"{asAr1.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)
asAr2_lo_addr = ex.generate_intf_addr(f"{asAr2.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)
asAr3_lo_addr = ex.generate_intf_addr(f"{asAr3.name}-lo", ex.generate_subnet_addr(ranges, lo_mask), lo_mask)

# ROUTER ASAR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr1_lo_addr}/{ex.subnet_addr[asAr1_lo_addr]} dev lo",
    f"ip unnumbered dev eth0",
    f"ip unnumbered dev eth1",
    "systemctl start frr"
], f"{asAr1.name}.startup")

asAr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('A')}",
    "no bgp ebgp-requires-policy",
    f"network {asAr1_lo_addr}/{ex.subnet_addr[asAr1_lo_addr]}"
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
    "no bgp ebgp-requires-policy",
    f"network {asAr2_lo_addr}/{ex.subnet_addr[asAr2_lo_addr]}"
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
    "no bgp ebgp-requires-policy",
    f"network {asAr3_lo_addr}/{ex.subnet_addr[asAr3_lo_addr]}"
], "/etc/frr/frr.conf")

asAr3.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asAr3.create_file_from_list(["service integrated-vtysh-config", f"hostname {asAr3.name}-frr"], "/etc/frr/vtysh.conf")

try:
    # STARTING THE LAB + RUN CLIENT
    print("Starting lab ...")
    Kathara.get_instance().deploy_lab(lab=lab)
    ex.run_client()

    ex.exec_cmd("as62r1", "vtysh -c 'configure terminal' -c 'router bgp 62' -c 'neighbor 172.24.41.108 remote-as 62' -c 'neighbor 172.24.41.108 update-source lo' -c 'neighbor 172.24.41.108 next-hop-self' -c 'neighbor 10.221.8.137 remote-as 62' -c 'neighbor 10.221.8.137 update-source lo' -c 'neighbor 10.221.8.137 next-hop-self' -c 'exit' -c 'exit' -c 'write memory'")
    ex.exec_cmd("as62r2", "vtysh -c 'configure terminal' -c 'router bgp 62' -c 'neighbor 172.19.128.55 remote-as 62' -c 'neighbor 172.19.128.55 update-source lo' -c 'neighbor 172.19.128.55 next-hop-self' -c 'neighbor 10.221.8.137 remote-as 62' -c 'neighbor 10.221.8.137 update-source lo' -c 'neighbor 10.221.8.137 next-hop-self' -c 'exit' -c 'exit' -c 'write memory'")
    ex.exec_cmd("as62r3", "vtysh -c 'configure terminal' -c 'router bgp 62' -c 'neighbor 172.19.128.55 remote-as 62' -c 'neighbor 172.19.128.55 update-source lo' -c 'neighbor 172.19.128.55 next-hop-self' -c 'neighbor 172.24.41.108 remote-as 62' -c 'neighbor 172.24.41.108 update-source lo' -c 'neighbor 172.24.41.108 next-hop-self' -c 'exit' -c 'exit' -c 'write memory'")
    ex.run_client()

    # EXERCICE EVALUATION
    for a in lab.machines.keys():
        for b in lab.machines.keys():
            if a != b:
                b_lo = ex.intf_addr[f"{b}-lo"]
                asn = ex.get_asn('A')

                ex.in_output_test(a, f"vtysh -c 'show ip bgp neighbors {b_lo}'",
                    f"BGP neighbor is {b_lo}, remote AS {asn}, local AS {asn}, internal link",
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