import argparse

parser = argparse.ArgumentParser(
    description="Connect to home or work wireless networks, caching rolling passwords at work.")

parser.add_argument('profile', metavar='PROFILE', type=str, nargs=1, help="the profile to connect to")
parser.add_argument('-s', '--show', nargs='?', type=int, default=False,
                    help="display the daily password of the given index or day")
parser.add_argument('-r', '--restart', type=bool, default=False, help="restarts the current profile")

args = parser.parse_args()

print(args)

