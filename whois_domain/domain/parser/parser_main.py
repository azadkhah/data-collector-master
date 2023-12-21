import json
from datetime import datetime
from time import sleep

import whois

from domain.config import database
from domain.database.stroge_manager import WhoisStorageManager
from domain.database.elstic_domain_manager import WhoisElasticManager


def main():
    storage_manager = WhoisStorageManager(database.MONGO_HOST, database.MONGO_PORT, database.MONGO_DATABASE,
                                          database.DATABASE_SUCCESS_COLLECTION, database.DATABASE_ERROR_COLLECTION,
                                          database.DATABASE_QUEUE_COLLECTION)

    elastic_manager = WhoisElasticManager(database.ELASTIC_HOST, database.ELASTIC_PORT, database.ELASTIC_INDEX_NAME)
    cursor = storage_manager.success_whois_list()

    alexa_list = open("../../files/alexa.csv", "r")
    cisco_list = open("../../files/cisco.csv", "r")

    alexa_rank = {}
    cisco_rank = {}

    for item in alexa_list:
        values = item.split(",")
        alexa_rank[values[1].strip()] = values[0].strip()

    for item in cisco_list:
        values = item.split(",")
        cisco_rank[values[1].strip()] = values[0].strip()

    error_count = 0
    records = []
    for item in cursor:
        try:
            entry = whois.WhoisEntry.load(item['domain'], item['text'])
            if not entry['domain_name']:
                pass
            else:
                entry['_id'] = item['domain']
                entry['tld'] = item['tld']
                domain_name = entry['domain_name']

                entry['domain_name'] = str(domain_name).lower()

                if item['domain'] in alexa_rank:
                    entry['alexa_rank'] = alexa_rank[item['domain']]

                if item['domain'] in cisco_rank:
                    entry['cisco_rank'] = cisco_rank[item['domain']]

                if 'updated_date' in entry:
                    if entry['updated_date'] and not isinstance(entry['updated_date'], datetime) and not isinstance(
                            entry['updated_date'], list):
                        del entry['updated_date']

                if 'creation_date' in entry:
                    if entry['creation_date'] and not isinstance(entry['creation_date'], datetime) and not isinstance(
                            entry['creation_date'], list):
                        del entry['creation_date']

                if 'expiration_date' in entry:
                    if entry['expiration_date'] and not isinstance(entry['expiration_date'],
                                                                   datetime) and not isinstance(
                        entry['expiration_date'], list):
                        del entry['expiration_date']
                # print(entry)
                keys = []
                for key, value in entry.items():
                    if not entry[key]:
                        keys.append(key)
                for key in keys:
                    del entry[key]
                records.append(entry)
                # print(entry)
        except Exception as e:
            error_count += 1

        try:
            if len(records) == 1000:
                elastic_manager.insert(records)
                records = []
        except Exception as e:
            records = []
            print(e)

    if len(records) > 0:
        elastic_manager.insert(records)


pass

if __name__ == '__main__':
    main()
