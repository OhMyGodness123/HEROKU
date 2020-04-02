from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {'Москва': random.choice(['213044/206a1f918127cba47675', '1652229/03bc32b99d3b281eb819']),
          'Париж': random.choice(['1652229/5b4a953bd72fca05206c', '1652229/edc1e9af15e3a32848b7']),
          'Нью-Йорк': random.choice(['213044/22f829f8be888b165ced', '1030494/1749f6b18d2ac260280c'])
          }

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'привет! Ты кто?'
        sessionStorage[user_id] = {
            'first_name': None
        }
        return
    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышал. давай еще разок'
        else:
            sessionStorage[user_id]['text'] = first_name
            res['response']['text'] = f'прикольна ' \
                                      f'{first_name.title()}, я Алиса прикинь.' \
                                      f' какой город хочешь поглядеть'
            res['response']['buttons'] = [
                {
                    'title': city.title(),
                    'hide': True
                } for city in cities
            ]
    else:
        city = get_city(req)
        if city in cities:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Этот город я знаю. лол'
            res['response']['card']['image_id'] = random.choice(cities[city])
            res['response']['text'] = 'ахахха я угадала а ты лох'
        else:
            res['response']['text'] = 'я хз чо это'


def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
