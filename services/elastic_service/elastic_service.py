from elasticsearch import Elasticsearch

from config.elastic_config import ES_URL, ELASTIC_INDEXES, ElasticAvailableIndexes

elastic_client = Elasticsearch(ES_URL)


def create_elastic_indexes_if_not_exists():
    for elastic_index in ELASTIC_INDEXES:
        if elastic_client.indices.exists(index=elastic_index):
            continue

        match elastic_index:
            case ElasticAvailableIndexes.PURCHASES.value:
                body = {
                    "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                    "mappings": {
                        "dynamic_templates": [
                            {
                                "strings_as_keywords": {
                                    "match_mapping_type": "string",
                                    "mapping": {"type": "keyword", "ignore_above": 256},
                                }
                            }
                        ],
                        "properties": {
                            "invoiceId": {"type": "keyword", "ignore_above": 128},
                            "status": {"type": "keyword", "ignore_above": 64},
                            "amount": {"type": "double"},
                            "ccy": {"type": "integer"},
                            "createdDate": {
                                "type": "date",
                                "format": "strict_date_optional_time||epoch_millis",
                            },
                            "modifiedDate": {
                                "type": "date",
                                "format": "strict_date_optional_time||epoch_millis",
                            },
                            "reference": {"type": "keyword", "ignore_above": 64},
                            "destination": {
                                "type": "text",
                                "fields": {
                                    "raw": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                        },
                    },
                }

            case ElasticAvailableIndexes.USER_ACTIVITY.value:
                body = {
                    "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                    "mappings": {
                        "dynamic_templates": [
                            {
                                "strings_as_keywords": {
                                    "match_mapping_type": "string",
                                    "mapping": {"type": "keyword", "ignore_above": 256},
                                }
                            }
                        ],
                        "properties": {
                            "activityId": {"type": "integer"},
                            "userId": {"type": "keyword", "ignore_above": 128},
                            "activityDate": {
                                "type": "date",
                                "format": "strict_date_optional_time||epoch_millis",
                            },
                            "tags": {"type": "keyword"},
                            "value": {"type": "keyword"},
                        },
                    },
                }

            case _:
                body = {
                    "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                    "mappings": {"dynamic": True},
                }

        elastic_client.indices.create(index=elastic_index, body=body)
