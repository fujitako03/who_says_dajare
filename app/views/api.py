# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask import jsonify
from flask import request

from views import api
from models import Shareka


@api.route('/hello', methods=['GET'])
def hello():
    return jsonify(dict(data='hello world'))


@api.route('/evaluate', methods=['GET'])
def evaluate():
    dajare = request.args.get('dajare')
    shareka = Shareka(dajare)

    shareka.evaluate()
    data = shareka.to_dict()

    return jsonify(dict(data=data))
