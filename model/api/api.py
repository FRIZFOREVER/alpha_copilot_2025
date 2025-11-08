from flask import Flask, json, jsonify, request

app = Flask(__name__)

@app.route('/ping')
def ping():
    return "", 200

@app.route('/message', methods=['POST'])
def message():
    # Выводим тело запроса
    if request.data:
        try:
            request_data = request.get_json()
            print("Тело запроса:", json.dumps(request_data, ensure_ascii=False, indent=2))
        except:
            print("Тело запроса (raw):", request.data.decode('utf-8'))
    
    # Создаем ответ в требуемом формате
    answer = {
        "message": "Сообщение получено успешно",
        "is_support_needed": False
    }
    
    return jsonify(answer), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)