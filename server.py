from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch, ConnectionError, NotFoundError
from dotenv import load_dotenv
import os
load_dotenv()


app = Flask(__name__)
espassword = os.getenv("ES_PASSWORD")
print(espassword)
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200, 'scheme': 'https'}],
    http_auth=('elastic', espassword),
    ca_certs='http_ca.crt'  # Update this path to your .crt file
)

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

if __name__ == '__main__':
    app.run(debug=True, port=6000)