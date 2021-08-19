import os
import string
import random

from dotenv import load_dotenv, find_dotenv
from tiktalik.computing import ComputingConnection

# def get_this_file_absolute_path():
#     return os.path.abspath(__file__)

DEFAULT_PREFIX = "def-prefix-"
DEFAULT_INSTANCE_SIZE = "1u"
DEFAULT_DISK_SIZE = 20

def get_api_keys():
    load_dotenv(find_dotenv())
    api_key = os.environ.get("TIKTALIK_API_KEY")
    secret_key = os.environ.get("TIKTALIK_API_SECRET")
    return {
        "api_key": api_key,
        "secret_key": secret_key
        }

def get_connection_object():
    api_keys = get_api_keys()
    conn = ComputingConnection(api_keys["api_key"], api_keys["secret_key"])
    return conn


def get_host_instances():
    conn = get_connection_object()
    return conn.list_instances()

def create_new_alpine_instance(new_instance_name: str):
    conn = get_connection_object()
    target_image = get_alpine_image_uuid_name_dict()
    new_instance_size = get_new_instance_size()
    networks = [ conn.list_networks()[0].uuid ]
    new_instance_disk_size = get_disk_size()
    conn.create_instance(new_instance_name, new_instance_size, target_image["uuid"], networks, disk_size_gb=new_instance_disk_size)

def get_public_network_instance():
    pass

def get_new_instance_size():
    size = DEFAULT_INSTANCE_SIZE
    try:
        load_dotenv(find_dotenv())
        size = str(os.environ["INSTANCE_SIZE"])
    except:
        pass
    return size


def get_new_instance_name(instance_prefix):
    instances = get_host_instances()
    i_names = []
    for i in instances:
        i_names.append(i.hostname)
    return get_new_name_based_on_names_list(i_names, instance_prefix)


def get_instance_prefix():
    load_dotenv(find_dotenv())
    try:
        instance_prefix = os.environ["TASK_PREFIX"]
    except KeyError:
        instance_prefix = DEFAULT_PREFIX
    return instance_prefix

def get_disk_size():
    load_dotenv(find_dotenv())
    try:
        disk_size = int(os.environ["DISK_SIZE_GB"])
    except KeyError:
        disk_size = DEFAULT_DISK_SIZE
    return disk_size

def get_new_name_based_on_names_list(instances_names: list, instance_prefix):
    numes_after_prefix = []
    for name in instances_names:
        splitted_by_prefix = name.split(instance_prefix)
        if len(splitted_by_prefix) > 1:
            splitted_by_dash = splitted_by_prefix[1].split('-')
            try:
                num = splitted_by_dash[0]
                num = int(num)
                numes_after_prefix.append(num)
            except:
                pass
    if len(numes_after_prefix):
        new_num = max(numes_after_prefix) + 1
    else:
        new_num = 0
    return instance_prefix + str(new_num) + '-' + get_random_string_for_hostname()

def get_random_string_for_hostname():
    letters = string.ascii_lowercase
    length = 7
    return ''.join(random.choice(letters) for i in range(length))

def get_alpine_image_uuid_name_dict() -> dict:
    conn = get_connection_object()
    alpine_images = []
    for image in conn.list_images():
        if "Alpine Linux" in image.name:
            alpine_images.append(image)
    return {
        "uuid": alpine_images[-1].uuid,
        "name": alpine_images[-1].name
        }


if __name__ == "__main__":
    pass