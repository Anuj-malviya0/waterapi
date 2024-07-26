from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(current_dir, 'water.csv')

def read_csv():
    data = []
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except IOError:
        app.logger.error(f"Could not read file: {csv_file}")
    return data

def write_csv(data):
    try:
        with open(csv_file, mode='w', newline='') as file:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except IOError:
        app.logger.error(f"Could not write to file: {csv_file}")

@app.route('/fetch', methods=['GET'])
def get_inventory():
    data = read_csv()
    return jsonify(data)

@app.route('/fetch/<item_id>', methods=['GET'])
def get_item(item_id):
    data = read_csv()
    item = next((item for item in data if item["Item ID"] == item_id), None)
    if item:
        return jsonify(item)
    else:
        app.logger.info(f"Item not found: {item_id}")
        return jsonify({"error": "Item not found"}), 404

@app.route('/fetch/<item_id>', methods=['PUT'])
def update_item(item_id):
    data = read_csv()
    item = next((item for item in data if item["Item ID"] == item_id), None)
    if item:
        updated_data = request.json
        for key, value in updated_data.items():
            if key in item:
                item[key] = value
        write_csv(data)
        app.logger.info(f"Item updated: {item_id}")
        return jsonify(item)
    else:
        app.logger.info(f"Item not found for update: {item_id}")
        return jsonify({"error": "Item not found"}), 404

if __name__ == '__main__':
    app.run()
