import json
import csv

def csv_to_json(txt):
    with open(txt, "r+") as txt_file:
        reader = csv.reader(txt_file)
        lst = list(reader)
        return lst

def make():
    fbk = csv_to_json("telegram.csv")[1:42]
    with open("telegram.txt", 'a') as _file:
        for a in range(len(fbk)):
            _file.write(f"Recipients.push(Recipient({fbk[a][1]}, {fbk[a][2]})); //{fbk[a][0]}*1000\n")
    return True
        
def dist():
    fbk = csv_to_json("telegram.csv")[1:42]
    addr = list()
    amnt = list()
    with open("distr_tg/undistributed.txt", 'a') as _file:
        n = 0
        for a in range(len(fbk)):
            try:
                _amnt = float(fbk[a][2])
            except ValueError:
                _amnt = _amnt
            _addr = fbk[a][1]
            if _amnt == 0 or type(_amnt) == str or not _addr.startswith('0x'):
                _file.write(f"Recipients.push(Recipient({fbk[a][1]}, {fbk[a][2]})); //{fbk[a][0]}\n")
                continue
            addr.append(_addr)
            amnt.append(int(_amnt*1000))
            n += 1
    assert len(addr) == len(amnt)
    with open("distr_tg/tg_addr.json", 'a') as _file:
        json.dump({'telegram_addresses': addr}, _file)
    with open("distr_tg/tg_amnt.json", 'a') as _file:
        json.dump({"telegram_amount": amnt}, _file)


dist()
# print(make())