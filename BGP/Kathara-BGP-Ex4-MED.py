#!/bin/python3
# Author : Jeremy Holodiline

# LAB SETUP
from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab
lab = Lab("Kathara BGP - Ex4 MED")

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
asBr1 = lab.new_machine(f"as{ex.get_asn('B')}r1", **{"image": "kathara/frr"})

lab.connect_machine_to_link(asAr1.name, "A", 0)
lab.connect_machine_to_link(asAr2.name, "A", 0)

lab.connect_machine_to_link(asAr1.name, "B", 1)
lab.connect_machine_to_link(asBr1.name, "B", 0)

lab.connect_machine_to_link(asAr2.name, "C", 1)
lab.connect_machine_to_link(asBr1.name, "C", 1)

ranges = [("10.0.0.0","10.255.255.255"), ("172.16.0.0","172.31.255.255"), ("192.168.0.0","192.168.255.255")]

mask = 24
asAr1_asAr2_subnet = ex.generate_subnet_addr(ranges, mask)
asAr1_asAr2_addr = ex.generate_intf_addr(f"{asAr1.name}-{asAr2.name}", asAr1_asAr2_subnet, mask)
asAr2_asAr1_addr = ex.generate_intf_addr(f"{asAr2.name}-{asAr1.name}", asAr1_asAr2_subnet, mask)

asAr1_asBr1_subnet = ex.generate_subnet_addr(ranges, mask)
asAr1_asBr1_addr = ex.generate_intf_addr(f"{asAr1.name}-{asBr1.name}", asAr1_asBr1_subnet, mask)
asBr1_asAr1_addr = ex.generate_intf_addr(f"{asBr1.name}-{asAr1.name}", asAr1_asBr1_subnet, mask)

asAr2_asBr1_subnet = ex.generate_subnet_addr(ranges, mask)
asAr2_asBr1_addr = ex.generate_intf_addr(f"{asAr2.name}-{asBr1.name}", asAr2_asBr1_subnet, mask)
asBr1_asAr2_addr = ex.generate_intf_addr(f"{asBr1.name}-{asAr2.name}", asAr2_asBr1_subnet, mask)

# ROUTER ASAR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr1_asAr2_addr}/{ex.subnet_addr[asAr1_asAr2_subnet]} dev eth0",
    f"ip addr add {asAr1_asBr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]} dev eth1",
    "systemctl start frr"
], f"{asAr1.name}.startup")

asAr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('A')}",
    f"network {asAr1_asBr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]}",
    f"network {asAr1_asAr2_addr}/{ex.subnet_addr[asAr1_asAr2_subnet]}",
    f"neighbor {asBr1_asAr1_addr} remote-as {ex.get_asn('B')}",
    f"neighbor {asAr2_asAr1_addr} remote-as {ex.get_asn('A')}",
    f"neighbor {asAr2_asAr1_addr} next-hop-self"
], "/etc/frr/frr.conf")

asAr1.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asAr1.create_file_from_list(["service integrated-vtysh-config", f"hostname {asAr1.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASAR2 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr2_asAr1_addr}/{ex.subnet_addr[asAr1_asAr2_subnet]} dev eth0",
    f"ip addr add {asAr2_asBr1_addr}/{ex.subnet_addr[asAr2_asBr1_subnet]} dev eth1",
    "systemctl start frr"
], f"{asAr2.name}.startup")

asAr2.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('A')}",
    f"network {asAr2_asBr1_addr}/{ex.subnet_addr[asAr2_asBr1_subnet]}",
    f"network {asAr2_asAr1_addr}/{ex.subnet_addr[asAr1_asAr2_subnet]}",
    f"neighbor {asBr1_asAr2_addr} remote-as {ex.get_asn('B')}",
    f"neighbor {asAr1_asAr2_addr} remote-as {ex.get_asn('A')}",
    f"neighbor {asAr1_asAr2_addr} next-hop-self"
], "/etc/frr/frr.conf")

asAr2.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asAr2.create_file_from_list(["service integrated-vtysh-config", f"hostname {asAr2.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASBR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asBr1_asAr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]} dev eth0",
    f"ip addr add {asBr1_asAr2_addr}/{ex.subnet_addr[asAr2_asBr1_subnet]} dev eth1",
    "systemctl start frr"
], f"{asBr1.name}.startup")

asBr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    f"router bgp {ex.get_asn('B')}",
    f"network {asBr1_asAr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]}",
    f"network {asBr1_asAr2_addr}/{ex.subnet_addr[asAr2_asBr1_subnet]}",
    f"neighbor {asAr1_asBr1_addr} remote-as {ex.get_asn('A')}",
    f"neighbor {asAr2_asBr1_addr} remote-as {ex.get_asn('A')}"
], "/etc/frr/frr.conf")

asBr1.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asBr1.create_file_from_list(["service integrated-vtysh-config", f"hostname {asBr1.name}-frr"], "/etc/frr/vtysh.conf")

try:
    # STARTING THE LAB + RUN CLIENT
    print("Starting lab ...")
    Kathara.get_instance().deploy_lab(lab=lab)
    ex.run_client()

    # EXERCICE EVALUATION
    ex.show_ip_bgp_test(asBr1.name, [ex.to_ignore, f"{asAr1_asAr2_subnet}/{ex.subnet_addr[asAr1_asAr2_subnet]}", ex.to_ignore, ex.to_ignore, ex.to_ignore, f"{ex.get_asn('A')}", "i"], True,
        f"{asBr1.name} knows {asAr1.name}-{asAr2.name} subnet in his BGP table",
        f"{asBr1.name} does not know {asAr1.name}-{asAr2.name} subnet in his BGP table, make sure you have created and applied the route map that accepts all routes for all routers")

    ex.show_ip_bgp_test(asBr1.name, ["*>", f"{asAr1_asAr2_subnet}/{ex.subnet_addr[asAr1_asAr2_subnet]}", f"{asAr2_asBr1_addr}", ex.to_ignore, ex.to_ignore, f"{ex.get_asn('A')}", "i"], True,
        f"{asBr1.name} knows {asAr1.name}-{asAr2.name} subnet in his BGP table with {asAr2.name} as the best route",
        f"{asBr1.name} does not know {asAr1.name}-{asAr2.name} subnet in his BGP table or {asAr2.name} is not the best route, make sure you have created and applied the route map that modifies the MED attribute to the correct route")

    # SHOW FEEDBACK
    ex.send_feedback()

except Exception as e:
    ex.send_feedback(0, "crash", f"Error from the Kathara script : {e}")

finally:
    # STOPPING THE LAB
    Kathara.get_instance().undeploy_lab(lab=lab)