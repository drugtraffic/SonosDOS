import soco,string,threading
from socket import *

def scan():
    ip = gethostbyname(gethostname())
    device = soco.discover(5, False, ip)
    iplist = []
    for x in str(device).split(','):
        iplist.append(x.split("\"")[1])

    return iplist

def webserver(iplist: list):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', 80))
    serverSocket.listen(1)
    while True:
        global selectedSpeaker
        global deauthing
        global t_deauth
        c, (client_host, client_port) = serverSocket.accept()
        rec = format_recieval(c.recv(1000))
        if(rec[0].count('GET')!=0):
            to_get = rec[0].split(' ')[1]
            print(to_get)
            if 'speaker' in to_get.split('/'):
                selectedSpeaker = int(to_get.split('/')[2])
            elif 'deauth' in to_get.split('/'):
                deauthing = False if deauthing else True
                t_deauth = threading.Thread(target=deauth_thread)
                t_deauth.start()
            for x in getmsg():
                c.send(bytes(x, encoding='utf8'))


        c.close()

    serverSocket.close()

def format_recieval(uf_rec: bytes):
    uf_rec = str(uf_rec,encoding='utf8')
    uf_rec = uf_rec.split('\n')
    return uf_rec

def getmsg():
    msg = []
    msg.append("HTTP/1.0 200 OK")
    msg.append("Content-Type: text/html")
    msg.append("")
    for x in gethtml():
       msg.append(f"{x}\n")
    return msg

def gethtml():
    global selectedSpeaker
    global deauthing
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<body>")
    html.append("<h1>Sonoshack Webserver</h1>")
    html.append(f"<h2>{len(devices)} speakers found</h2>")
    c=0
    for x in speakernames:
        html.append(f"<p><a href=\"/speaker/{c}\">Speaker</a> {c}: {x}</p>")
        c+=1
    html.append("\n")
    if selectedSpeaker != None:
        html.append(f"<h2> Selected speaker: {selectedSpeaker}")
        html.append(f"<p><a href=\"/deauth\">Toggle deauth: {'on' if deauthing else 'off'}</a></p>")
    html.append("</body>")
    html.append("</html>")

    bsn = []
    for x in html:
        bsn.append(f"{x}\n")
    return bsn

def deauth_thread():
    global deauthing
    global selectedSpeaker
    while deauthing:
        soco.SoCo(devices[selectedSpeaker]).pause()

global selectedSpeaker
global deauthing

if __name__ == "__main__":
    global selectedSpeaker
    global deauthing
    deauthing = False

    devices = scan()
    print(f"{len(devices)} speakers found!")
    speakernames = []
    selectedSpeaker = None
    for x in devices:
        #print(str(soco.SoCo(x).get_speaker_info()))
        speakernames.append(str(soco.SoCo(x).get_speaker_info()).split('\'')[3])
    webserver(devices)
