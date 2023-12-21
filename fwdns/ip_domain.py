import json
import logging
import socket
import time
import traceback

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


def update():
    json_file = open("config.json")
    config = json.load(json_file)
    json_file.close()
    hit_list = []

    client = Elasticsearch(hosts=config["elastic_ip"])


    s = Search(using=client, index="whois_domain").exclude('bool', must=[Q('exists', field="fwdns_time")])
    for hit in s.scan():
        hit_list.append(hit)
        if len(hit_list) > 100000:
            break
    s = Search(using=client, index="whois_domain").filter('range', fwdns_time={'lt': time.time() - (5 * 24 * 60 * 60)})
    for hit in s.scan():
        hit_list.append(hit)
        if len(hit_list) > 100000:
            break
    def ()
    # s = Search(using=client, index="whois_domain")
    # for hit in s.scan():
    #     hit_list.append(hit)
    for hit in hit_list:
        try:
            logging.info(hit.domain)
            client.update("whois_domain", hit.domain,
                          body={"doc": {"fwdns_time": time.time()}})
            result = socket.gethostbyname_ex(hit.domain)
            for ip in result[2]:
                ss = Search(using=client, index="ip_to_domain").query("match", _id=ip)
                x = False
                rec = None
                for h in ss.scan():
                    rec = h
                    x = True
                if x:
                    domains = []
                    # logging.info(domains)
                    if not hit.domain in rec.domains:
                        for d in rec.domains:
                            domains.append(d)
                        domains.append(hit.domain)
                        client.update("ip_to_domain", rec.meta.id,
                                      body={"doc": {"domains": domains}})
                else:
                    new_record = {}
                    domains = [hit.domain]
                    new_record["domains"] = domains
                    new_record["ipaddr"] = ip
                    client.index("ip_to_domain", id=ip, body=new_record)
        except:
            logging.info(traceback.format_exc())
