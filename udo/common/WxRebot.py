import requests


def push_message(message: str, we_work_robot: str, alert_list: list):
    if not message or not message.strip():
        return
    if not we_work_robot:
        return
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='+we_work_robot
    alert_user = ''
    if alert_list:
        for i in alert_list:
            alert_user = alert_user + '<@{}>'.format(i)
    param = {
        "msgtype": "markdown",
        "markdown": {"content": message + alert_user}
    }
    try:
        requests.post(url=url, json=param)
    except BaseException as e:
        print(e)

