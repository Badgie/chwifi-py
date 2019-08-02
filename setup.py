import netifaces


def prompt_index(length):
    return input("Select index [0-" + str(length - 1) + ']: ')


def prompt_interface():
    interfaces = netifaces.interfaces()
    print('Which of the following interfaces is the wireless adapter?')
    print(interfaces)

    adapter_index = prompt_index(len(interfaces))
    while int(adapter_index) < 0 or int(adapter_index) > (len(interfaces) - 1):
        print("Index chosen: %s is out of bounds. Try again" % adapter_index)
        adapter_index = prompt_index(len(interfaces))
    return int(adapter_index)


adapter = netifaces.interfaces()[prompt_interface()]
print("Chose: " + adapter)
