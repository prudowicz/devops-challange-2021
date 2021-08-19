import sys
import os
from tiktalik.computing.objects import Instance

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from host_provider import *

TEST_PREFIX = "test-pref-"

def test_get_api_keys():
    api_keys = get_api_keys()
    if not isinstance(api_keys, dict):
        raise_failure_getting_keys()
    dict_keys = list(api_keys.keys())
    if "api_key" not in dict_keys or "secret_key" not in dict_keys:
        raise_failure_getting_keys()
    if not isinstance(api_keys["api_key"], str):
        raise_failure_getting_keys()
    if not isinstance(api_keys["secret_key"], str):
        raise_failure_getting_keys()

def raise_failure_getting_keys():
    raise Exception("api keys do not pass format. please check if you set .env file")

def test_get_instances():
    instances = get_host_instances()
    for i in instances:
        if not isinstance(i, Instance):
            raise Exception("host instance object is diffrent type than tiktalik Instance: " + str(type(i)))
    if not isinstance(instances, list):
        raise Exception("cannot get host instances from host provider")

def test_get_new_instance_name():
    fake_instances_list = []
    for i in range(0, 3):
        s = TEST_PREFIX + str(i) + "-" + get_random_string_for_hostname()
        fake_instances_list.append(s)
    new_name = get_new_name_based_on_names_list(fake_instances_list, TEST_PREFIX)
    assert TEST_PREFIX + "3-" in new_name

def test_get_alpine_image():
    img = get_alpine_image_uuid_name_dict()
    assert "alpine linux" in img["name"].lower()
    assert len(img["uuid"]) > 15

def test_create_new_alpine_instance():
    test_instance_name = get_new_instance_name(TEST_PREFIX)
    create_new_alpine_instance(test_instance_name)
    print("Created instance with hostname: " + str(test_instance_name))