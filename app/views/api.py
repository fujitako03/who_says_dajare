# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from flask import jsonify

from views import api


@api.route('/hello')
def hello():
    return jsonify(dict(data='hello world'))
