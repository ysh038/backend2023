import json
import sys


def main(argv):
    obj1 = {
        "name": "SH Yoo",
        "id": 60172174,
    }

    obj2 = {
        "phone": "010-0000-0000",
        "age": 20,
    }

    obj = [obj1, obj2]

    s = json.dumps(obj, indent=2)
    print(s)


if __name__ == "__main__":
    main(sys.argv)
