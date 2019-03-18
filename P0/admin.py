import read_files
import os


def show_hardware():
    # Hardware log does not exist
    if not os.path.exists(read_files.subdirectory + read_files.hardware_log_filename):
        print('[ERROR] No hardware log found.')
        return 0
    else:
        log = open(read_files.subdirectory + read_files.hardware_log_filename, 'r')

        for machine in log:
            machine = machine.strip('\n').split(' ')
            name = machine[0]
            remaining_mem = machine[5]
            remaining_disks = machine[6]
            remaining_vcpus = machine[7]

            print('Server: {0} --- Memory: {1} - Disks: {2} - Vcpus: {3}' \
                  .format(name, remaining_mem, remaining_disks, remaining_vcpus))
    return 1


def can_host(machine_name, flavor_name):
    if not os.path.exists(read_files.subdirectory + read_files.hardware_log_filename):
        print('[ERROR] No hardware log found.')
        return 0

    if not os.path.exists(read_files.subdirectory + read_files.flavor_log_filename):
        print('[ERROR] No flavor log found.')
        return 0

    hdwr_log = open(read_files.subdirectory + read_files.hardware_log_filename, 'r')
    flvr_log = open(read_files.subdirectory + read_files.flavor_log_filename, 'r')

    remaining_mem = 0
    remaining_disks = 0
    remaining_vcpus = 0
    for machine in hdwr_log:
        machine = machine.strip('\n').split(' ')

        if machine[0] == machine_name:
            remaining_mem = float(machine[5])
            remaining_disks = float(machine[6])
            remaining_vcpus = float(machine[7])
            break

    if remaining_mem == 0:
        print('[ERROR] No machine found.')
        return 0

    flavor_mem = 0
    flavor_disks = 0
    flavor_vcpus = 0
    for flavor in flvr_log:
        flavor = flavor.strip('\n').split(' ')

        if flavor[0] == flavor_name:
            flavor_mem = float(flavor[1])
            flavor_disks = float(flavor[2])
            flavor_vcpus = float(flavor[3])
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
