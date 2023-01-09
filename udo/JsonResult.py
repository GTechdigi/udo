from flask import jsonify
from udo.common.UdoErrors import UdoErrors
from udo.utils.BaseModel import BaseModel


def ok(data):
    if isinstance(data, BaseModel):
        data = data.to_json()
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], BaseModel):
        data_list = []
        for dat in data:
            data_list.append(dat.to_json())
        data = data_list
    return jsonify({'code': None, 'msg': None, 'success': True, 'data': data})


def ok_base_page(data, total):
    data_list = []
    if data:
        if isinstance(data[0], BaseModel):
            for dat in data:
                data_list.append(dat.to_json())
            return ok_page(data_list, total)
        else:
            return ok_page(data, total)
    else:
        return ok_page(data_list, total)


def ok_page(data_list, total):
    return jsonify({'code': None, 'msg': None, 'success': True, 'data': {'list': data_list, 'total': total}})


def failed(data: UdoErrors):
    return jsonify({'code': data.value[0], 'msg': data.value[1], 'success': False, 'data': None})


