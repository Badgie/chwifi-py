import netifaces
import re
from time import sleep

import requests
from getpass import getpass
import pexpect


# TODO; develop nicer method for executing sudo-commands;
#  1. preloading sudo for all spawned processes,
#  2. saving sudo-password during runtime

class Profile:
    state = bool
    profile_name = ""
    work_profile = bool
    adapter = ""
    current_mac = ""
    new_mac = ""

    def __init__(self, profile_name):
        self.profile_name = profile_name
        self.state = is_profile_active(self.profile_name)
        self.current_mac = get_mac_address(self.adapter)
        # TODO: how to handle setting work profiles? Config?

    def connect(self, change_mac):
        if self.state:
            print("Profile is already active, restarting it now.")
            self.restart()
            return

        # If any profile is active, stop-all before continuing
        active_profile = is_any_profile_active()
        if active_profile[0]:
            print(f"Profile: {active_profile[1]} is currently active. Stopping it before continuing")
            stop_all_profiles()

        if change_mac:  # todo; handle enabling of macchanger and options through config?
            change_mac_address(self.adapter, '-e')

        pexpect.run('netctl', ['start', self.profile_name])
        self.state = True

        # todo; wait for connection

        # todo; update cache

    def restart(self):
        pexpect.run(['sudo', 'netctl', 'restart', self.profile_name])

    def disconnect(self):
        pexpect.run(['sudo', 'netctl', 'stop', self.profile_name])


def wait_for_connection(address):
    """
    Continuously prompts the given address until an 'ok' status has been received.
    :param address: the address to wait for connection to
    :return:
    """

    def get_status(url) -> requests.Response.ok:
        """
        Returns the status check 'ok' from given url. 'ok' is defined by Requests as a status code below 400.
        :param url: the address to access
        :return: the boolean result of the 'ok'
        """
        return requests.get(url).ok

    try:
        status = get_status(address)
        while not status:
            sleep(0.25)
            status = get_status(address)
    except requests.exceptions.ConnectionError:
        print(
            f"[Error] Looking up: {address} caused an exception. Please check if address is valid and prefixed by the "
            f"correct protocol. (http/https)://url.tld")


def stop_all_profiles() -> None:
    """
    Stops all profiles through 'netctl'
    :return: None
    """
    child = pexpect.spawn('sudo netctl stop-all', timeout=10)
    # Wait for sudo-prompt
    child.expect(re.escape("[sudo] password for ") + r".*:")

    # Use getpass for securely passing password to spawned process
    child.send(getpass() + "\n")

    # Wait for EOF before continuing connection routine
    child.expect(pexpect.EOF)


def get_mac_address(adapter: str) -> str:
    """
    Returns the MAC address of given adapter
    :param adapter: given adapter to fetch MAC address from
    :return: MAC address of adapter as string
    """
    return netifaces.ifaddresses(adapter)[netifaces.AF_LINK]


def change_mac_address(adapter: str, options: str) -> str:
    try:
        assert not is_any_profile_active()[0]  # Ensure that no profile is currently running
    except AssertionError:
        print("[Error] A profile is already active. Stopping all profiles and retrying.")

    child = pexpect.spawn('sudo macchanger ' + options + ' ' + adapter, timeout=10)
    child.expect(re.escape("[sudo] password for ") + r".*:")

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
    # Returns boolean on whether given profile is prefixed with 'netctl' standard '* ' pattern on listing
    return any(filter(re.compile(re.escape('* ') + profile + r'\s').match, output.decode().split('\n')))


def is_any_profile_active() -> (bool, str):
    """
    Runs 'netctl list' and checks whether any profile is marked '^\*'. If a match is found, the profile name is
    extracted and returned in the tuple, otherwise (False, '') is returned.
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

wait_for_connection('https://aau234q1gwb.dk')
