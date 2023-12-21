import gzip
import json
import logging
import shutil
import traceback
import zipfile
import requests
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


def update_domains():
    json_file = open("config.json")
    config = json.load(json_file)
    json_file.close()
    for url_r in config["domain_url"]:
        try:
            logging.info("getting domains from "+str(url_r))
            url = config["domain_url"][url_r]
            r = requests.get(url, allow_redirects=True)
            f = open('top-1m.csv.zip', 'wb')
            f.write(r.content)
            f.close()
            with zipfile.ZipFile("top-1m.csv.zip", 'r') as zip_ref:
                zip_ref.extractall()

            client = Elasticsearch(hosts=config["elastic_ip"])
            rank=1
            with open('top-1m.csv', 'r') as f:
                for line in f:
                    try:
                        line = line.rstrip().lstrip().strip()
                        domain = line.split(",")[-1]
                        ss = Search(using=client, index="whois_domain").query("match", _id=domain)
                        x = False
                        for h in ss.scan():
                            x = True
                        if x:
                            pass
                        else:
                            domain_map = {"domain": domain
                                , "tld": line.split(".")[-1]
                                , "source": str(url_r)
                                , "rank": rank
                                , "whois_veriosn": 0
                                , "update_time": 0.0}
                            client.index("whois_domain",id=domain, body=domain_map)
                    except:
                        logging.info(traceback.format_exc())
                    rank+=1
        except:
            logging.info(traceback.format_exc())
    # try:
    #     with zipfile.ZipFile("tranco_74WX.zip", 'r') as zip_ref:
    #         zip_ref.extractall()
    #     client = Elasticsearch(hosts=config["elastic_ip"])
    #     with open('tranco_74WX.csv', 'r') as f:
    #         for line in f:
    #             try:
    #                 line = line.rstrip().lstrip().strip()
    #                 domain = line.split(",")[-1]
    #                 ss = Search(using=client, index="whois_domain").query("match", _id=domain)
    #                 x = False
    #                 for h in ss.scan():
    #                     x = True
    #                 if x:
    #                     pass
    #                 else:
    #                     domain_map = {"domain": domain
    #                         , "tld": line.split(".")[-1]
    #                         , "source": "tranco"
    #                         , "update_time": 0.0}
    #                     client.index("whois_domain",id=domain, body=domain_map)
    #             except:
    #                 logging.info(traceback.format_exc())
    # except:
    #     logging.info(traceback.format_exc())
