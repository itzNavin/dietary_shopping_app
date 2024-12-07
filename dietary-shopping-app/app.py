import os
import json
import qrcode
import cv2
from flask import Flask, render_template, request, redirect, url_for
from utils import decode_barcode_opencv  # Ensure your utils.py has this function

app = Flask(__name__)

# Directory Setup
STATIC_DIR = os.path.join('static')
QR_CODES_DIR = os.path.join(STATIC_DIR, 'qr_codes')
UPLOADS_DIR = os.path.join(STATIC_DIR, 'uploads')

# Ensure directories exist
os.makedirs(QR_CODES_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Load and Save Catalog
CATALOG_FILE = 'catalog.json'

def load_catalog():
    if os.path.exists(CATALOG_FILE):
        with open(CATALOG_FILE, 'r') as file:
            return json.load(file)
    return []

def save_catalog(catalog):
    with open(CATALOG_FILE, 'w') as file:
        json.dump(catalog, file)

# QR Code Generation
def generate_qr_code(catalog):
    qr_path = os.path.join(QR_CODES_DIR, 'catalog_qr.png')
    qr = qrcode.make(json.dumps(catalog))
    qr.save(qr_path)
    return qr_path

# Routes
@app.route('/')
def index():
    catalog = load_catalog()
    qr_code_path = generate_qr_code(catalog)
    return render_template('index.html', qr_code_path=qr_code_path)

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item = {
            'name': request.form['name'],
            'nutritional_values': request.form['nutritional_values'],
            'price': request.form['price'],
            'quantity': request.form['quantity']
        }
        catalog = load_catalog()
        catalog.append(item)
        save_catalog(catalog)
        return redirect(url_for('items_list'))
    return render_template('add_items.html')

@app.route('/items_list')
def items_list():
    catalog = load_catalog()
    return render_template('items_list.html', catalog=catalog)

@app.route('/delete_item/<int:item_index>', methods=['GET'])
def delete_item(item_index):
    catalog = load_catalog()
    if 0 <= item_index < len(catalog):
        catalog.pop(item_index)
    save_catalog(catalog)
    return redirect(url_for('items_list'))

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            file_path = os.path.join(UPLOADS_DIR, file.filename)
            file.save(file_path)
            barcode_data = decode_barcode_opencv(file_path)
            if barcode_data:
                catalog = load_catalog()
                catalog.append({
                    'name': barcode_data,
                    'nutritional_values': "Unknown",
                    'price': 0,
                    'quantity': 1
                })
                save_catalog(catalog)
                return redirect(url_for('items_list'))
    return render_template('scan.html')

if __name__ == '__main__':
    app.run(debug=True)