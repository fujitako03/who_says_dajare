# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask import jsonify
from flask import request
import numpy as np

from views import api
from models import Shareka
from models import Ukeruka


@api.route('/hello', methods=['GET'])
def hello():
    return jsonify(dict(data='hello world'))


@api.route('/evaluate', methods=['GET'])
def evaluate():
    dajare = request.args.get('dajare')
    shareka = Shareka(dajare)
    shareka.divide()
    shareka.evaluate()
    if not shareka.is_dajare:
        data = {'result': 0}
        return jsonify(dict(data=data))

    ukeruka = Ukeruka(dajare)
    ukeruka.evaluate()
    ukeruka_result = ukeruka.to_dict()
    data = {
        'result': ukeruka_result['result'],
        'f1': np.random.randint(low=1, high=5),
        'f2': np.random.randint(low=1, high=5),
        'f3': np.random.randint(low=1, high=5),
        'f4': np.random.randint(low=1, high=5),
        'f5': np.random.randint(low=1, high=5),
        'f6': np.random.randint(low=1, high=5),
    }
    return jsonify(dict(data=data))
