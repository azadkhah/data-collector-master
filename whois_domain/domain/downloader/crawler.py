import json
import queue
import random
import time

import whois

from domain.database.stroge_manager import WhoisStorageManager
from domain.exception.exception import NoWhoisResultFound
from domain.model.domain_raw import DomainRaw


class Crawler:
    suffix = ''
    domains = None
    storage_manager = None
    min_sleep = 10
    max_sleep = 60

    success_list = {}
    error_list = {}
    queued_list = {}

    """
    constructor of crawl page 
    init blocking queue of requested domain
    and initialize required variables
    """

    def __init__(self, suffix, storage_manager: WhoisStorageManager, min_sleep, max_sleep):
        self.suffix = suffix
        self.domains = queue.Queue()
        self.storage_manager = storage_manager
        if min_sleep is not None:
            self.min_sleep = min_sleep
        if max_sleep is not None:
            self.max_sleep = max_sleep

        self.success_list = self.storage_manager.get_success_dict(self.suffix)
        self.queued_list = self.storage_manager.get_queue_dict(self.suffix)
        self.error_list = self.storage_manager.get_error_dict(self.suffix)

        for key in self.queued_list:
            self.domains.put(self.queued_list[key])

    # # destructor of class
    # def __del__(self):
    #     new_items = []
    #     for key in self.queued_list:
    #         if "_id" in self.queued_list[key]:
    #             self.storage_manager.update_queue_item(self.queued_list[key])
    #         else:
    #             new_items.append(self.queued_list[key])
    #     if len(new_items) > 0:
    #         self.storage_manager.save_queue_item(new_items)

    # function to use whois lib to send requested domain name and get whois result
    @staticmethod
    def get_result_from_whois(domain):
        result = whois.whois(domain)
        if result is None:
            raise NoWhoisResultFound()
        return result

    # thread function to get domain list one by one from blocking queue and fetch result
    def worker(self):
        log = '******* worker of "{}" started\n min_sleep= {}\n max_sleep= {}\n length of  queue= {}\n length ' \
              'of success= {}\n length of error= {} \n'.format(self.suffix, self.min_sleep, self.min_sleep,
                                                               len(self.queued_list), len(self.success_list),
                                                               len(self.error_list))
        print(log)
        while True:
            try:
                domain_raw = self.get_domain()
                print("domain name: {}".format(domain_raw.domain))
                from whois.parser import PywhoisError
                try:
                    print("Domain Name :\t" + domain_raw.domain)
                    entity = Crawler.get_result_from_whois(domain_raw.domain)
                    if entity.text is None:
                        self.error_fetch(domain_raw.domain, "text is none", whois_error=True)
                        continue
                    entry = whois.WhoisEntry.load(domain_raw.domain, entity.text)
                    self.storage_manager.save_data(tld=self.suffix, domain=domain_raw.domain, data=entry,
                                                   text=entity.text)
                except PywhoisError as error:
                    print("get domain throws ex:", error)
                    self.error_fetch(domain_raw.domain, str(error), whois_error=True)
                except Exception as e:
                    self.error_fetch(domain_raw.domain, str(e))
                    print("normal exception ", domain_raw.domain, e)
                finally:
                    sleep_time = random.randint(self.min_sleep, self.max_sleep)
                    time.sleep(sleep_time)
            except Exception as e:
                print(e)

    # add domain to list of domain
    def add_domain(self, domain):
        if domain in self.success_list or domain in self.error_list or domain in self.queued_list:
            return False
        else:
            raw = DomainRaw(domain, 0, self.suffix, [])
            self.storage_manager.save_queue_item(raw)
            self.domains.put(raw)
            self.queued_list[domain] = raw

    # get single domain from queued list to fetch data
    def get_domain(self):
        # while True:
        raw = self.domains.get(block=True)
        try_count = raw.try_count
        return raw
        # if try_count < 5:
        #     return raw
        # else:
        #     pass

    def success_fetch(self, domain, data, text):
        self.storage_manager.save_data(self.suffix, domain, data, text)

        self.success_list[domain] = 1
        if domain in self.queued_list:
            raw = self.queued_list[domain]
            if raw.try_count > 0:
                self.storage_manager.del_queue_record(domain=domain)
                pass
            del self.queued_list[domain]

    def error_fetch(self, domain, message, whois_error=False):
        if domain in self.queued_list:
            raw = self.queued_list[domain]
            raw.try_count = raw.try_count + 1
            try:
                raw.errors_text.append(message)
            except Exception as e:
                print("error_fetch function throws ex:", e)
            if "[Errno -3] Temporary failure in name resolution" in message or \
                    "[Errno -5] No address associated with hostname" in message or \
                    raw.try_count > 4 or \
                    whois_error:
                raw.try_count = 6
                self.storage_manager.save_error_domain_row(raw)
                self.storage_manager.del_queue_record(domain)
                self.error_list[domain] = 1
                del self.queued_list[domain]
            else:
                self.storage_manager.update_queue_item(raw)
                self.domains.put(raw)
