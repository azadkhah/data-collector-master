import json
import logging
import socket
import time
import traceback

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


def domain_to_ip():
    json_file = open("config.json")
    config = json.load(json_file)
    json_file.close()
    versions_file = open("versions.json")
    versions = json.load(versions_file)
    versions_file.close()
    hit_list = []

    client = Elasticsearch(hosts=config["elastic_ip"])

    s = Search(using=client, index="whois_domain") \
        .query("match", source="alexa") \
        .filter('range', ip_up_time={'lt': versions['domain_ip_version'][1]})
    for hit in s.scan():
        hit_list.append(hit)
        if len(hit_list) > 100000:
            break
    s = Search(using=client, index="whois_domain") \
        .query("match", source="alexa") \
        .exclude('bool', must=[Q('exists', field="domain_ip_version")])
    for hit in s.scan():
        hit_list.append(hit)
        if len(hit_list) > 100000:
            break

    s = Search(using=client, index="whois_domain") \
        .query("match", source="umbrella") \
        .filter('range', ip_up_time={'lt': versions['domain_ip_version'][1]})
    for hit in s.scan():
        hit_list.append(hit)
        if len(hit_list) > 100000:
            break
    s = Search(using=client, index="whois_domain") \
        .query("match", source="umbrella") \
        .exclude('bool', must=[Q('exists', field="domain_ip_version")])
    for hit in s.scan():
        hit_list.append(hit)
        if len(hit_list) > 100000:
            break

    s = Search(using=client, index="whois_domain").exclude('bool', must=[Q('exists', field="ip_up_time")])
    for hit in s.scan():
        hit_list.append(hit)
        if len(hit_list) > 100000:
            break
    s = Search(using=client, index="whois_domain").exclude('bool', must=[Q('exists', field="domain_ip_version")])
    for hit in s.scan():
        hit_list.append(hit)
        if len(hit_list) > 100000:
            break
    s = Search(using=client, index="whois_domain").filter('range', ip_up_time={'lt': versions['domain_ip_version'][1]})
    for hit in s.scan():
        hit_list.append(hit)
        if len(hit_list) > 100000:
            break

    if len(hit_list) == 0:
        if versions['domain_ip_version'][1] < (time.time() - (5 * 24 * 60 * 60)):
            versions_file = open("versions.json")
            versions = json.load(versions_file)
            versions['domain_ip_version'][0] = versions['domain_ip_version'][0] + 1
            versions['domain_ip_version'][1] = time.time()
            with open('versions.json', 'w') as outfile:
                json.dump(versions, outfile)
        return
    for hit in hit_list:
        try:
            # logging.info(hit)
            # ip = socket.gethostbyname(hit.domain)
            # logging.info(ip)
            # client.update("whois_domain", hit.meta.id, body={"doc": {"ipaddr": ip, "ip_up_time": time.time()}})
            result = socket.gethostbyname_ex(hit.domain)
            ipl = []
            for ip in result[2]:
                ipl.append(ip)
            client.update("whois_domain", hit.meta.id, body={"doc": {"ips": ipl, "ip_up_time": time.time(),
                                                                     "domain_ip_version": versions[
                                                                         "domain_ip_version"][0]}})
        except:
            try:
                client.update("whois_domain", hit.meta.id, body={"doc": {"error": 'true', "ip_up_time": time.time(),
                                                                         "domain_ip_version": versions[
                                                                             "domain_ip_version"][0]}})
                error_map = {}
                error_map['class'] = 'domain_to_ip'
                error_map['domain'] = hit.meta.id
                error_map['text'] = traceback.format_exc()
                error_map['error_time'] = time.time()
                client.index("error_index", body=error_map)
            except:
                logging.info(traceback.format_exc())
