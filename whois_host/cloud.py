import json

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


def is_cloud(ip,limit_count):
    json_file = open("config.json")
    config = json.load(json_file)
    client = Elasticsearch(hosts=config["elastic_ip"])
    s = Search(using=client, index="whois_domain").query("match", ip=ip)
    hit_list = []
    for hit in s.scan():
        hit_list.append(hit)
    if(len(hit_list)>limit_count):
        return True
    else:
        return False

def get_all_multi_domain_by_limit_count(limit_count):
    json_file = open("config.json")
    config = json.load(json_file)
    client = Elasticsearch(hosts=config["elastic_ip"])
    res = client.search(index="whois_domain", body={"size": 0,
                                                    "aggs": {
                                                        "my-aggs": {
                                                            "terms": {
                                                                "field": "ip.keyword",
                                                                "size": 10000
                                                            },
                                                            "aggs": {
                                                                "count_bucket_selector": {
                                                                    "bucket_selector": {
                                                                        "buckets_path": {
                                                                            "count": "_count"
                                                                        },
                                                                        "script": {
                                                                            "lang": "expression",
                                                                            "inline": "count > " + str(limit_count)
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }})
    return res['aggregations']['my-aggs']["buckets"]


