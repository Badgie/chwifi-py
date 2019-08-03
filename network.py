import netifaces
import re
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
        self.profile_name = profile_name
        self.state = is_profile_active(self.profile_name)
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


def get_mac_address(adapter: str) -> str:
    """
    Returns the MAC address of given adapter
    :param adapter: given adapter to fetch MAC address from
    :return: MAC address of adapter as string
    """
    return netifaces.ifaddresses(adapter)[netifaces.AF_LINK]


def change_mac_address(adapter: str, options: str) -> str:
    try:
        assert is_any_profile_active() is False
    except AssertionError:
        print("[Error] A profile")
    child = pexpect.spawn('sudo macchanger ' + options + ' ' + adapter, timeout=10)
    child.expect(re.escape("[sudo] password for ") + ".*:")

    # Use getpass for securely passing password to spawned process
    child.send(getpass() + "\n")

    try:
        child.expect("New MAC:")
    except pexpect.exceptions.EOF:  # Return empty string if 'macchanger' doesn't return expected output
        print("[Error] Could not change MAC address")
        return ""
    # Search string containing 'New MAC:' for a MAC-address and returning first match. Assumes match given index lookup
    return re.search("([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})", child.readline().decode())[0]


def is_profile_active(profile: str) -> bool:
    """
    Return boolean on whether given profile is active as described by 'netctl'
    :param profile: given profile to test
    :return: boolean on whether the given profile is active
    """
    (output, exit_code) = pexpect.run('netctl list', withexitstatus=1)
    assert exit_code == 0
    assert output is not None
    return any(filter(re.compile(re.escape('* ') + profile + r'\s').match, output.decode().split('\n')))


def is_any_profile_active() -> (bool, str):
    """
    Runs 'netctl list' and checks whether any profile is marked '^\*'.
    :return: tuple consisting of boolean on whether any profile is active, and name of active profile
    """
    (output, exit_code) = pexpect.run('netctl list', withexitstatus=1)
    assert exit_code == 0
    assert output is not None
    # Decode and split output at newlines
    output = output.decode().split('\n')

    # Get list of matches which appear to conform to 'netctl's description of active
    matches = list(filter(re.compile('^' + re.escape("* ") + '.*$').match, output))

    # Any match found?
    ret_bool = any(matches)

    # Extract profile name if any matches are present
    ret_profile_name = re.sub(re.compile(r'\*\s*'), '', matches[0]).strip() if any(matches) else ''

    return ret_bool, ret_profile_name


def update_cache():
    raise NotImplementedError


def decode_output(x):
    """
    Decodes input iterable from bytes to string
    :param x: the iterable to be decoded
    :return: the decoded iterable
    """
    return "".join(map(lambda b: b.decode('utf-8'), x))


ret = is_any_profile_active()

print(ret)
