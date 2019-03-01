from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

from views import api
