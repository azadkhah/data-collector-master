import traceback
from typing import List

from pymongo import MongoClient

from domain.model.domain_raw import DomainRaw


class WhoisStorageManager:
    client = None
    database = None
    success_collection = None
    error_collection = None
    queue_collection = None

    def __init__(self, host, port, database, success_collection, error_collection, queue_collection):
        self.client = MongoClient(host, port)
        self.database = self.client[database]

        if success_collection is None:
            success_collection = 'success'

        if error_collection is None:
            error_collection = 'error'

        if queue_collection is None:
            queue_collection = 'queue'

        self.success_collection = self.database[success_collection]
        self.error_collection = self.database[error_collection]
        self.queue_collection = self.database[queue_collection]
        print(self.client.list_database_names())
        pass

    def save_data(self, tld, domain, data, text):
        try:
            document = {
                "domain": domain,
                "data": data,
                "text": text,
                "tld": tld
            }
            self.success_collection.insert_one(document)
            print(domain, data)
        except Exception as e:
            print("save_data function in storage manager throws ex :", e)
        pass

    def success_whois_list(self):
        cursor = self.success_collection.find({})
        return cursor

    def domain_list(self):
        domain_map = {}
        cursor = self.success_collection.find({}, {"domain": 1, "_id": 0})
        for item in cursor:
            domain_map[item['domain']] = 1
        return domain_map
        pass

    def error_domain_list(self):
        domain_map = {}
        cursor = self.error_collection.find({}, {"domain": 1, "_id": 0})
        for item in cursor:
            domain_map[item['domain']] = 1
        return domain_map
        pass

    def __del__(self):
        self.client.close()
        pass

    def get_success_dict(self, tld):
        domain_map = {}
        query = {}
        if tld:
            query['tld'] = tld
        cursor = self.success_collection.find(query, {"domain": 1, "_id": 0})
        for item in cursor:
            domain_map[item['domain']] = 1
        return domain_map

    def get_error_dict(self, tld):
        domain_map = {}
        query = {}
        if tld:
            query['tld'] = tld
        cursor = self.error_collection.find(query, {"domain": 1, "_id": 0})
        for item in cursor:
            domain_map[item['domain']] = 1
        return domain_map

    def get_queue_dict(self, tld):
        domain_map = {}
        query = {}
        if tld:
            query['tld'] = tld
        cursor = self.error_collection.find(query)
        for item in cursor:
            error_text = item['errors_text']
            if not error_text:
                error_text = []
            temp = DomainRaw(item['domain'], item['try_count'], item['tld'], error_text)
            temp.id = item["_id"]
            domain_map[item['domain']] = temp
        return domain_map

    def save_error_domain_row(self, domain_raw: DomainRaw):
        try:
            document = {'domain': domain_raw.domain, 'tld': domain_raw.tld, 'try_count': domain_raw.try_count,
                        'errors_text': domain_raw.errors_text}
            self.error_collection.insert_one(document)
        except Exception as e:
            print("save error domain row throws ex:", e)
        pass

    # def save_queue_items(self, items: List[DomainRaw]):
    #     item_list = []
    #     for domain_raw in items:
    #         try:
    #             document = {'domain': domain_raw.domain, 'tld': domain_raw.tld, 'try_count': domain_raw.try_count,
    #                         'errors_text': domain_raw.errors_text}
    #             item_list.append(document)
    #             if(len(item_list))
    #             self.queue_collection.insert(items)
    #             self.queue_collection.insert(items)
    #         except Exception as e:
    #             print(e)
    #     pass

    def save_queue_item(self, domain_raw: DomainRaw):
        try:
            document = {'domain': domain_raw.domain, 'tld': domain_raw.tld, 'try_count': domain_raw.try_count,
                        'errors_text': domain_raw.errors_text}
            document_id = self.queue_collection.insert_one(document).inserted_id
            domain_raw.id = document_id
        except Exception as e:
            print("save queue item throws ex:", e)
        pass

    def update_queue_item(self, domain_raw: DomainRaw):
        try:
            self.queue_collection.update_one({'_id': domain_raw.id}, {
                "$set": {"domain": domain_raw.domain, "tld": domain_raw.tld, "try_count": domain_raw.try_count,
                         "errors_text": domain_raw.errors_text}

            })
        except Exception as e:
            just_the_string = traceback.format_exc()
            print("update queue item throws ex:", just_the_string)
        pass

    def del_queue_record(self, domain):
        cursor = self.queue_collection.delete_many({"domain": domain})
        return cursor.deleted_count > 0
