import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


import sys
import datetime

#test

lines = sys.stdin.read().splitlines()
format_type = lines[0].strip() if lines else "iso"

now = datetime.datetime.utcnow()

if format_type == "timestamp":
    print(str(int(now.timestamp())))
else:
    print(now.isoformat())