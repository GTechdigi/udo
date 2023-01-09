
from flask import Blueprint, request
from udo.models.Metadada import Metadata
from udo.JsonResult import ok
metadata = Blueprint('metadata', __name__, url_prefix='/metadata')


@metadata.route('/list', methods=['GET'])
def connect_test():
    global metadata_result
    type = request.args.get('type')
    if type:
        metadata_result = Metadata.query.filter_by(type=type).all()
    else:
        metadata_result = Metadata.query.all()
    return ok(metadata_result)

