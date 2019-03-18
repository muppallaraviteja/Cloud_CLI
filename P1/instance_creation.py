import pymongo
from pymongo import ASCENDING

from P1.connection.mongoConnect import connect_mongo

db = connect_mongo()


def create_instance(image_name, flavor_name, instance_name):
    collection = db['images']

    if collection.find({'_id': image_name}).count() == 0:
        print("[ERROR] The given Image id not available to host the instance.")
        return 0
    image_details = collection.find({'_id': image_name}).next()
    if db['flavors'].find({'_id': flavor_name}).count() == 0:
        print("[ERROR] The given Flavor is not available to host the instance.")
        return 0
    flavor_details = db['flavors'].find({'_id': flavor_name}).next()
    collection = db['hardware']
    free_hardware_list = collection.find({'$and': [
        {"remain_memory": {'$gte': flavor_details['memory']}},
        {"remain_num_disks": {'$gte': flavor_details['num_disks']}},
        {"remain_num_vcpus": {'$gte': flavor_details['num_vcpus']}}
         ]}).sort([('remain_num_disks', pymongo.ASCENDING),
                   ("remain_memory", pymongo.ASCENDING),
                   ("remain_num_vcpus", pymongo.ASCENDING)])

    if free_hardware_list.count() == 0:
        print("[ERROR] No hardware available to host the instance.")
        return 0

    machine = free_hardware_list.next()
    remain_num_disks = machine['remain_num_disks'] - flavor_details['num_disks']
    remain_memory = machine['remain_memory'] - flavor_details['memory']
    remain_num_vcpus = machine['remain_num_vcpus'] - flavor_details['num_vcpus']
    collection.update({"_id": machine['_id']},
                      {'$set': {
                          "remain_num_disks": remain_num_disks,
                          "remain_memory": remain_memory,
                          "remain_num_vcpus": remain_num_vcpus}},
                      False)
    instance = {
        "_id": instance_name,
        "flavor": flavor_name,
        "image": image_name,
        "hardware": machine['_id']
    }

    try:
        db['instance'].insert_one(instance)
    except:
        print('[ERROR] Something went wrong when adding an instance. A unique instance name is required.')
        return 0


    return 1


def delete_instance(instance_name):
    instance_details = db['instance'].find_one({"_id": instance_name})

    if instance_details == None:
        print('[ERROR] No instance exists by that name.')
        return 0

    flavor_details = db['flavors'].find({"_id": instance_details['flavor']}).next()
    machine_name = instance_details['hardware']
    db['hardware'].update({"_id": machine_name},
                      {'$inc': {
                          "remain_num_disks": flavor_details['num_disks'],
                          "remain_memory": flavor_details['memory'],
                          "remain_num_vcpus": flavor_details['num_vcpus']}},
                      False)
    db['instance'].delete_one({'_id': instance_name})

    return 1

def server_list():
    instance_list = db['instance'].find()
    if instance_list.count() == 0:
        print('[ERROR] Instance is not Present.')
        return 0
    print("FORMAT: <name> <image> <flavor> ")
    for instance in instance_list:
        print(instance['_id'], instance['image'], instance['flavor'])

    return 1