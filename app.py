import logging
from flask import Flask, send_from_directory

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Отдаем HTML страницы
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/app')
def app_page():
    return send_from_directory('.', 'app.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/health')
def health():
    return {"status": "ok", "message": "Mini App is running"}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
