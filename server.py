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

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    try:
        response = es.search(index="your_index", body={"query": {"match": {"field": query}}})
        return jsonify(response.body)
    except ConnectionError as e:
        return jsonify({"error": "Elasticsearch connection error", "details": str(e)}), 500

@app.route('/insertindex', methods=['POST'])
def insertindex():
    requestbody = request.json
    mapping = {
        "mappings": {
            "properties": {
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
                }
            }
        }
    }
    
    indexname = requestbody['indexname']
    hashedindex = hclass.hash(indexname)
    
    hclass.addmovietojson(hashedindex, indexname)
    if not es.indices.exists(index=hashedindex):
        es.indices.create(index=hashedindex, body=mapping)
        print(f"Index {hashedindex} ({indexname}) created with mapping.")
        # return (f"Index {hashedindex} ({indexname}) created with mapping.", 200)
    else:
        print(f"Index {hashedindex} ({indexname}) already exists.")
        return (f"Index {hashedindex} ({indexname}) already exists.", 409)
    
    returnvalue = hclass.elasticingest(requestbody['filepath'], hashedindex)
    
    statuscode = 200 if returnvalue == 'success' else 400
    
    return (returnvalue, statuscode)
    
    

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

if __name__ == '__main__':
    app.run(debug=True, port=6000)