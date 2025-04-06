import os
import boto3
import datetime
import json
import urllib.request


def lambda_handler(event, context):
    #print(event)
    body = json.loads(event['body'])
    if body.get('check') == True:
        # 安否確認
        check_time()
    elif body.get('test') == True:
        push_line_message_test()
    else:
        deviceType = body.get('context').get('deviceType')
        if deviceType == 'WoPresence':
            # 検知時間更新
            print(body['context'])
            update_detection_time()


def update_detection_time():
    #===========================
    # 検知時間の更新(環境変数を使用)
    #===========================
    now = datetime.datetime.now()
    now_JST = now + datetime.timedelta(hours=9)
    print('detection: ' + now_JST.strftime('%Y-%m-%d %H:%M:%S'))
    lambda_client = boto3.client('lambda')
    # 環境変数全てを指定しないと消えてしまうので注意
    lambda_client.update_function_configuration(
        FunctionName='human_detection',
        Environment={
            'Variables': {
                'PREVIOUS_DETECTION_TIME': now.strftime('%Y-%m-%d %H:%M:%S'),
                'PREVIOUS_DETECTION_TIME_JST': now_JST.strftime('%Y-%m-%d %H:%M:%S'),
                'LINE_USER_ID': os.environ.get('LINE_USER_ID'),
                'LINE_SECRET_TOKEN': os.environ.get('LINE_SECRET_TOKEN')
            }
        }
    )

def check_time():
    #===========================
    # 最終動体検知から指定した時間が経過してるかチェック
    #===========================
    now = datetime.datetime.now()
    previous_detection_time = datetime.datetime.strptime(os.environ.get('PREVIOUS_DETECTION_TIME'), '%Y-%m-%d %H:%M:%S')
    diff_time = now - previous_detection_time
    add_time = previous_detection_time + datetime.timedelta(hours=8)
    
    if add_time < now:
        push_line_message()

def push_line_message():
    #===========================
    # LINEへのPUSHメッセージ作成
    #===========================
    previous_detection_time_jst = datetime.datetime.strptime(os.environ.get('PREVIOUS_DETECTION_TIME'), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=9)
    message = [
        {'type':'text','text':previous_detection_time_jst.strftime('%Y/%m/%d %H:%M:%S') + '以降から動態検知がありません。安否確認してください。'}
    ]
    user_id = os.environ.get('LINE_USER_ID')
    token = os.environ.get('LINE_SECRET_TOKEN')
    payload = {'to': user_id, 'messages': message}
    headers = {'content-type': 'application/json', 'Authorization': f'Bearer {token}'}
    url = 'https://api.line.me/v2/bot/message/push'

    req = urllib.request.Request(url, json.dumps(payload).encode(), headers)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    print("send OK")

def push_line_message_test():
    #===========================
    # LINEへのPUSHメッセージ作成
    #===========================
    print('test')
    message = [
        {'type':'text','text': '【テスト】送信テストです。'}
    ]
    user_id = os.environ.get('LINE_USER_ID')
    token = os.environ.get('LINE_SECRET_TOKEN')
    payload = {'to': user_id, 'messages': message}
    headers = {'content-type': 'application/json', 'Authorization': f'Bearer {token}'}
    url = 'https://api.line.me/v2/bot/message/push'

    req = urllib.request.Request(url, json.dumps(payload).encode(), headers)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    print("send OK")
