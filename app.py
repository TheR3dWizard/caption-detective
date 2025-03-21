from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Welcome to the Flask Elasticsearch app!"


@app.route('/search', methods=['POST'])
def search():
    message = {
  "Actors": "Dev Patel, Sharlto Copley, Pitobash",
  "Awards": "7 wins & 20 nominations total",
  "BoxOffice": "$25,116,955",
  "Country": "United States, Canada, Singapore, India",
  "DVD": "N/A",
  "Director": "Dev Patel",
  "Genre": "Action, Crime, Thriller",
  "Language": "English, Hindi",
  "Metascore": "70",
  "Plot": "An anonymous young man unleashes a campaign of vengeance against the corrupt leaders who murdered his mother and continue to systematically victimize the poor and powerless.",
  "Poster": "https://m.media-amazon.com/images/M/MV5BOTJlNzY5OTAtNjIxNi00MTUxLWJkZjEtZDcxYTg2YWY0MjZkXkEyXkFqcGc@._V1_SX300.jpg",
  "Production": "N/A",
  "Rated": "R",
  "Ratings": [
    {
      "Source": "Internet Movie Database",
      "Value": "6.8/10"
    },
    {
      "Source": "Rotten Tomatoes",
      "Value": "89%"
    },
    {
      "Source": "Metacritic",
      "Value": "70/100"
    }
  ],
  "Released": "05 Apr 2024",
  "Response": "True",
  "Runtime": "121 min",
  "Title": "Monkey Man",
  "Type": "movie",
  "Website": "N/A",
  "Writer": "Dev Patel, Paul Angunawela, John Collee",
  "Year": "2024",
  "dialogue": "Do you know, the story of Hanuman? Mm-mm.",
  "imdbID": "tt9214772",
  "imdbRating": "6.8",
  "imdbVotes": "85,640"
    }
    return jsonify(message)

@app.route('/setup', methods=['POST'])
def setup():
    return "Index allenglishmovies (allenglishmovies) already exists."

@app.route('/insertindex', methods=['POST'])
def insertindex():
    return "succcess"

if __name__ == '__main__':
    app.run(debug=False, port=6754)