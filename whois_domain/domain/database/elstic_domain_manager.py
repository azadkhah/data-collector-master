from elasticsearch import helpers, Elasticsearch


class WhoisElasticManager:
    elastic = None
    index_name: None

    def __init__(self, ip, port, index_name):
        self.elastic = Elasticsearch(hosts=(ip + ":" + str(port)))
        self.index_name = index_name

    def insert(self, records):
        helpers.bulk(self.elastic, index=self.index_name, actions=records, chunk_size=500, request_timeout=200)
