from collections import defaultdict

import toml
import os


def load_config(path: str) -> dict:
    """
    Loads a config from given path and returns the dict resulting from a toml parse
    :param path: the path to the config to load
    :return: a dict of the config
    """
    default_options = dict({'network': dict({'work_networks': ['work', 'aau'], 'ping_address': 'https://aau.dk'}),
                            'macchanger': dict({'enabled': True, 'options': '-e'}),
                            'cas': dict({'cas_password_page': 'login.aau.dk'})})
    try:
        f = open(path)
        config = toml.loads(''.join(f.readlines()))
        f.close()
        out = defaultdict(dict, default_options)
        out.update(config) # TODO; update does not seem to work
        return out
    except FileNotFoundError:
        print(f"[Error] Could not find config at path: '{path}'.\nThe config should be placed at '$XDG_CONFIG_HOME"
              f"/.config/chwifi/config'.")
        exit(1)


def write_config(path: str, config: dict):
    """
    Writes dict as toml to given file, overwriting any existing file
    :param path: the path to the resulting file
    :param config: the dict to write
    """
    try:
        # Write passed dict, as toml, to path
        toml.dump(config, open(path, 'w'))
    except OSError as e:
        print(f"[Error] Some error occurred when trying to write to '{path}'")
        # Re-raise exception for verbosity on error
        raise e


# config_dir = os.path.expanduser('~') + '/.config/chwifi'
# Override for development
config_path = "config-sample.toml"

parsed_toml = load_config(config_path)

write_config("config-test.toml", parsed_toml)

print('result: ')

print(parsed_toml['credentials']['username'])
print(parsed_toml['credentials']['password'])
