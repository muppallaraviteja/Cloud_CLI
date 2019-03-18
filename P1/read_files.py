import os.path
import pprint

import pymongo
from pymongo.errors import DuplicateKeyError

from P1.connection.mongoConnect import connect_mongo

subdirectory = "logs/"
hardware_log_filename = 'hardware_log'
image_log_filename = 'image_log'
flavor_log_filename = 'flavor_log'

# TO DO: Validate each entry in each in line to ensure that they are valid
# E.g. cdb = connect_mongo()hecking that the memory and num_vcpus are actually numbers.. etc

db = connect_mongo()


def validate_hardware_input(file):
    """
    Reads the hardware input and validates that the input is in the correct
    format. Returns true if it is valid. False otherwise.

    Inputs:
        - file: This is the file object referencing the input file

    Returns:
        - 1 if input file is valid, 0 otherwise.
    """
    rack_number = int(file.readline())
    for i in range(1, rack_number+1):
        line = file.readline()
        line = line.rstrip('\n').strip(' ').split(' ')
        # If there are missing or too many values on a line.
        if len(line) != 2:
            return 0
    num_machines = file.readline()
    for line in file:
        line = line.rstrip('\n').strip(' ').split(' ')
        # If there are missing or too many values on a line.
        if len(line) != 6:
            return 0
    return 1


def read_hardware_file(file):
    # Ensure that the input hardware file is of correct format.
    if validate_hardware_input(file) == 0:
        print('[ERROR] Invalid hardware file format.')
        return 0
    # Reset file pointer
    file.seek(0)
    collection = db["rack"]
    rack_number = int(file.readline())
    collection.update({"_id": "number"}, {"no_of_racks": rack_number}, True)
    for i in range(1, rack_number + 1):
        line = file.readline()
        line = line.rstrip('\n').split(' ')
        data = {
            "_id": line[0],
            "rack_space": line[1]
        }
        try:
            collection.insert_one(data)
        except DuplicateKeyError:
            print(data.get("_id") + " already Present")
            continue
    collection = db["hardware"]
    num_machines = int(file.readline())
    collection.update({"_id": "number"}, {"no_of_machines": num_machines}, True)
    for line in file:
        line = line.rstrip('\n').split(' ')
        data = {
            "_id": line[0],
            "rackName": line[1],
            "ip_address": line[2],
            "memory": int(line[3]),
            "num_disks": int(line[4]),
            "num_vcpus": int(line[5]),
            "remain_memory": int(line[3]),
            "remain_num_disks": int(line[4]),
            "remain_num_vcpus": int(line[5])
        }
        try:
            collection.insert_one(data)
        except DuplicateKeyError:
            print(data.get("_id") + " already Present")
            continue
    return 1


def validate_image_input(file):
    """
    Validates the image file input.
    """
    num_images = file.readline()
    for line in file:
        line = line.strip('\n').strip(' ').split(' ')
        # Each line in the image file should consist of <image-name> <path-to-image>
        if len(line) != 3:
            return 0
    return 1


def read_image_file(file):
    """ Same concept as the read_hardware_file() function but instead for
    image files.
    """
    if validate_image_input(file) == 0:
        print('[ERROR] Invalid input file format.')
        return 0

    file.seek(0)
    num_images = int(file.readline())
    collection = db["images"]
    collection.update({"_id": "number"}, {"no_of_images": num_images}, True)
    for line in file:
        line = line.rstrip('\n').split(' ')
        data = {
            "_id": line[0],
            'image_size': line[1],
            "image_location": line[2]
        }
        try:
            collection.insert_one(data)
        except DuplicateKeyError:
            print(data.get("_id") + " Image already Present")
            continue
    return 1


def validate_flavor_input(file):
    """
    Validates the flavor input file. Returns 0 if invalid.
    """
    num_flavors = file.readline()
    for line in file:
        line = line.strip('\n').strip(' ').split(' ')

        # Each line in the image file should consist of <image-name> <path-to-image>
        if len(line) != 4:
            return 0

    return 1


def read_flavor_file(file):
    if validate_flavor_input(file) == 0:
        print('[ERROR] Invalid flavor file input.')
        return 0

    file.seek(0)
    num_flavors = int(file.readline())
    # Check if the image log file already exists. If it doesn't, make a new one.
    collection = db["flavors"]
    collection.update({"_id": "number"}, {"no_of_flavors": num_flavors}, True)
    for line in file:
        line = line.strip('\n').split(' ')
        data = {
            "_id": line[0],
            "memory": int(line[1]),
            "num_disks": int(line[2]),
            "num_vcpus": int(line[3])
        }
        try:

            collection.insert_one(data)
        except DuplicateKeyError:
            print(data.get("_id") + " Flavor already Present")
            continue
    return 1


# Outputs all of the hardware information from the general log file
def show_hardware():
    collection = db["hardware"]
    hardware_list = collection.find({'_id': {'$ne': "number"}})
    count = collection.find({'_id': {'$ne': "number"}}).count()
    if count == 0:
        print('[ERROR] Hardware log does not exist.')
        return 0

    print("Hardware available:")
    print("FORMAT: <rack-name> <name> <ip> <mem> <num-disks> <num-vpus>")
    for hardware in hardware_list:
        print(hardware["rackName"], hardware["_id"], hardware["ip_address"], \
              hardware["memory"], hardware["num_disks"], hardware["num_vcpus"])

def show_images():
    collection = db["images"]
    image_list = collection.find({'_id': {'$ne': "number"}})
    count = collection.find({'_id': {'$ne': "number"}}).count()
    if count == 0:
        print('[ERROR] Image log does not exist.')
        return 0
    print("Images available:")
    for image in image_list:
        print(image["_id"], image["image_size"], image["image_location"])


def show_flavors():
    collection = db["flavors"]
    flavors_list = collection.find({'_id': {'$ne': "number"}})
    count = collection.find({'_id': {'$ne': "number"}}).count()
    if count == 0:
        print('[ERROR] Flavor log does not exist.')
        return 0
    print("Flavors available:")
    print("FORMAT: <name> <RAM in GB> <num-disks> <num-vcpus>")
    for flavor in flavors_list:
        print(flavor["_id"], flavor["memory"], flavor["num_disks"], flavor["num_vcpus"])


def show_all():
    print("_______________________________________________________________")
    print("---------------------------------------------------------------")
    show_hardware()
    print("---------------------------------------------------------------")
    show_images()
    print("---------------------------------------------------------------")
    show_flavors()
    print("_______________________________________________________________")
    print("---------------------------------------------------------------")
