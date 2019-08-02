import netifaces
from getpass import getpass

import pexpect


class Profile:
    state = bool
    profile_name = ""
    work_profile = bool
    adapter = ""
    old_mac = ""
    new_mac = ""

    def __init__(self, profile_name):
        self.state = False
        self.profile_name = profile_name
        self.old_mac = get_mac_address(self.adapter)
        # TODO: how to handle setting work profiles? Config?

    def connect(self, change_mac):
        if self.state:
            print("Profile is already active, restarting it now")
            self.restart()
            return

        if change_mac:
            # change mac_address
            pexpect.spawn('sudo macchanger' + self.adapter)

        pexpect.spawn('netctl', ['start', self.profile_name])
        self.state = True

    def restart(self):
        pexpect.spawn('netctl', ['restart', self.profile_name])

    def disconnect(self):
        pexpect.spawn('netctl', ['stop', self.profile_name])


def get_mac_address(adapter):
    return netifaces.ifaddresses(adapter)[netifaces.AF_LINK]


def change_mac_address(adapter, options):
    child = pexpect.spawn('sudo macchanger ' + options + ' ' + adapter, timeout=10)
    child.expect("\[sudo\] password for ")

    # Use getpass for securely passing password to spawned process
    child.send(getpass() + "\n")
    try:
        child.expect("New MAC:")
        print(child.readline())
    except pexpect.exceptions.EOF as e:
        print("[Error] Could not change MAC address")
        return

    return decode_output(child.readlines())


def is_profile_active(profile):
    raise NotImplementedError


def update_cache():
    raise NotImplementedError


def decode_output(x):
    """
    Decodes input iterable from bytes to string
    :param x: the iterable to be decoded
    :return: the decoded iterable
    """
    return "".join(map(lambda b: b.decode('utf-8'), x))


output = change_mac_address("wlp3s0", "-e")

print(output)

