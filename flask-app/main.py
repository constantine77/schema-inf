from flask import Flask, render_template, request, jsonify, send_from_directory
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_json_files', methods=['POST'])
def process_json_files():
    if request.method == 'POST':
        # Read the JSON file contents
        file1_content = request.json['file1']
        file2_content = request.json['file2']

        # Load the JSON data into Python objects
        data1 = json.loads(file1_content)
        data2 = json.loads(file2_content)

        # Process the data and produce output (replace with your logic)
        output = f"File 1 has {len(data1)} items and File 2 has {len(data2)} items."

        return output

@app.route('/<path:json_file>')
def serve_json(json_file):
    json_directory = "/Users/veles/Applications/dev/schema-inf/data"  # Change this to the directory where your JSON files are located
    return send_from_directory(json_directory, json_file)

if __name__ == "__main__":
    app.run(debug=True)
