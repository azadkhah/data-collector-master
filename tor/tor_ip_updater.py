import json
import logging
import sys
import traceback

import requests
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


def update_tor_ip():
    try:
        logging.info("update_tor_ip started")
        torbulkexitlist = "torbulkexitlist.txt"
        exit_addresses = "exit-addresses.txt"

        logging.info("dling " + exit_addresses[:-4])
        url = "http://188.34.137.49:5000/" + exit_addresses[:-4]
        r = requests.get(url, verify=False)
        open(exit_addresses, 'wb').write(r.content)

        logging.info("dling " + torbulkexitlist[:-4])
        url = "http://188.34.137.49:5000/" + torbulkexitlist[:-4]
        r = requests.get(url, allow_redirects=True)
        open(torbulkexitlist, 'wb').write(r.content)

        logging.info("load config.json")
        json_file = open("config.json")
        config = json.load(json_file)

        client = Elasticsearch(hosts=config["elastic_ip"])

        tor_doc = {}
        for line in open(exit_addresses, "r"):
            try:
                parts = line.split(" ")
                if not parts[0].__eq__("ExitNode") and len(tor_doc) == 0:
                    continue
                if parts[0].__eq__("ExitNode"):
                    tor_doc = {}
                    tor_doc["ExitNode"] = parts[1]
                if parts[0].__eq__("Published"):
                    tor_doc["Published"] = parts[1] + " " + parts[2]
                if parts[0].__eq__("LastStatus"):
                    tor_doc["LastStatus"] = parts[1] + " " + parts[2]
                if parts[0].__eq__("ExitAddress"):
                    tor_doc["ipaddr"] = parts[1]
                    s = Search().using(client).index("tor_ip").query("match", _id=tor_doc['ipaddr'])
                    response = s.execute()
                    find = False
                    tor_hit = None
                    if len(response["hits"]["hits"]) > 0:
                        for hit in s:
                            if str(hit.ipaddr).__eq__(tor_doc["ipaddr"]):
                                find = True
                                tor_hit = hit
                                break
                    if find is False:
                        client.index("tor_ip", id=tor_doc['ipaddr'], body=tor_doc)
                        logging.info("new record" + str(tor_doc))
                    else:
                        if not str(tor_doc["LastStatus"]).__eq__(tor_hit.LastStatus):
                            logging.info("update tor record")
                            client.update("tor_ip", tor_hit.meta.id, body={"doc": {"LastStatus": tor_doc["LastStatus"]}})
                    tor_doc = {}

                # if parts[0].__eq__("ExitAddress"):
                #     tor_doc["ipaddr"] = parts[1]
                #     s = Search().using(client).index("tor_ip").query("match", _id=tor_doc['ipaddr'])
                #     response = s.execute()
                #     find = False
                #     tor_hit=None
                #     if len(response["hits"]["hits"]) > 0:
                #         for hit in s:
                #             if str(hit.ipaddr).__eq__(tor_doc["ipaddr"]):
                #                 find = True
                #                 tor_hit=hit
                #                 break
                #     if find is False:
                #         client.index("tor_ip",id=tor_doc['ipaddr'], body=tor_doc)
                #         logging.info("new record"+str(tor_doc))
                #     else:
                #         logging.info("update_tor_ip started")
                #         client.update("tor_ip", tor_hit.meta.id, body={"doc": {"LastStatus": tor_doc["LastStatus"]}})
                #     tor_doc = {}
                # if parts[0].__eq__("LastStatus"):
                #     tor_doc["LastStatus"] = parts[1] + parts[2]
                # if parts[0].__eq__("Published"):
                #     tor_doc["Published"] = parts[1] + parts[2]
                # if parts[0].__eq__("ExitNode"):
                #     tor_doc = {}
                #     tor_doc["ExitNode"] = parts[1]
            except:
                tor_doc = {}
                logging.info(traceback.format_exc())
    except:
        logging.info(traceback.format_exc())

# if __name__ == '__main__':
#     update_tor_ip()
