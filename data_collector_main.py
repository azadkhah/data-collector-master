import json
import logging
import sys
import traceback
from threading import Thread
from time import sleep

import schedule
from elasticsearch import Elasticsearch

from fwdns import ip_domain
from tor import tor_ip_updater
from whois_domain import whois_tld, domain_downloader, domain_to_ip
from whois_range import range_updater, range_api

main_logger = logging.getLogger()
main_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
main_logger.addHandler(handler)
main_logger.disabled=True


def run_threaded(job_func, args=()):
    job_thread = Thread(target=job_func, args=args)
    job_thread.start()


# schedule.every().hour.do(run_threaded, tor_ip_updater.update_tor_ip, args=())
schedule.every(10).days.do(run_threaded, domain_downloader.update_domains, args=())
schedule.every(4).hours.do(run_threaded, ip_domain.update, args=())
schedule.every(15).days.do(run_threaded, whois_tld.worker, args=("com",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("net",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("ir",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("org",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("io",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("cn",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("edu",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("co",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("us",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("biz",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("gov",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("info",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("in",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("jp",))
schedule.every(20).days.do(run_threaded, whois_tld.worker, args=("ru",))
schedule.every(2).hours.do(run_threaded, domain_to_ip.domain_to_ip, args=())
schedule.every(5).days.do(run_threaded, range_updater.update_range, args=())
schedule.every(1).days.do(run_threaded, range_api.update_with_batch_api, args=(6,))


# schedule.every(30).days.do(run_threaded, range_api.update_with_api, args=("ipinfo", 1,))
# schedule.every(30).days.do(run_threaded, range_api.update_with_api, args=("ip-api", 2,))
# schedule.every(30).days.do(run_threaded, range_api.update_with_api, args=("ipstack", 1,))


def schedule_thread():
    while True:
        try:
            schedule.run_pending()
            sleep(60)
        except:
            logging.info(traceback.format_exc())


def init_run():
    # run_threaded(tor_ip_updater.update_tor_ip, args=())
    # run_threaded(range_updater.update_range, args=())
    run_threaded(domain_downloader.update_domains, args=())
    sleep(1000)
    run_threaded(range_api.update_with_batch_api, args=(6,))
    run_threaded(domain_to_ip.domain_to_ip, args=())
    run_threaded(ip_domain.update, args=())
    run_threaded(whois_tld.worker, args=("com",))
    run_threaded(whois_tld.worker, args=("net",))
    run_threaded(whois_tld.worker, args=("ir",))
    run_threaded(whois_tld.worker, args=("org",))
    run_threaded(whois_tld.worker, args=("io",))
    run_threaded(whois_tld.worker, args=("cn",))
    run_threaded(whois_tld.worker, args=("edu",))
    run_threaded(whois_tld.worker, args=("co",))
    run_threaded(whois_tld.worker, args=("us",))
    run_threaded(whois_tld.worker, args=("biz",))
    run_threaded(whois_tld.worker, args=("gov",))
    run_threaded(whois_tld.worker, args=("info",))
    run_threaded(whois_tld.worker, args=("in",))
    run_threaded(whois_tld.worker, args=("jp",))
    run_threaded(whois_tld.worker, args=("ru",))
    # run_threaded(range_updater.update_range, args=())
    # run_threaded(range_api.update_with_api, args=("ipinfo", 1))
    # run_threaded(range_api.update_with_api, args=("ip-api", 2))
    # run_threaded(range_api.update_with_api, args=("ipstack", 1))


if __name__ == '__main__':

    json_file = open("config.json")
    config = json.load(json_file)
    # es = Elasticsearch(hosts="127.0.0.1:9200")
    es = Elasticsearch(hosts=config["elastic_ip"])
    if not es.indices.exists(index="whois_range"):
        mapping = {
            "mappings": {
                "properties": {
                    "route": {
                        "type": "ip_range"
                    },
                    "mnt-by": {
                        "type": "text"
                    },
                    "origin": {
                        "type": "text"
                    },
                    "descr": {
                        "type": "text"
                    },
                    "last-modified": {
                        "type": "text"
                    }
                }
            }
        }
        es.indices.create(index='whois_range', body=mapping)
    if not es.indices.exists(index="whois_domain"):
        mapping = {
            "mappings": {
                "properties": {
                    "ipaddr": {
                        "type": "ip"
                    }
                }
            }
        }
        es.indices.create(index="whois_domain",body=mapping)
    if not es.indices.exists(index="tor_ip"):
        mapping = {
            "mappings": {
                "properties": {
                    "ipaddr": {
                        "type": "ip"
                    }
                }
            }
        }
        es.indices.create(index='tor_ip',body=mapping)
    if not es.indices.exists(index="error_index"):
        es.indices.create(index='error_index')
    if not es.indices.exists(index="ip_to_domain"):
        mapping = {
            "mappings": {
                "properties": {
                    "ipaddr": {
                        "type": "ip"
                    }
                }
            }
        }
        es.indices.create(index='ip_to_domain',body=mapping)

    init_run()
    thread1 = Thread(target=schedule_thread, )
    thread1.start()
    # while True:
    #     try:
    #         try:
    #             range_updater.update_range()
    #             sleep(60)
    #         except:
    #             logging.info(traceback.format_exc())
    #         try:
    #             range_api.update_with_api("ipinfo", 2)
    #             sleep(60)
    #         except:
    #             logging.info(traceback.format_exc())
    #         try:
    #             range_api.update_with_api("ip-api", 2)
    #             sleep(60)
    #         except:
    #             logging.info(traceback.format_exc())
    #         try:
    #             range_api.update_with_api("ipstack", 2)
    #         except:
    #             logging.info(traceback.format_exc())
    #         sleep(30 * 24 * 60 * 60)
    #     except:
    #         logging.info(traceback.format_exc())
