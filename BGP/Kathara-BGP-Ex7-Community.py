#!/bin/python3
# Author : Jeremy Holodiline

# LAB SETUP
from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab
lab = Lab("Kathara BGP - Ex7 Community")

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
asCr1 = lab.new_machine(f"as{ex.get_asn('C')}r1", **{"image": "kathara/frr"})
asDr1 = lab.new_machine(f"as{ex.get_asn('D')}r1", **{"image": "kathara/frr"})

lab.connect_machine_to_link(asAr1.name, "A", 0)
lab.connect_machine_to_link(asBr1.name, "A", 0)

lab.connect_machine_to_link(asBr1.name, "B", 1)
lab.connect_machine_to_link(asCr1.name, "B", 0)

lab.connect_machine_to_link(asBr1.name, "D", 2)
lab.connect_machine_to_link(asDr1.name, "D", 0)

mask = 24
asAr1_asBr1_subnet = ex.generate_subnet_addr(4, mask)
asAr1_asBr1_addr = ex.generate_intf_addr(f"{asAr1.name}-{asBr1.name}", asAr1_asBr1_subnet, mask)
asBr1_asAr1_addr = ex.generate_intf_addr(f"{asBr1.name}-{asAr1.name}", asAr1_asBr1_subnet, mask)

asBr1_asCr1_subnet = ex.generate_subnet_addr(4, mask)
asBr1_asCr1_addr = ex.generate_intf_addr(f"{asBr1.name}-{asCr1.name}", asBr1_asCr1_subnet, mask)
asCr1_asBr1_addr = ex.generate_intf_addr(f"{asCr1.name}-{asBr1.name}", asBr1_asCr1_subnet, mask)

asBr1_asDr1_subnet = ex.generate_subnet_addr(4, mask)
asBr1_asDr1_addr = ex.generate_intf_addr(f"{asBr1.name}-{asDr1.name}", asBr1_asDr1_subnet, mask)
asDr1_asBr1_addr = ex.generate_intf_addr(f"{asDr1.name}-{asBr1.name}", asBr1_asDr1_subnet, mask)

# ROUTER ASAR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asAr1_asBr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]} dev eth0",
    "systemctl start frr"
], f"{asAr1.name}.startup")

asAr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    "route-map ACCEPT_ALL permit 20",
    "exit",
    f"router bgp {ex.get_asn('A')}",
    f"network {asAr1_asBr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]}",
    f"neighbor {asBr1_asAr1_addr} remote-as {ex.get_asn('B')}",
    f"neighbor {asBr1_asAr1_addr} route-map ACCEPT_ALL in",
    f"neighbor {asBr1_asAr1_addr} route-map ACCEPT_ALL out"
], "/etc/frr/frr.conf")

asAr1.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asAr1.create_file_from_list(["service integrated-vtysh-config", f"hostname {asAr1.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASBR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asBr1_asAr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]} dev eth0",
    f"ip addr add {asBr1_asCr1_addr}/{ex.subnet_addr[asBr1_asCr1_subnet]} dev eth1",
    f"ip addr add {asBr1_asDr1_addr}/{ex.subnet_addr[asBr1_asDr1_subnet]} dev eth2",
    "systemctl start frr"
], f"{asBr1.name}.startup")

asBr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    "route-map ACCEPT_ALL permit 20",
    "exit",
    f"router bgp {ex.get_asn('B')}",
    f"network {asBr1_asAr1_addr}/{ex.subnet_addr[asAr1_asBr1_subnet]}",
    f"network {asBr1_asCr1_addr}/{ex.subnet_addr[asBr1_asCr1_subnet]}",
    f"network {asBr1_asDr1_addr}/{ex.subnet_addr[asBr1_asDr1_subnet]}",
    f"neighbor {asAr1_asBr1_addr} remote-as {ex.get_asn('A')}",
    f"neighbor {asAr1_asBr1_addr} route-map ACCEPT_ALL in",
    f"neighbor {asAr1_asBr1_addr} route-map ACCEPT_ALL out",
    f"neighbor {asCr1_asBr1_addr} remote-as {ex.get_asn('C')}",
    f"neighbor {asCr1_asBr1_addr} route-map ACCEPT_ALL in",
    f"neighbor {asCr1_asBr1_addr} route-map ACCEPT_ALL out",
    f"neighbor {asDr1_asBr1_addr} remote-as {ex.get_asn('D')}",
    f"neighbor {asDr1_asBr1_addr} route-map ACCEPT_ALL in",
    f"neighbor {asDr1_asBr1_addr} route-map ACCEPT_ALL out"
], "/etc/frr/frr.conf")

asBr1.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asBr1.create_file_from_list(["service integrated-vtysh-config", f"hostname {asBr1.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASCR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asCr1_asBr1_addr}/{ex.subnet_addr[asBr1_asCr1_subnet]} dev eth0",
    "systemctl start frr"
], f"{asCr1.name}.startup")

asCr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    "route-map ACCEPT_ALL permit 20",
    "exit",
    f"router bgp {ex.get_asn('C')}",
    f"network {asCr1_asBr1_addr}/{ex.subnet_addr[asBr1_asCr1_subnet]}",
    f"neighbor {asBr1_asCr1_addr} remote-as {ex.get_asn('B')}",
    f"neighbor {asBr1_asCr1_addr} route-map ACCEPT_ALL in",
    f"neighbor {asBr1_asCr1_addr} route-map ACCEPT_ALL out"
], "/etc/frr/frr.conf")

asCr1.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asCr1.create_file_from_list(["service integrated-vtysh-config", f"hostname {asCr1.name}-frr"], "/etc/frr/vtysh.conf")

# ROUTER ASDR1 SETUP
lab.create_file_from_list([
    f"ip addr add {asDr1_asBr1_addr}/{ex.subnet_addr[asBr1_asDr1_subnet]} dev eth0",
    "systemctl start frr"
], f"{asDr1.name}.startup")

asDr1.create_file_from_list([
    "password zebra",
    "enable password zebra",
    "route-map ACCEPT_ALL permit 20",
    "exit",
    f"router bgp {ex.get_asn('D')}",
    f"network {asDr1_asBr1_addr}/{ex.subnet_addr[asBr1_asDr1_subnet]}",
    f"neighbor {asBr1_asDr1_addr} remote-as {ex.get_asn('B')}",
    f"neighbor {asBr1_asDr1_addr} route-map ACCEPT_ALL in",
    f"neighbor {asBr1_asDr1_addr} route-map ACCEPT_ALL out"
], "/etc/frr/frr.conf")

asDr1.create_file_from_list(ex.set_daemons(["zebra","bgpd"]), "/etc/frr/daemons")
asDr1.create_file_from_list(["service integrated-vtysh-config", f"hostname {asDr1.name}-frr"], "/etc/frr/vtysh.conf")

try:
    # STARTING THE LAB + RUN CLIENT
    print("Starting lab ...")
    Kathara.get_instance().deploy_lab(lab=lab)
    ex.run_client()

    # EXERCICE EVALUATION
    ex.show_ip_bgp_test(asBr1.name, [ex.to_ignore, f"{asAr1_asBr1_subnet}/{ex.subnet_addr[asAr1_asBr1_subnet]}", f"{asAr1_asBr1_addr}", ex.to_ignore, ex.to_ignore, f"{ex.get_asn('A')}", "i"], True,
        f"{asBr1.name} knows a route to AS{ex.get_asn('A')}",
        f"{asBr1.name} does not know any route to AS{ex.get_asn('A')}, it must be able to reach it")

    ex.show_ip_bgp_test(asCr1.name, [ex.to_ignore, f"{asAr1_asBr1_subnet}/{ex.subnet_addr[asAr1_asBr1_subnet]}", f"{asBr1_asCr1_addr}", ex.to_ignore, ex.to_ignore, f"{ex.get_asn('B')}", "i"], True,
        f"{asCr1.name} knows a route to AS{ex.get_asn('A')}",
        f"{asCr1.name} does not know any route to AS{ex.get_asn('A')}, it must be able to reach it")

    ex.show_ip_bgp_test(asDr1.name, [ex.to_ignore, f"{asAr1_asBr1_subnet}/{ex.subnet_addr[asAr1_asBr1_subnet]}", f"{asBr1_asDr1_addr}", ex.to_ignore, ex.to_ignore, f"{ex.get_asn('B')}", "i"], False,
        f"{asDr1.name} does not know any route to AS{ex.get_asn('A')}",
        f"{asDr1.name} knows a route to AS{ex.get_asn('A')}, make sure you have correctly configured the community in {asAr1.name} and filtred the correct route with it in {asBr1.name}")

    ex.in_output_test(asAr1.name, f"vtysh -c 'show running-config'",
        f"set community {ex.get_asn('A')}:",
        f"set community in {asAr1.name}",
        f"no set community in {asAr1.name}, make sure you have created the route map with the set community inside")

    ex.in_output_test(asBr1.name, f"vtysh -c 'show running-config'",
        f"match community {ex.get_asn('A')}:",
        f"match community in {asBr1.name}",
        f"no match community in {asBr1.name}, make sure you have created the route map that matches the community created in {asAr1.name}")

    # SHOW FEEDBACK
    ex.send_feedback()

except Exception as e:
    ex.send_feedback(0, "crash", f"Error from the Kathara script : {e}")

finally:
    # STOPPING THE LAB
    Kathara.get_instance().undeploy_lab(lab=lab)