def checkReverse(toCheck):
    if set(toCheck["end"].strip()).issubset(set(toCheck["cur"])):
        return True
    else:
        return False


def shiftList(item: object):
    arr = list(item["cur"])
    btf = bool(item["reverse"])
    end = bool(item["end"])
    # only shift our array if we have a defined endpoint
    if end:
        if btf:
            return "".join(arr[1:] + arr[:1])
        else:
            return "".join(arr[-1:] + arr[:-1])
    else:
        return item["cur"]
