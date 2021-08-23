import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ssh_handler import AlpineSSHHandler
from test_host_provider import TEST_PREFIX
from host_provider import create_new_alpine_instance, get_new_instance_name,\
    wait_for_instance_running, remove_instance


@pytest.fixture(scope='session', autouse=True)
def ssh_handler():
    test_instance_name = get_new_instance_name(TEST_PREFIX)
    instance_result = create_new_alpine_instance(test_instance_name)
    print("Creating instance uuid: " + str(instance_result["uuid"]))
    wait_for_instance_running(instance_result["uuid"])
    handler = AlpineSSHHandler(
        ip_address=instance_result["ip"],
        password=instance_result["default_password"]
    )
    handler.connect()
    if handler.is_first_login():
        handler.handle_first_login_password_change()
    print("Connected with ssh to " + str(instance_result["ip"]) + ":" + str(handler.port))
    yield handler
    handler.close()
    remove_instance(instance_result["uuid"])
    print("Removed instance with uuid: " + instance_result["uuid"])


# @pytest.fixture(scope='session', autouse=True)
# def ssh_handler():
#     handler = AlpineSSHHandler(
#         ip_address="37.233.103.18",
#         password="c47b75d9191"
#     )
#     handler.connect()
#     if handler.is_first_login():
#         handler.handle_first_login_password_change()
#     print("Connected with ssh to " + str(handler.ip_address) + ":" + str(handler.port))
#     yield handler
#     handler.close()

def test_list_remote_homedir(ssh_handler):
    response = ssh_handler.execute_command("ls -a")
    counted = 0
    for line in response.stdout:
        line = line.strip()
        if line == "." or line == "..":
            counted += 1
    assert counted == 2

def test_check_is_package_installed(ssh_handler):
    assert ssh_handler.check_is_package_installed("linux-firmware")
    assert not ssh_handler.check_is_package_installed("this-is-not-a-proper-package-name")

def test_exit_status(ssh_handler):
    response = ssh_handler.execute_command("true")
    assert response.exit_status == 0
    response = ssh_handler.execute_command("false")
    assert response.exit_status != 0


def test_clone_repo(ssh_handler):
    ssh_handler.install_deploy_dependecies()
    repo_url = "https://github.com/prudowicz/hltv-veto-simulator"
    ssh_handler.clone_repo_from_url(repo_url)
    repo_dir = repo_url.split("/")[-1]
    print(repo_dir)
    response = ssh_handler.execute_command("cd " + repo_dir)
    assert response