from udo import redis
import json


def get_current_user(request):
    user_cache = redis.get('udo:auth:' + request.headers['UDO-Token'])
    result = json.loads(user_cache)
    return result['username']
