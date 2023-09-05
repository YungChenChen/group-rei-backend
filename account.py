from flask import Blueprint, request, jsonify
import hashlib, os

from datetime import datetime

from dbConnection import dbConnect

account = Blueprint('account',  __name__)

@account.route('/login', methods = ['POST'])
def login():

    accountDb = dbConnect('account')
    loginDb = dbConnect('login_record')

    uid = request.get_json()['uid'].lower()
    password = hashlib.md5(request.get_json()['password'].encode('utf-8')).hexdigest()

    query = {"uid": uid}
    record = accountDb.find_one(query, {'_id': 0})

    print({'uid': uid, 'password': password})
    print(record)

    if record['password'] == password:
        print('uid login')
        token = hashlib.sha1(os.urandom(24)).hexdigest()

        logoutAll(uid)
        loginDb.insert_one({
            'token_hash': hashlib.md5(token.encode('utf-8')).hexdigest(),
            'uid': uid,
            'login_date': datetime.today().replace(microsecond = 0),
            'is_login': True
        })

        data = {
            'token': token,
            'name': record['name'],
            'birthday': record['birthday'],
            'phone': record['phone'],
            'memberLevel': record['member_level'],
            'email': record['email']
        }

        return jsonify(data)

    else:
        return jsonify(
            {
                "statusCode": 400,
                "failedMsg": "登入失敗"
            }
        )


@account.route('/logout', methods = ['POST'])
def logout():
    expiresDays = 30

    loginDb = dbConnect('login_record')

    uid = request.get_json()['uid'].lower()
    tokenHash = hashlib.md5(request.get_json()['token'].encode('utf-8')).hexdigest()

    query = {
        'uid': uid,
        'token_hash': tokenHash,
    }

    record = loginDb.find_one(query, {"_id": 0})

    if record is not None:
        loginDays = (datetime.today()-record['login_date']).days

        if loginDays > expiresDays:
            data = {
                'state': 'token expires',
                'stateMessage': '此登入過期',
                'date': record['login_date']
            }
            return jsonify(data)

        if record['is_login'] == True:
            logoutAll(uid)

            data = {
                'state': 'success',
                'stateMessage': '登出成功'
            }
        else:
            data = {
                'state': 'token invalid',
                'stateMessage': '此登入狀態無效'
            }
    else:
        data = {
                'state': 'none login',
                'stateMessage': '無此登入記錄'
            }

    return jsonify(data)

@account.route('/signup', methods = ['POST'])
def signup():
    uid =  request.get_json()['uid'].lower()
    name = request.get_json()['name']
    email = request.get_json()['email']
    phone = request.get_json()['phone']
    birthday = datetime.strptime(
        request.get_json()['birthday'], '%Y-%m-%d'
    )
    password = hashlib.md5(request.get_json()['password'].encode('utf-8')).hexdigest()

    insertData = {
        'uid': uid,
        'name': name,
        'password': password,
        'email': email,
        'birthday': birthday,
        'phone': phone,
        'member_level': 0
    }

    try:
        accountDb = dbConnect('account')

        print(insertData)
        accountDb.insert_one(insertData)
        data = {
            'state': 'success',
            'stateMessage': '註冊成功'
        }
    except:
        data = {
            'state': 'failed',
            'stateMessage': '註冊失敗'
        }

    return jsonify(data)

@account.route('/check-uid', methods = ['GET'])
def checkUid():
    uid = request.args['uid'].lower()

    accountDb = dbConnect('account')

    record = accountDb.find_one({'uid': uid})

    if record is not None:
        data = {
            'isUsed': True
        }
    else:
        data = {
            'isUsed': False
        }
    
    return jsonify(data)


# 登出所有裝置
def logoutAll(uid):
    loginDb = dbConnect('login_record')

    allLoginData = loginDb.update_many({'uid': uid}, {'$set': {'is_login': False}})
    print(uid, allLoginData.modified_count, "documents of login_record updated")