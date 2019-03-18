from instance_creation import delete_instance
import pymongo
from pymongo import ASCENDING
from P1.connection.mongoConnect import connect_mongo

db = connect_mongo()


def show_hardware():
    # Hardware log does not exist
    collection = db['hardware']
    if collection.find().count() == 0:
        print('[ERROR] No hardware Document found.')
        return 0

    hardware_list = collection.find({'_id': {'$ne': "number"}})
    for machine in hardware_list:
        # print(machine)
        name = machine['_id']
        remaining_mem = machine.get('remain_memory')
        remaining_disks = machine.get('remain_num_disks')
        remaining_vcpus = machine.get('remain_num_vcpus')

        print('Server: {0} --- Memory: {1} - Disks: {2} - Vcpus: {3}' \
              .format(name, remaining_mem, remaining_disks, remaining_vcpus))
    return 1


def can_host(machine_name, flavor_name):
    collection_hardware = db['hardware']
    if collection_hardware.find().count() == 0:
        print('[ERROR] No hardware Document found.')
        return 0

    collection_flavor = db['flavors']
    if collection_flavor.find().count() == 0:
        print('[ERROR] No flavor Document found.')
        return 0

    hdwr_list = collection_hardware.find({'_id': {'$ne': "number"}})
    flvr_list = collection_flavor.find({'_id': {'$ne': "number"}})

    remaining_mem = 0
    remaining_disks = 0
    remaining_vcpus = 0
    for machine in hdwr_list:
        if machine['_id'] == machine_name:
            remaining_mem = float(machine.get('memory'))
            remaining_disks = float(machine.get('num_disks'))
            remaining_vcpus = float(machine.get('num_vcpus'))
            break

    if remaining_mem == 0:
        print('[ERROR] No machine found.')
        return 0

    flavor_mem = 0
    flavor_disks = 0
    flavor_vcpus = 0
    for flavor in flvr_list:
        if flavor['_id'] == flavor_name:
            flavor_mem = float(flavor.get('memory'))
            flavor_disks = float(flavor.get('num_disks'))
            flavor_vcpus = float(flavor.get('num_vcpus'))
            break

    if flavor_mem == 0:
        print('[ERROR] Flavor not found.')
        return 0

    if remaining_mem - flavor_mem >= 0 and remaining_disks - flavor_disks >= 0 \
            and remaining_vcpus - flavor_vcpus >= 0:
        print('YES')
        return 1
    else:
        print('NO')
        return 1

    return 1


def show_instances():
    instance_list = db['instance'].find()
    if instance_list.count() == 0:
        print('[ERROR] No instances are currently running.')
        return 0
    print("FORMAT: <name> <image> <flavor> <hardware-name>")
    for instance in instance_list:
        print(instance['_id'], instance['image'], instance['flavor'], instance['hardware'])

def _process_add_machine_args(args):
    """
    Process the arguments provided when added a machine.
    
    Returns:
        - Returns machine info so it can be added to the machine list
    """
    machine = {}

    for i in range(0, len(args) - 1, 2):
        if args[i] == '-mem':
            mem_num = args[i+1]
        elif args[i] == '-disk':
            disk_num = args[i+1]
        elif args[i] == '-vcpus':
            vcpu_num = args[i+1]
        elif args[i] == '-ip':
            ip = args[i+1]
        elif args[i] == '-rack':
            rack_name = args[i+1]
            machine_name = args[i+2] # Assuming machine name is always after rack name
        else:
            print('[ERROR] Invalid argument provided.')
            return None

    # Return machine dictionary so it can be added directly to collection
    return {'_id': machine_name, 'rackName': rack_name, 'ip_address': ip, \
            'memory': mem_num, 'num_disks': disk_num, 'num_vcpus': vcpu_num, \
            'remain_memory': mem_num, 'remain_num_disks': disk_num, \
            'remain_num_vcpus': vcpu_num}

def add_machine(args):
    """ 
    This function will add a machine to the system. 
    
    It first processes all the arguments to generate the machine object. 
    Next, it will check that the machine doesn't already exist in the server
    with the same name.

    It will then check if the rack provided in the args is a rack that is listed 
    in the rack list.

    After all of these checks, the machine will be added to the hardware collection
    in our database so that it can be displayed.
    """

    machine_info = _process_add_machine_args(args)

    if machine_info == None:
        return 0

    hardware_collection = db['hardware']

    # Query hardware collection to determine if the machine already exists
    machine_list = hardware_collection.find({'_id': machine_info['_id']})

    # If the count is not 0, a machine exists so throw an error
    if machine_list.count() != 0:
        print('[ERROR] A machine already exists by that name.')
        return 0

    # Check if the rack provided actually exists in the rack collection
    rack_collection = db['rack']
    rack_list = rack_collection.find({'_id': machine_info['rackName']})

    if rack_list.count() == 0:
        print('[ERROR] No rack exists by that name.')
        return 0

    try:
        hardware_collection.insert_one(machine_info)
    except:
        print('[ERROR] An error was encountered when trying to add the machine.')
        return 0

    return 1

def remove_machine(machine_name):
    hardware_collection  = db['hardware']
    
    # Query the hardware db to ensure that the machine exists
    machine_list = hardware_collection.find({'_id': machine_name})

    # If no machine is found, throw an error and exit
    if machine_list.count() == 0:
        print('[ERROR] Machine not found.')
        return 0

    machine = machine_list[0]

    # Query instance collection to find any instance that is running on the machine
    instance_list = db['instance'].find({'hardware': machine_name})

    # If an instance is found, then we can't remove the machine
    if instance_list.count() != 0:
        print('[ERROR] Unable to remove machine. An instance is currently running on it.')
        return 0

    # If the machine exists and no instances are running on the machine, delete it
    try:
        hardware_collection.delete_one({'_id': machine_name})
    except:
        print('[ERROR] Something went wrong with the deletion...')
        return 0

    return 1

def evacuate_rack(rack_name):
    """
    Evacuate a rack with the given rack name.

    Input:
        rack_name - name of rack to be evacuated

    Output:
        proper return code 1 or 0 for success or failure
    """
    ### Determine if the rack even exists
    rack_collection = db["rack"]
    racks = rack_collection.find({'_id': rack_name})

    # Either we found no racks with the provided name, OR 
    # There were multiple racks with the name found (This should never be the case)
    # Should throw an error either way.
    if racks.count() != 1:
        print('[ERROR] Either no rack was found by that name or multiple racks were found..')
        return 0

    ### Find all hardware on the specified rack 
    hardware_collection = db['hardware']
    instance_collection = db['instance']
    hardware_on_rack = hardware_collection.find({'rackName': rack_name})

    # Iterate through the hardware on a specific rack, determine if an instance
    # is running on that hardware. We then need to relocate that instance to another
    # rack.
    instances_to_be_relocated = []
    for hdwr in hardware_on_rack:
        instances = instance_collection.find({'hardware': hdwr['_id']})

        # If no instances running on the specific hardware, just continue to next hdwr
        if instances.count() == 0:
            continue
        else: # Loop through all instances on a machine 
            for i in instances:
                instances_to_be_relocated.append(i)

    # If there are no instances that need to be relocated, just exit cleanly.
    if len(instances_to_be_relocated) == 0:
        print('[ERROR] No instances need to be relocated. Exiting.')
        return 1

    image_collection = db['images']
    flavor_collection = db['flavors']

    # Iterate through each instance to be relocated and attempt to 
    # relocate to another rack. If no server is capable of hosting the instance,
    # we will just remove it entirely. (SHOULD WE DO THIS?)
    for instance in instances_to_be_relocated:
        flavor_details = flavor_collection.find({'_id': instance['flavor']}).next()
        image_details = image_collection.find({'_id': instance['image']}).next()

        # First we delete the instance currently on the machine
        delete_instance(instance['_id']) # Imported from instance_creation.py

        # Next, we must find a suitable machine on another rack 
        # This query finds all machines with enough remaining
        free_hardware_list = hardware_collection.find({'$and': [
        {"remain_memory": {'$gte': flavor_details['memory']}},
        {"remain_num_disks": {'$gte': flavor_details['num_disks']}},
        {"remain_num_vcpus": {'$gte': flavor_details['num_vcpus']}},
        {"rackName": {'$ne': rack_name}}
         ]}).sort([('remain_num_disks', pymongo.ASCENDING),
                   ("remain_memory", pymongo.ASCENDING),
                   ("remain_num_vcpus", pymongo.ASCENDING)])

        # If no hardware exists that can handle the instance, the instance
        # will just be deleted and not added anywhere else.
        if free_hardware_list.count() == 0:
            continue

        # Pull the first machine returned from the above query
        machine = free_hardware_list.next()

        # Compute remaining memory for the new machine when instance is added
        remain_num_disks = machine['remain_num_disks'] - flavor_details['num_disks']
        remain_memory = machine['remain_memory'] - flavor_details['memory']
        remain_num_vcpus = machine['remain_num_vcpus'] - flavor_details['num_vcpus']

        # Update hardware collection
        hardware_collection.update({"_id": machine['_id']},
                      {'$set': {
                          "remain_num_disks": remain_num_disks,
                          "remain_memory": remain_memory,
                          "remain_num_vcpus": remain_num_vcpus}},
                      False)

        # Construct new instance reflecting new hardware name
        instance = {
            "_id": instance['_id'],
            "flavor": flavor_details['_id'],
            "image": image_details['_id'],
            "hardware": machine['_id']
            }

        # Add it to the instance DB
        db['instance'].insert_one(instance)

    return 1