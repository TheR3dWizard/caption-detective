from helper import Helper
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch, ConnectionError, NotFoundError
from dotenv import load_dotenv
import os
load_dotenv()


app = Flask(__name__)
espassword = os.getenv("ES_PASSWORD")
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200, 'scheme': 'https'}],
    basic_auth=('elastic', espassword),
    ca_certs='http_ca.crt'  # Update this path to your .crt file
)
hclass = Helper()

@app.route('/')
def home():
    return "Welcome to the Flask Elasticsearch app!"

@app.route('/search', methods=['POST'])
def search():
    requestbody = request.json
    searchtemplate = {
    "query": {
        "bool": {
        "should": [
            {
            "match_phrase": {
                "text": {
                "query": requestbody['query'],
                "boost": 2
                }
            }
            },
            {
            "match_phrase": {
                "overlapping_text": {
                "query": requestbody['query']
                }
            }
            }
        ]
        }
    },
    "sort": [
        {
        "start.as_timestamp": {
            "order": "asc"
        }
        }
    ]
    }
    
    try:
        returnresponse = es.search(index='englishmovies', body=searchtemplate)
        setofallmovieids = set()
        for hit in returnresponse['hits']['hits']:
            setofallmovieids.add(hit['_source']['movie_id'])
        
        moviedetails = list()
        for movieid in setofallmovieids:
            omdbresponse, statuscode = hclass.getmoviedetailsfromIMDBID(movieid)
            if statuscode == 200:
                moviedetails.append(omdbresponse)
        
        if len(moviedetails) == 0:
            return jsonify({"error": "No movie details found."}), 404
        elif len(moviedetails) == 1:
            return jsonify(moviedetails[0]), 200
        else:
            return jsonify(moviedetails), 200    
            
    except ConnectionError as e:
        return jsonify({"error": "Elasticsearch connection error", "details": str(e)}), 500

@app.route('/setup', methods=['POST'])
def setup():
    requestbody = request.json
    mapping = {
        "mappings": {
            "properties": {
            "movie_id": {
                "type": "keyword"
            },
            "sub_id": {
                "type": "integer"
            },
            "start": {
                "type": "text",
                "fields": {
                "as_timestamp": {
                    "type": "date",
                    "format": "HH:mm:ss,SSS"
                }
                }
            },
            "end": {
                "type": "text",
                "fields": {
                "as_timestamp": {
                    "type": "date",
                    "format": "HH:mm:ss,SSS"
                }
                }
            },
            "text": {
                "type": "text"
            },
            "overlapping_text": {
                "type": "text"
            }
            }
        }
        }
    
    indexname = requestbody['indexname']
    hashedindex = requestbody['indexname']
    
    hclass.addmovietojson(hashedindex, indexname)
    if not es.indices.exists(index=hashedindex):
        es.indices.create(index=hashedindex, body=mapping)
        return (f"Index {hashedindex} ({indexname}) created with mapping.", 200)
    else:
        print(f"Index {hashedindex} ({indexname}) already exists.")
        return (f"Index {hashedindex} ({indexname}) already exists.", 409)

@app.route('/insertindex', methods=['POST'])
def insertindex():
    
    requestbody = request.json
    hashedindex = requestbody['hashedindex']
    if 'movie_name' not in requestbody:
        return jsonify({"error": "Movie name not provided."}), 400
    else:
        omdbresponse, statuscode = hclass.getmoviedetailsfromtitle(requestbody['movie_name'])
        if statuscode == 200:
            movie_id = omdbresponse['imdbID']
            print(f"Assuming {requestbody['movie_name']} is {omdbresponse['Title']} ({omdbresponse['Year']}) with IMDB ID {movie_id}.")
            returnvalue = hclass.elasticingest(requestbody['filepath'], hashedindex, movie_id)
            statuscode = 200 if returnvalue == 'success' else 400
            return (returnvalue, statuscode)
        else:
            return jsonify({"error": "Movie not found in OMDB database."}), 404
    
    

@app.route('/add', methods=['POST'])
def add():
    data = request.json
    if not data or 'index' not in data or 'body' not in data:
        return jsonify({"error": "Invalid data format"}), 400

    try:
        response = es.index(index=data['index'], body=data['body'])
        return jsonify(response.body)
    except ConnectionError as e:
        return jsonify({"error": "Elasticsearch connection error", "details": str(e)}), 500
    except NotFoundError as e:
        return jsonify({"error": "Index not found", "details": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500
        
@app.route('/deleteindex', methods=['POST'])
def deleteindex():
    indexname = request.json['indexname']
    hashedindex = hclass.hash(indexname)
    
    try:
        if es.indices.exists(index=hashedindex):
            es.indices.delete(index=hashedindex)
            print(f"Index {hashedindex} ({indexname}) deleted.")
            return jsonify({"message": f"Index {hashedindex} ({indexname}) deleted."}), 200
        else:
            print(f"Index {hashedindex} ({indexname}) does not exist.")
            return jsonify({"error": f"Index {hashedindex} ({indexname}) does not exist."}), 404
    except ConnectionError as e:
        return jsonify({"error": "Elasticsearch connection error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

@app.route('/deletehash', methods=['POST'])
def deletehash():
    indexname = request.json['indexname']
    hashedindex = request.json['indexname']
    
    try:
        if es.indices.exists(index=hashedindex):
            es.indices.delete(index=hashedindex)
            print(f"Index {hashedindex} ({indexname}) deleted.")
            return jsonify({"message": f"Index {hashedindex} ({indexname}) deleted."}), 200
        else:
            print(f"Index {hashedindex} ({indexname}) does not exist.")
            return jsonify({"error": f"Index {hashedindex} ({indexname}) does not exist."}), 404
    except ConnectionError as e:
        return jsonify({"error": "Elasticsearch connection error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=6000)