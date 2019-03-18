import json
import os.path
import pprint

import pymongo
from pymongo.errors import DuplicateKeyError

from P0.connection.mongoConnect import connect_mongo

subdirectory = "logs/"
hardware_log_filename = 'hardware_log'
image_log_filename = 'image_log'
flavor_log_filename = 'flavor_log'

# TO DO: Validate each entry in each in line to ensure that they are valid
# E.g. checking that the memory and num_vcpus are actually numbers.. etc

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
    num_machines = file.readline()
    for line in file:
        line = line.rstrip('\n').strip(' ').split(' ')

        # If there are missing or too many values on a line.
        if len(line) != 5:
            return 0
    return 1


def read_hardware_file(file):
    # Ensure that the input hardware file is of correct format.
    if validate_hardware_input(file) == 0:
        print('[ERROR] Invalid hardware file format.')
        return 0
    # Reset file pointer
    file.seek(0)
    num_machines = int(file.readline())
    collection = db["hardware"]
    collection.update({"_id": "number"}, {"no_Of_machines": num_machines}, True)

    for line in file:
        line = line.rstrip('\n').split(' ')
        data = {
            "_id": line[0],
            "Ip_Address": line[1],
            "Memory": int(line[2]),
            "Num_Disks": int(line[3]),
            "Num_Vcpus": int(line[4])
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
        if len(line) != 2:
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
    collection.update({"_id": "number"}, {"no_Of_images": num_images}, True)
    for line in file:
        line = line.rstrip('\n').split(' ')
        data = {
            "_id": line[0],
            "Image Location": line[1],
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
    collection.update({"_id": "number"}, {"no_Of_flavors": num_flavors}, True)
    for line in file:
        line = line.rstrip('\n').split(' ')
        data = {
            "_id": line[0],
            "Memory": int(line[1]),
            "Num_Disks": int(line[2]),
            "Num_Vcpus": int(line[3])
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
    print("FORMAT: <name> <ip> <mem> <num-disks> <num-vpus>")
    for hardware in hardware_list:
        line = ""
        for key in hardware:
            line = line + str(hardware[key])+" "
        print(line.strip(" "))


def show_images():
    collection = db["images"]
    image_list = collection.find({'_id': {'$ne': "number"}})
    count = collection.find({'_id': {'$ne': "number"}}).count()
    if count == 0:
        print('[ERROR] Image log does not exist.')
        return 0
    print("Images available:")
    for image in image_list:
        # We have to strip the newline char since newlines appear in the input files
        line = ""
        for key in image:
            line = line + str(image[key]) + " "
        print(line.strip(" "))


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
        line = ""
        for key in flavor:
            line = line + str(flavor[key])+" "
        print(line.strip(" "))


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
