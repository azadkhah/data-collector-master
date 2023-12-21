import json
import logging
import random
import sys
import time
import traceback
from time import sleep

import requests
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


#
# api_map = {
#     "ipinfo": {
#         "base_url": "http://ipinfo.io/",
#         "access_parameter": "token",
#         "pool": [
#             "8d5bc5badd0b13",
#             "a92375cd5a6622",
#             "2a5cabb438cd6d",
#             "44ae74bb1cdffc",
#             "05ca1feef6c6f2",
#             "9554d6670ca545",
#
#             "b7f143568032ad",
#             "02cf252c4a4b37",
#             "097b32d003c5a6",
#             "826cbfaa4b6929",
#             "43db677ec96da4",
#             "3f0dadc0e1c2b7",
#             "bf631884d7666c",
#             "a04382f09d9ec5",
#             "722bb828e12fd5",
#             "c443ed26f263d9"
#         ],
#         "response_parameters": [
#             "postal",
#             "hostname",
#             "city",
#             "region",
#             "country",
#             "loc",
#             "org",
#             "timezone"
#         ]
#     },
#     "ip-api": {
#         "base_url": "http://ip-api.com/json/",
#         "access_parameter": "token",
#         "pool": [
#             "x"
#         ],
#         "response_parameters": [
#             "country",
#             "countryCode",
#             "region",
#             "regionName",
#             "city",
#             "zip",
#             "lat",
#             "lon",
#             "timezone",
#             "isp",
#             "org",
#             "as"
#         ]
#     },
#     "ipstack": {
#         "base_url": "http://api.ipstack.com/",
#         "access_parameter": "access_key",
#         "pool": [
#             "4b97ca7f91b8b7486214ba96958adcdb",
#             "627c0cc91986500b8e9f5fc838fbf1a2",
#             "18574eb0ebd6babd5daae7cfc0e27261",
#             "16d6fa6f7c5514da750026bc729a0761",
#             "9d7ceb1d4ff5756cb9f2c93a15876276",
#             "9c5b2b6df7cab6e27a45f5e46f77f887",
#
#             "19434c226b7a75ac1ede6101b8298b09",
#             "59a96edd2461ca65e08ce7843d4570a6",
#             "0cd00ff939a0d77d8c1077eb4b27988c",
#             "9714f51bf95c0109b1cc4639948d6c3e",
#             "2d4ee818eba55b44e577006cbc2ab128",
#             "adc2f9c10352f31b26844e7390926751",
#             "6c72996e6f3247ec9974962d78d0f410",
#             "fa1df3d96f2af52c058c77679690d3b0",
#             "3c501136eefed7ab0416c34d2313fd85",
#             "9f949b40dc3c95c0dd3f4d9b0c1a4083",
#             "c25c1328f5fa29efc507fb951080b004",
#             "399cfdfaed0d4570c18ba5681af44e38",
#             "b5bdbe5eb0e9bb76bc7d33341e498a5c",
#             "2025d8de6f85d90bc059065e1f02c030",
#             "d6c1b6ad18e84bdfd3219a3259e2586d",
#             "7b47eec63174e47dfdffbe3635ebbbb3",
#             "1d402f9949da2a60b207c219ef27b74d",
#             "6bb5f8ae773e04a9f4a96ae241fff872",
#             "c6c2d521deca351cf5636da88fc7a3f1",
#             "8d7b095ea00c38520308995b5195df5e",
#             "d95a1b3ef8d8129d735178769ddb1496",
#             "d13ba0468a614b1e7d60997374d15a46",
#             "81367cf57fd84d5eb9c65d6218c83213",
#             "f0a04db0234e5fbd898f21ea6b4199e4",
#             "454a67d370899c2b70063784c5af30c8",
#             "4998aa02ec0f2219050e2ec98ef2cc11",
#             "c8859f6a54128ac9be845c478476bc92",
#             "608e963ab505f74f2619edcb9cc07c93",
#             "007181faac46b946c52b1fa1cde27f40",
#             "a4974560e56047fe173d96beeea0bdf4",
#             "6491a3547f4ad37af7bf2f2e14381319",
#             "6535a713b7821bf3d19e628fd89df25c",
#             "275d6da7cea168ea0c920fe3d17a6f5f",
#             "816f0d715aba195b3fda2530066ba0d5"
#         ],
#         "response_parameters": [
#             "type",
#             "continent_code",
#             "continent_name",
#             "country_code",
#             "country_name",
#             "region_code",
#             "region_name",
#             "city",
#             "zip",
#             "latitude",
#             "longitude"
#         ]
#     },
#     "ipapi": {
#         "base_url": "http://api.ipapi.com/",
#         "access_parameter": "access_key",
#         "pool": [
#             "6e8c168e1f8ea6730595703670ba67c2",
#             "13e0a33d9c038d40483651d4a4e8109a",
#             "c049d54fbfb10ef9b0287acaa8dcd9f6",
#             "91facd89f6f294384070ebbc0743f7d6",
#             "5dc89da496856cdef9370bff444b4326",
#
#             "45f49f454347ee90bd55c70165be3221",
#             "6f15ba5aa8ca268c41171efcfc6392d0",
#             "24a3110951d94f3ae2c9d667e1500549",
#             "b75185ccbda0e8a47c27969734c02818",
#             "1277e547de2ab5d518278c87526760d3",
#             "c43f7cde2b3208f180bb7e02696ebee6",
#             "d6a5f98574b2554c925e927e7800eb98",
#             "7160722459b06050a4305b7d6bbed9df",
#             "b11ec13ac9329200d27dc9726b5b8f48",
#             "46475cdea545c58ecd4698e99d2808c0",
#             "7a51e22536b9e2402e49f158e2802330",
#             "5e1c6dc1276b8f7c7ce1725734fe3d51",
#             "7a33b37e8eff4525e2dfe65a99c1bfe1",
#             "1ef1d0a446b2a67cd3f11babf9aa4de5",
#             "272c398cf9dc923e567b835f33a739a4",
#             "6e3b4ab7fdba189adf1da712da8a9ab2",
#             "ec3cbcb56faf5ba52c449b5279a08c5b",
#             "9bbd570c714f00585f72ed736fec22e2",
#             "aeac50f3879c9504f2ac8ea74e4860d8",
#             "66effaf633bad347b02e69e495e62e13",
#             "9752627d21c8b09f9514607a61caf132",
#             "eed092653553fde82828f05442c8e220",
#             "d48ae551b403039dc6ccc5d86329fe10",
#             "aa60080ebe510001e31f6a36003f71ce",
#             "1e19e5490eb54ace81775a1bcb511909",
#             "7ffbad180e97e65c793e93e85a2a09a5",
#             "86781266ed5cf02fbd0dc2795f18999e",
#             "d58c6934d61667131960e1f98cd0dfcf",
#             "a2dea1365374d02a6517131d32809a9f",
#             "29e0c8759d40aca6e7a12006de91cb39",
#             "eec901074b304653ac5a94e32094297a",
#             "507bcc278cc6fdccba41454d4ec4599c",
#             "897336a9f350b8d742ba0a33a4f41fa7",
#             "2ee1d77f6e20ae9152e0630866237d73"
#         ],
#         "response_parameters": [
#             "type",
#             "continent_code",
#             "continent_name",
#             "country_code",
#             "country_name",
#             "region_code",
#             "region_name",
#             "city",
#             "zip",
#             "latitude",
#             "longitude"
#         ]
#     }
# }
# api_log = logging.getLogger()
# api_log.setLevel(logging.INFO)
#
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# api_log.addHandler(handler)

#
# def update_with_ip_api_com():
#     updated_range = []
#     with open("route_json.txt", 'r') as f:
#         range_list = json.load(f)
#         print(len(range_list))
#         for obj in range_list:
#             token = api_map['ip-api.com']["pool"][random.randint(0, (len(api_map['ip-api.com']["pool"]) - 1))]
#             url = api_map['ip-api.com']["base_url"] \
#                   + obj["route"].split("/")[0] \
#                   + "?" + api_map['ip-api.com']["access_parameter"] \
#                   + "=" + token
#             r = requests.get(url, allow_redirects=True)
#             data = r.json()
#             print(data)
#             obj['ip-api:country'] = data['country']
#             obj['ip-api:countryCode'] = data['countryCode']
#             obj['ip-api:region'] = data['region']
#             obj['ip-api:regionName'] = data['regionName']
#             obj['ip-api:city'] = data['city']
#             obj['ip-api:zip'] = data['zip']
#             obj['ip-api:lat'] = data['lat']
#             obj['ip-api:lon'] = data['lon']
#             obj['ip-api:isp'] = data['isp']
#             obj['ip-api:timezone'] = data['timezone']
#             obj['ip-api:as'] = data['as']
#             obj['ip-api:org'] = data['org']
#             updated_range.append(obj)
#             sleep(2)
#         with open("route_json.txt", 'w') as w:
#             w.write(json.dumps(updated_range))
#
# def update_with_ipinfo():
#     updated_range = []
#     with open("route_json.txt", 'r') as f:
#         range_list = json.load(f)
#         print(len(range_list))
#         for obj in range_list:
#             token = api_map['ipinfo.io']["pool"][random.randint(0, (len(api_map['ipinfo.io']["pool"]) - 1))]
#             url = api_map['ipinfo.io']["base_url"] \
#                   + obj["route"].split("/")[0] \
#                   + "?" + api_map['ipinfo.io']["access_parameter"] \
#                   + "=" + token
#             r = requests.get(url, allow_redirects=True)
#             data = r.json()
#             print(data)
#             obj['ipinfo:city'] = data['city']
#             obj['ipinfo:region'] = data['region']
#             obj['ipinfo:country'] = data['country']
#             obj['ipinfo:loc'] = data['loc']
#             obj['ipinfo:org'] = data['org']
#             obj['ipinfo:timezone'] = data['timezone']
#             updated_range.append(obj)
#             sleep(2)
#         with open("route_json.txt", 'w') as w:
#             w.write(json.dumps(updated_range))

def update_with_api(api_name, sleep_time):
    try:
        json_file = open("config.json")
        config = json.load(json_file)
        api_map = config["api_map"]
        logging.info("run api:" + api_name)
        # client = Elasticsearch(hosts="81.91.137.50:9200")
        client = Elasticsearch(hosts=config["elastic_ip"])
        s = Search(using=client, index='whois_range')
        hit_list = []
        for hit in s.scan():
            hit_list.append(hit)
        for hit in hit_list:
            try:
                token = api_map[api_name]["pool"][random.randint(0, (len(api_map[api_name]["pool"]) - 1))]
                url = api_map[api_name]["base_url"] \
                      + hit.route.split("/")[0] \
                      + "?" + api_map[api_name]["access_parameter"] \
                      + "=" + token
                r = requests.get(url, allow_redirects=True)
                data = r.json()
                data['token'] = token
                # print(data)
                client.update("whois_range", hit.meta.id, body={"doc": {api_name: data}})
                sleep(sleep_time)
            except:
                logging.info(traceback.format_exc())
    except:
        logging.info(traceback.format_exc())


def update_with_batch_api(sleep_time):
    try:
        json_file = open("config.json")
        config = json.load(json_file)
        json_file.close()
        logging.info("run api: batch api ip-api")
        temp_list = []
        temp_map = {}
        # client = Elasticsearch(hosts="81.91.137.50:9200")
        client = Elasticsearch(hosts=config["elastic_ip"])
        hit_list = []
        s = Search(using=client, index="whois_range").exclude('bool', must=[Q('exists', field="whois_update_time")])
        for hit in s.scan():
            hit_list.append(hit)
            logging.info(len(hit_list))
            if len(hit_list)>100000:
                break
        s = Search(using=client, index='whois_range').filter('range', whois_update_time={
            'lt': time.time() - (10 * 24 * 60 * 60)})
        logging.info("----------------------------------------")
        for hit in s.scan():
            hit_list.append(hit)
            logging.info(len(hit_list))
            if len(hit_list)>100000:
                break
        logging.info("deprecated doc founded in whois_range: " + str(len(hit_list)))
        for hit in hit_list:
            try:
                temp_list.append(hit.route.split("/")[0])
                # temp_map[hit.meta.id]=hit.route.split("/")[0]
                temp_map[hit.route.split("/")[0]] = hit.meta.id
                if (len(temp_list) == 90):
                    url = "http://ip-api.com/batch"
                    logging.info(temp_list)
                    r = requests.post(url, allow_redirects=True, json=temp_list)
                    data = r.json()
                    logging.info(data)
                    for doc in data:
                        try:
                            doc["whois_update_time"] = time.time()
                            doc["api_name"] = "ip-api batch"
                            client.update("whois_range", temp_map[doc["query"]], body={"doc": doc})
                        except:
                            try:
                                client.update("whois_range", temp_map[doc["query"]],
                                              body={"doc": {"error": "true",
                                                            "whois_update_time": (time.time() - (5 * 24 * 60 * 60))}})
                                error_map = {}
                                error_map['class'] = 'range_api'
                                error_map['ip'] = temp_map[doc["query"]]
                                error_map['text'] = traceback.format_exc()
                                error_map['error_time'] = time.time()
                                client.index("error_index", body=error_map)
                            except:
                                logging.info(traceback.format_exc())
                    temp_list = []
                    temp_map = {}
                    sleep(sleep_time)
            except:
                logging.info(traceback.format_exc())

        if len(temp_list) < 90:
            url = "http://ip-api.com/batch"
            r = requests.post(url, allow_redirects=True, data=temp_list)
            data = r.json()
            for doc in data:
                try:
                    doc["whois_update_time"] = time.time()
                    client.update("whois_range", temp_map[doc["query"]], body={"doc": doc})
                except:
                    try:
                        client.update("whois_range", temp_map[doc["query"]],
                                      body={"doc": {"error": "true",
                                                    "whois_update_time": (time.time() - (5 * 24 * 60 * 60))}})
                        error_map = {}
                        error_map['class'] = 'range_api'
                        error_map['ip'] = temp_map[doc["query"]]
                        error_map['text'] = traceback.format_exc()
                        error_map['error_time'] = time.time()
                        client.index("error_index", body=error_map)
                    except:
                        logging.info(traceback.format_exc())
                temp_list = []
                temp_map = {}
                sleep(sleep_time)
    except:
        logging.info(traceback.format_exc())
