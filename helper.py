import json
import hashlib
from itertools import groupby
from collections import namedtuple
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from subtitleparser import parse_subs

from dotenv import load_dotenv
import os
load_dotenv()

class Helper:
    def __init__(self) -> None:
        self.elasticpassword = os.getenv("ES_PASSWORD")
        self.elasticsearchhandler = Elasticsearch(
            [{'host': 'localhost', 'port': 9200, 'scheme': 'https'}],
            basic_auth=('elastic', self.elasticpassword),
            ca_certs='http_ca.crt'
        )
    def addmovietojson(self, key, value):
        file_path = "hashreference.json"
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        data[key] = value

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    def hash(self, value):
        return hashlib.sha256(value.encode()).hexdigest()
    
    def saltgen(self, value):
        ordsum = sum([ord(x) for x in value])
        return ordsum
        
    def parsesubtitle(self, fpath, movie_id):
        with open(fpath) as f:
            res = [list(g) for b, g in groupby(f, lambda x: bool(x.strip())) if b]

        Subtitle = namedtuple('Subtitle', 'sub_id start end text')

        subs = []
        for sub in res:
            if len(sub) >= 3:
                sub = [x.strip() for x in sub]
                sub_id, start_end, *content = sub
                start, end = start_end.split(' --> ')
                sub_id = int(sub_id.lstrip('\ufeff') + str(self.saltgen(movie_id)))
                text = ', '.join(content)
                subs.append(Subtitle(sub_id, start, end, text))

        es_ready_subs = []
        for index, sub_object in enumerate(subs):
            prev_sub_text = ''
            next_sub_text = ''
            if index > 0:
                prev_sub_text = subs[index - 1].text + ' '
            if index < len(subs) - 1:
                next_sub_text = ' ' + subs[index + 1].text
            es_ready_subs.append(dict(
                movie_id=movie_id,
                **sub_object._asdict(),
                overlapping_text=prev_sub_text + sub_object.text + next_sub_text
            ))

        return es_ready_subs

        
    def elasticingest(self, filepath, indexname, movieid):
        parsedsubtitle = self.parsesubtitle(filepath, movieid)
        actions = [
            {
                "_index": indexname,
                "_id": sub_group['sub_id'],
                "_source": sub_group
            } for sub_group in parsedsubtitle
        ]
        
        try:
            bulk(self.elasticsearchhandler, actions)
            return 'success'
        except Exception as e:
            return str(e)