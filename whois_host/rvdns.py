import logging
import traceback

import dns.reversename
import dns.resolver

from whois_host.cloud import is_cloud


def check_ipfile():
    threshold = 10
    results = []
    with open("ipf.txt") as f:
        for line in f:
            line = line.strip()
            print(line)
            ic = is_cloud(line, threshold)
            rdic = False
            try:
                i = 0
                qname = dns.reversename.from_address(line)
                answer = dns.resolver.resolve(qname, 'PTR')
                for rr in answer:
                    if i > threshold:
                        rdic = True
                        break
                    print(rr)
                    i += 1
            except:
                logging.info(traceback.format_exc())
            print(str(ic) + "   " + str(rdic))
            if ic and rdic:
                results.append(line + " --- {fw:" + str(ic) + ",rv:" + str(rdic) + "} --- share hosting")
            elif ic and not rdic:
                results.append(line + " --- {fw:" + str(ic) + ",rv:" + str(rdic) + "} --- cloud hosting")
            else:
                results.append(line + " --- {fw:" + str(ic) + ",rv:" + str(rdic) + "} --- unknown")
    with open("rs.txt") as f:
        for r in results:
            f.write(r)
