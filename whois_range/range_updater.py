import json
import logging
import sys
import traceback

import requests
import gzip
import shutil
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch, helpers


def update_range():
    try:
        json_file=open("config.json")
        config = json.load(json_file)
        json_file.close()
        logging.info("Updating range ips")
        url = 'https://ftp.ripe.net/ripe/dbase/split/ripe.db.route.gz'
        logging.info("dl ripe database")

        r = requests.get(url, allow_redirects=True)

        f = open('db.route4.gz', 'wb')
        f.write(r.content)
        f.close()
        logging.info("extract ripe db to text")

        with gzip.open('db.route4.gz', 'rb') as f_in:
            with open('db.route4.txt', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        logging.info("reading ripe db")
        # client = Elasticsearch(hosts="127.0.0.1:9200")
        client = Elasticsearch(hosts=config["elastic_ip"])
        with open('db.route4.txt', 'r', encoding='ISO-8859-1') as f:
            temp_m = {}
            for line in f:
                try:
                    if line.startswith("route:"):
                        if 'route' in temp_m:
                            s = Search().using(client).index("whois_range").query("match", route=temp_m['route'].split("/")[0])
                            response = s.execute()
                            find = False
                            if len(response["hits"]["hits"]) > 0:
                                for hit in s:
                                    if str(hit.route).__eq__(temp_m["route"]):
                                        find = True
                                        break
                                if find is False:
                                    client.index("whois_range", body=temp_m)
                                    # route_list.append(temp_m)
                            else:
                                client.index("whois_range", body=temp_m)
                                # route_list.append(temp_m)
                        temp_m = {}
                    sp = line.rstrip().split(": ")
                    if len(sp) == 2:
                        if sp[0].rstrip().lstrip() == "route":
                            temp_m = {}
                            temp_m['route'] = sp[1].rstrip().lstrip()

                        if sp[0].rstrip().lstrip() == "mnt-by":
                            temp_m['mnt-by'] = sp[1].rstrip().lstrip()

                        if sp[0].rstrip().lstrip() == "origin":
                            temp_m['origin'] = sp[1].rstrip().lstrip()

                        if sp[0].rstrip().lstrip() == "descr":
                            temp_m['descr'] = sp[1].rstrip().lstrip()

                        if sp[0].rstrip().lstrip() == "last-modified":
                            temp_m['last-modified'] = sp[1].rstrip().lstrip()
                except:
                    logging.info(traceback.format_exc())
    except:
        logging.info(traceback.format_exc())
        # main_logger.info("inserting data on elastic")
        # es = Elasticsearch(hosts="127.0.0.1:9200")
        # es = Elasticsearch(hosts="81.91.137.50:9200")
        # helpers.bulk(es, index='data_collector', actions=route_list, chunk_size=500, request_timeout=200)
