from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from subtitleparser import parse_subs

from dotenv import load_dotenv
import os
load_dotenv()


espassword = os.getenv("ES_PASSWORD")
print(espassword)
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200, 'scheme': 'https'}],
    basic_auth=('elastic', espassword),
    ca_certs='http_ca.crt'
)

es_ready_subs = parse_subs('data/Monkey.Man.2024.1080p.AMZN.WEB-DL.DDP5.1.H.264-FLUX.srt')

actions = [
    {
        "_index": "monkeymansubs",
        "_id": sub_group['sub_id'],
        "_source": sub_group
    } for sub_group in es_ready_subs
]

bulk(es, actions)