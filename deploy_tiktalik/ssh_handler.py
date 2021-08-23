import paramiko
import time

from host_provider import DEFAULT_TRY_TO_REMOVE_ATTEMPTS, DEFAULT_PAUSE_BEFORE_REMOVE_SECONDS

TO_APPEND_TO_DEFAULT_PASSWORD = "1"


class SSHHandler(object):
    def __init__(self, ip_address:str, password: str, username: str = "root", port: int = 22):
        self.ip_address = ip_address
        self.password = password
        self.username = username
        self.port = port
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        self.__shell_obj = None
    
    def connect(self):
        for i in range(0, DEFAULT_TRY_TO_REMOVE_ATTEMPTS):
            try:
                self._client.connect(self.ip_address, 
                    port=self.port, 
                    username=self.username, 
                    password=self.password,
                    timeout=30
                )
                break
            except paramiko.ssh_exception.NoValidConnectionsError:
                print("Connection error, trying again in " + str(DEFAULT_PAUSE_BEFORE_REMOVE_SECONDS) + " seconds...")
                time.sleep(DEFAULT_PAUSE_BEFORE_REMOVE_SECONDS)

    def close(self):
        self._client.close()

    def is_first_login(self):
        self._shell_obj = self._client.invoke_shell()
        out = self._get_last_line_from__shell_object()
        print(out)
        if "New password:" in out:
            return True

    def _get_last_line_from__shell_object(self):
        out = ""
        time.sleep(1)
        while self._shell_obj.recv_ready():
            out += self._shell_obj.recv(2048).decode("utf-8")
        return out.split('\n')[-1]

    def handle_first_login_password_change(self):
        new_password = self.password + TO_APPEND_TO_DEFAULT_PASSWORD
        self._shell_obj.send(new_password+'\n')
        out = self._get_last_line_from__shell_object()
        print(out)
        if "Retype new password" in out:
            self._shell_obj.send(new_password+'\n')
        self.close()
        self.password = new_password
        self.connect()

    def execute_command(self, command: str) -> dict:
        # chan = self._client.get_transport().open_session()
        stdin, stdout, stderr = self._client.exec_command(command)
        to_ret = {}
        to_ret["stdin"] = stdin
        to_ret["stdout"] = stdout
        to_ret["stderr"] = stderr
        to_ret["exit_status"] = stdout.channel.recv_exit_status() + stdout.channel.recv_exit_status()
        return to_ret


    def install_deploy_dependecies(self):
        dependencies = "docker openrc docker-compose git"
        self.install_packages(dependencies)
        for dep in dependencies.split():
            if not self.check_is_package_installed(dep):
                raise Exception(dep + " is not installed on remote " + self.ip_address)
        exits = 0
        exits += self.execute_command("rc-update add docker boot")["exit_status"]
        exits += self.execute_command("service docker start")["exit_status"]
        if exits != 0:
            raise Exception("There was an error while setting docker dependencies. Sum of exit codes is: " + str(exits))



    def install_packages(self, package_names: str):
        response = self.execute_command("apk add --update " + package_names)
        exit_status = response["exit_status"]
        print("exit status of installing " + package_names + " is " + str(exit_status))
        assert exit_status == 0



    def check_is_package_installed(self, package_name: str) -> bool:
        response = self.execute_command("apk info | grep " + package_name)
        for line in response["stdout"]:
            line = line.strip()
            if package_name == line:
                return True
        return False