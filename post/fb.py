import json
import csv


def csv_to_json(txt):
    with open(txt, "r+") as txt_file:
        reader = csv.reader(txt_file)
        lst = list(reader)
        return lst


def make():
    fbk = csv_to_json("facebook.csv")[1:153]
    with open("facebook.txt", 'a') as _file:
        for a in range(len(fbk)):
            _file.write(f"Recipients.push(Recipient({fbk[a][1]}, {fbk[a][2]})); //{fbk[a][0]}\n")
    return True


def dist():
    fbk = csv_to_json("facebook.csv")[1:153]
    addr = list()
    amnt = list()
    with open("distr_fbk/undistributed.txt", 'a') as _file:
        n = 0
        for a in range(len(fbk)):
            _amnt = float(fbk[a][2])
            _addr = fbk[a][1]
            if _amnt == 0 or _amnt == 0.0 or not _addr.startswith('0x'):
                _file.write(f"Recipients.push(Recipient({fbk[a][1]}, {fbk[a][2]})); //{fbk[a][0]}\n")
                continue
            addr.append(_addr)
            amnt.append(int(_amnt*1000))
            n += 1
    assert len(addr) == len(amnt)
    with open("distr_fbk/fbk_addr.json", 'a') as _file:
        json.dump({'facebook_addresses': addr}, _file)
    with open("distr_fbk/fbk_amnt.json", 'a') as _file:
        json.dump({"facebook_amount": amnt}, _file)


dist()
# print(make())
