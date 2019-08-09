import netifaces


def prompt_index(length):
    return input("Select index [0-" + str(length - 1) + ']: ')


def get_boolean(prompt):
    while True:
        try:
            return {"y": True, "n": False}[input(prompt).lower()]
        except KeyError:
            print("Invalid input. Please enter 'y' or 'n'.")


def prompt_interface():
    interfaces = netifaces.interfaces()
    print('Which of the following interfaces is the wireless adapter?')
    print(interfaces)

    adapter_index = prompt_index(len(interfaces))
    while int(adapter_index) < 0 or int(adapter_index) > (len(interfaces) - 1):
        print("Index chosen: %s is out of bounds. Try again" % adapter_index)
        adapter_index = prompt_index(len(interfaces))
    return netifaces.interfaces()[int(adapter_index)]


def prompt_credentials():
    username = input("Please input username/email: ")
    password = input("Please input password: ")
    return [username, password]


def prompt_mac():
    global options
    mac_enabled = get_boolean(input("Enable macchanger to randomise MAC-address upon each connection? [y/n]: "))
    if mac_enabled:
        options = input("What options do you want to pass macchanger? '-e' keeps vendor-specific bytes: ")
    return [mac_enabled, options]


print("Chose interface: " + prompt_interface())
print("Chose credentials: ", end='')
for s in prompt_credentials():
    print('\t' + str(s))

print("Chose MAC-settings: ", end='')
for s in prompt_mac():
    print('\t' + str(s))
