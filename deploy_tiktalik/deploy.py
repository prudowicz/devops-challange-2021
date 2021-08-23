import os
import sys
import time

from dotenv import load_dotenv, find_dotenv
import requests

from host_provider import create_new_alpine_instance, get_new_instance_name,\
    wait_for_instance_running, get_instance_prefix
from ssh_handler import AlpineSSHHandler

DEFAULT_REPO_TO_DEPLOY = "https://github.com/prudowicz/devops-challange-2021"

def get_repo_to_deploy():
    repo_to_deploy = DEFAULT_REPO_TO_DEPLOY
    # try:
    #     load_dotenv(find_dotenv())
    #     repo_to_deploy = os.environ["REPO_TO_DEPLOY"]
    # except KeyError:
    #     pass
    return repo_to_deploy


def print_response_outs(response):
    for line in response.stdout:
        print(line)
    for line in response.stderr:
        print(line)


def test_get_endpoints(hostname: str, port: int, endpoints: list):
    url = "http://" + hostname + ":" + str(port)
    for e in endpoints:
        full_address = url + e
        r = requests.get(full_address)
        print(full_address + " " + str(r.status_code))
        assert r.status_code == 200
    print("OK")


if __name__ == "__main__":
    instance_prefix = get_instance_prefix()
    new_instance_name = get_new_instance_name(instance_prefix)
    instance_result = create_new_alpine_instance(new_instance_name)
    print("Creating instance uuid: " + str(instance_result["uuid"]) + \
        " with ip address: " + instance_result["ip"])
    wait_for_instance_running(instance_result["uuid"])
    alpine_ssh_handler = AlpineSSHHandler(
        ip_address=instance_result["ip"],
        password=instance_result["default_password"]
    )
    alpine_ssh_handler.connect()
    if alpine_ssh_handler.is_first_login():
        alpine_ssh_handler.handle_first_login_password_change()
    print("Connected with ssh to " + str(alpine_ssh_handler.ip_address) + ":" + str(alpine_ssh_handler.port))
    alpine_ssh_handler.install_deploy_dependecies()
    repo_url = get_repo_to_deploy()
    try:
        alpine_ssh_handler.clone_repo_from_url(repo_url)
    except Exception as e:
        print(str(e))
        print("Please ensure that repo " + repo_url + " is a public one")
        sys.exit(1)
    repo_dir = repo_url.split("/")[-1]
    if repo_dir[-1] != "/":
        repo_dir += "/"
    response = alpine_ssh_handler.execute_command("cd " + repo_dir + "; docker-compose build")
    if response.exit_status != 0:
        print_response_outs(response)
        raise Exception("Error exit stats="+ str(response.exit_status) + " while building repo from " + repo_url)
    response = alpine_ssh_handler.execute_command("cd " + repo_dir + "; docker-compose up -d")
    if response.exit_status != 0:
        print_response_outs(response)
        raise Exception("Error exit stats="+ str(response.exit_status) + " while starting repo from " + repo_url)
    print("app started at ip address: " + instance_result["ip"])
    alpine_ssh_handler.close()
    endpoints = ["/", "/healthz", "/ready"]
    try:
        test_get_endpoints(
            hostname=instance_result["ip"],
            port=5001,
            endpoints=endpoints
        )
    except Exception as e:
        time.sleep(10)
        test_get_endpoints(
            hostname=instance_result["ip"],
            port=5001,
            endpoints=endpoints
        )


