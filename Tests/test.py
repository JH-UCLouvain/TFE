output = """
BGP table version is 3, local router ID is 192.168.112.6, vrf id 0
Default local pref 100, local AS 62
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

    Network          Next Hop            Metric LocPrf Weight Path
 *  172.17.186.0/24  172.17.186.19            0             0 6 i
 *>                  0.0.0.0                  0         32768 i
 *> 172.31.5.45/32   
                 172.17.186.19            0            
        0 6 i
 *> 192.168.112.6/32 0.0.0.0                  0         32768 i

Displayed  3 routes and 4 total paths

"""
lines = output.strip().split("\n")
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
    #print(entry)
    ent = [e for e in entry.split() if e.strip()]
    print(ent)