import socket

ip = "127.0.0.1"
port = 8888


s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s.bind((ip,port))

threads = []
print(f"[!][!]  Server is up, running on {ip}, port- {port}  [!][!]")

#holds a tuple (ip,name,[x,y,angle],[actions])
active_players = []


def convert_raw(msg):
    res = []
    msg = msg.split(";")
    for i in msg:
        obj = {}
        for j in i.split(","):
            obj[j[0:j.find(":")]] = j[j.find(":") + 1:]
        res.append(obj)
    return res

while True:
    data, ip = s.recvfrom(1024)
    data = str(data)
    data = data[2:]
    data = data[:-1]
    data = convert_raw(data)
    print(f"=={ip}==>> {data}")