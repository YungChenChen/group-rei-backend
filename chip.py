from bson import ObjectId
from flask import Blueprint, request, jsonify
import hashlib, os
from dbConnection import dbConnect

chip = Blueprint('chip',  __name__)


@chip.route('/info', methods = ['GET'])
def info():
    chipId = request.get_json()['chipId']

    chipDb = dbConnect('chip')
    
    record = chipDb.find_one({'chip_id' : chipId},{'_id': 0 ,'item_oid':0})
    
    print(record)
    
    return jsonify(record)
    
@chip.route('upgrade', methods = ['POST'])
def upgrade():
    token = request.get_json()['token']
    objItemOid = request.get_json()['objItemOid']
    typeId = request.get_json()['typeId']
    u = request.get_json()['u']
    mu = request.get_json()['mu']
    
    bagDb = dbConnect('bag')
    obj_itemDb = dbConnect('obj_item')
    chipDb = dbConnect('chip')

    r = obj_itemDb.find_one({"_id":ObjectId(objItemOid)})

    print(r)
    
    if u[0]['UType'] == 'i00010':
        exp = u[0]['UNum']*100
    elif u[0]['UType'] == 'i00011':
        exp = u[0]['UNum']*1000
    else:
        exp = u[0]['UNum']*10000
    print(exp)

    obj_itemDb.update_one({"_id":ObjectId(objItemOid)},{'$inc':{'exp': exp}})
    cost = exp*5
    bagDb.update_one({"obj_items":ObjectId(objItemOid),'items.item_id':'i0001'},{'$inc':{'items.1.amount': -cost}})
    afterexp = obj_itemDb.find_one({"_id":ObjectId(objItemOid)},{"exp":1,"_id":0})
    cost_mu = bagDb.find_one({"obj_items":ObjectId(objItemOid),'items.item_id':'i0001'},{'items.amount':1, '_id':0})
    print(cost_mu)
    data = [cost_mu,afterexp]
    print(data)
    return jsonify(data)

    


    
    
    




