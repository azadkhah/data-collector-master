import json
import logging
import random
import time
import traceback

import whois
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search




def get_result_from_whois(domain):
    result = whois.whois(domain)
    if result is None:
        return None
    return result


def worker(tld):
    json_file = open("config.json")
    config = json.load(json_file)
    json_file.close()
    min_sleep = 10.0
    max_sleep = 60.0
    if tld in config["tld_configs"]:
        min_sleep = config["tld_configs"][tld]['min_sleep']
        max_sleep = config["tld_configs"][tld]['max_sleep']
    else:
        min_sleep = config["tld_configs"]['default']['min_sleep']
        max_sleep = config["tld_configs"]['default']['max_sleep']
    client = Elasticsearch(hosts=config["elastic_ip"])
    hit_list = []
    for url_r in config["domain_url"]:
        try:
            s = Search(using=client, index="whois_domain")\
                .query("match", tld=tld)\
                .query("match", source=str(url_r))\
                .filter('range', update_time={
                'lt': time.time() - (30 * 24 * 60 * 60)})
            for hit in s.scan():
                hit_list.append(hit)
        except:
            logging.info(traceback.format_exc())
    for hit in hit_list:
        logging.info("getting whois info for: "+hit.domain)
        try:
            entity = get_result_from_whois(hit.domain)
            logging.info(entity)
            if entity.text is None:
                raise ValueError('whois result is None')
            entry = whois.WhoisEntry.load(hit.domain, entity.text)
            v=-1
            try:
                v=hit.whois_veriosn
            except:
                pass
            v=v+1
            # logging.info(entry)
            client.update("whois_domain", hit.meta.id,
                          body={"doc": {"text": entity.text, "update_time": time.time(), "parsed_data": entry, "whois_veriosn": v}})

        except:
            try:
                client.update("whois_domain", hit.meta.id,
                              body={"doc": {"error": "true","update_time": (time.time() - (25 * 24 * 60 * 60))}})

                error_map = {}
                error_map['class'] = 'whois_tld'
                error_map['domain'] = hit.domain
                error_map['text'] = traceback.format_exc()
                error_map['error_time'] = time.time()
                client.index("error_index", body=error_map)
            except:
                logging.info(traceback.format_exc())
            logging.info(traceback.format_exc())
        finally:
            sleep_time = (random.random() * (max_sleep - min_sleep)) + min_sleep
            logging.info("sleepTime(" + tld + "): " + str(sleep_time))
            time.sleep(sleep_time)
