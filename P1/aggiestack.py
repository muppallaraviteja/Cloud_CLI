import sys
import os.path
sys.path.append('../')

from P1.instance_creation import create_instance, delete_instance, server_list
from P1 import read_files, admin

# Add argument and explanations to this string


argument_help_string = """ 
usage: main.py [command] [command-args] 

Commands available: 
    config --hardware <filename> (Reads hardware config file)
    config --images <filename> (Reads images config file)
    config --flavors <filename> (Reads flavors config file)

    show hardware (Output all hardware information)
    show images (Output all images information)
    show flavors (Output all flavor information)
    show all (Output everything)

    admin show hardware (Lists information about the hardware)
    admin can_host <machine_name> <flavor> (Tells user if physical server <machine_name> can host flavor <flavor>)
    admin show instances (Output information about each instance currently running)
    admin remove <machine_name> (Remove a machine from its view in the datacenter)
    admin add -mem <MEM> -disk <NUM_DISKS> -vcpus <NUM_VCPUS> -ip <IP> -rack <RACK_NAME> <MACHINE_NAME>

    server create --image <image_name> --flavor <flavor_name> <instance_name> (Create a new instance)
    server delete <instance_name> (Delete an instance named <instance_name>)
"""


# This takes in the command used as well as the success or failure
# and appends it to the status log.
def append_to_log(command, status):
    log = open('aggiestack-log.txt', 'a')

    log.write(command + ' --- ' + status + '\n')


def run_config(args):
    # Ensure there are enough command lind arguments
    if len(args) < 4:
        # Output error
        print('[ERROR] Not enough config arguments provided.')
        print(argument_help_string)
        return 0

    # Store filename and check if valid
    filename = args[3]
    if not os.path.exists(filename):
        print('[ERROR] File provided does not exist.')
        return 0

    file = open(filename, 'r') # Open file

    if args[2] == '--hardware':
        return read_files.read_hardware_file(file)

    elif args[2] == '--images':
        return read_files.read_image_file(file)

    elif args[2] == '--flavors':
        return read_files.read_flavor_file(file)

    else:
        print('[ERROR] Invalid config argument provided')
        print(argument_help_string)
        return 0

    return 1


def run_show(args):
    if len(args) < 3:
        print('[ERROR] Not enough show arguments provided')
        print(argument_help_string)
        return 0

    if args[2] == 'hardware':
        read_files.show_hardware()
    elif args[2] == 'images':
        read_files.show_images()
    elif args[2] == 'flavors':
        read_files.show_flavors()
    elif args[2] == 'all':
        read_files.show_all()
    else:
        print('[ERROR] Invalid show argument provided')
        print(argument_help_string)
        return 0

    return 1


def run_admin(args):
    if len(args) < 4:
        print('[ERROR] Not enough admin arguments provided')
        print(argument_help_string)
        return 0

    if args[2] == 'show' and args[3] == 'hardware':
        return admin.show_hardware()

    # Must be enough args for machine and flavor flags
    elif args[2] == 'can_host' and len(args) > 4:
        machine_name = args[3]
        flavor = args[4]
        return admin.can_host(machine_name, flavor)
    elif args[2] == 'show' and args[3] == 'instances' and len(args) == 4:
        admin.show_instances()
    elif args[2] == 'remove' and len(args) == 4:
        return admin.remove_machine(args[3])
    elif args[2] == 'add' and len(args) == 14:
        print('adding a machine')
        return admin.add_machine(args[3:])
    elif args[2] == 'evacuate' and len(args) == 4:
        return admin.evacuate_rack(args[3])
    else:
        print('[ERROR] Invalid admin argument provided')
        print(argument_help_string)
        return 0


def instance_control(args):
    if args[2] == 'create' and len(args) == 8:
        image_name = args[4]
        flavor_name = args[6]
        instance_name = args[7]
        return create_instance(image_name, flavor_name, instance_name)
    elif args[2] == 'delete' and len(args) == 4:
        return delete_instance(args[3])
    elif args[2] == 'list' and len(args) ==3:
        return server_list()
    else:
        print('[ERROR] Not enough arguments provided for server command.')
        print(argument_help_string)
        return 0


def parse_args():
    num_args = len(sys.argv)
    args = sys.argv
    # If no command line arguments provided, return error
    if num_args < 2:
        print('[ERROR] Not enough arguments provided.')
        print(argument_help_string)
        return 0
    
    # Check for valid command argument
    if args[1] == 'config':
        return run_config(args)

    elif args[1] == 'show':
        return run_show(args)
    
    # Admin mode should be handled once config/show are done
    elif args[1] == 'admin':
        return run_admin(args)
    elif args[1] == 'server':
        return instance_control(args)

    else:
        print('[ERROR] Incorrect command argument entered.')
        print(argument_help_string)
        return 0


def main():
    return_code = parse_args()

    # Return code 0 = fail
    # Return code 1 = success
    if return_code: 
        append_to_log(' '.join(sys.argv), 'SUCCESS')
    else:
        append_to_log(' '.join(sys.argv), 'FAILURE')


if __name__ == '__main__':
    main()
