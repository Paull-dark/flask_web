from flask import Flask, jsonify, request
app = Flask('__name__')

@app.route('/json-example', methods=['POST'])
def json_example():
    request_data = request.get_json()
    language = request_data['language']
    framework = request_data['framework']

    return f'The language value is: {language}The framework value is: {framework}'

@app.route('/add_num', methods=['POST'])
def add_num():
    data = request.get_json()
    x = data['x']
    y = data['y']
    z = x + y
    retJson = {
        "z": z
    }
    return jsonify(retJson), 200


@app.route('/bye')
def bye():
    age = 31+4
    retJson = {
        'Name': 'Paul',
        'age': age,
        'phones' : [
            {
                'phoneName' : 'Iphone13',
                'phone_num' : 19990
            },
            {
                'phoneName': 'IphoneX',
                'phone_num': 8888
            }
        ]
    }

    return jsonify(retJson)

if __name__ == '__main__':
    app.run(debug=True)