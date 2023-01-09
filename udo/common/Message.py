import json
import requests
from hashlib import sha256
import hmac
from log import logger
from udo import default_settings

log = logger


def get_sign(payload, key):
    key = key.encode('utf-8')
    message = payload.encode('utf-8')
    sign = hmac.new(key, message, sha256).digest().hex()
    log.info('sign: %s', sign)
    return sign


def send_email(data):
    try:
        values = json.dumps(data)
        app_id = default_settings.GATEWAY_APP_ID
        app_secret = default_settings.GATEWAY_APP_SECRET
        signature = get_sign(values, app_secret)
        headers = {
            'Content-Type': 'application/json',
            'X-Gateway-App-Id': app_id,
            'X-Gateway-Signature': signature
        }
        log.info("message body: %s", values.encode('utf-8'))
        res = requests.post(default_settings.GATEWAY_URL + "/message/engine/send", data=values, headers=headers)
        log.info("message res: %s", res.json())
    except Exception as e:
        log.error('send email failed', e)
