import os
import consul
import logging

from pathlib import Path
from flask import Flask, jsonify, make_response, request
from datetime import date, datetime

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello World 2 !'


@app.route('/env')
def env():
    variable = os.getenv('KTA_DEBUG_VAR')
    message = 'KTA_DEBUG_VAR={}'.format(variable)
    return message


@app.route('/environ')
def environ():
    result = {}
    for k, v in os.environ.items():
        result[k] = v
    return jsonify(result)


@app.route('/storage')
def storage():
    path = os.getenv('KTA_LOG_PATH')

    file_name = '{}.log'.format(date.today())
    path = Path(path) / file_name

    message = '{}: Hello from app!\n'.format(datetime.now().time())

    with path.open('a') as f:
        f.write(message)

    return message


@app.route('/consul')
def consul_view():
    host = os.getenv('KTA_CONSUL_HOST')
    port = os.getenv('KTA_CONSUL_PORT', 8500)
    if not host:
        return jsonify({'message': 'no KTA_CONSUL_HOST environment variable'})

    c = consul.Consul(host=host, port=int(port))
    index, value = c.kv.get('kta/counter')

    if not value:
        counter = 0
    else:
        counter = int(value['Value'])

    counter += 1

    c.kv.put('kta/counter', str(counter))

    return jsonify({'counter': counter})


@app.route('/authtest')
def auth_test():
    result = ""
    for k, v in request.headers:
        result += "%s => %s\n" % (k, v)
    app.logger.info(result)
    return make_response(result, 200)


if __name__ == '__main__':
    app.run(debug=True)
