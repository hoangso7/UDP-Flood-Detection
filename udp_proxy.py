from optparse import OptionParser
import socket
import logging

import numpy as np 
from scipy.stats import entropy
from math import log, e 
import pandas as pd


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


rejected_ip = []
MAX_HIGH_ENTROPY_PACKETS = 10

def calc_entropy(labels, base=None):
    n_labels = len(labels)

    if n_labels <= 1:
        return 0

    value,counts = np.unique(labels, return_counts=True)
    probs = counts / n_labels
    n_classes = np.count_nonzero(probs)

    if n_classes <= 1:
        return 0

    ent = 0.

    # Compute entropy
    base = e if base is None else base
    for i in probs:
        ent -= i * log(i, base)

    return ent

def parse_args():
    parser = OptionParser()

    parser.add_option('--bind-address',
                      help='The address to bind, use 0.0.0.0 for all ip address.')
    parser.add_option('--port',
                      help='The port to listen, eg. 623.',
                      type=int)
    parser.add_option('--dst-ip',
                      help='Destination host ip, eg. 192.168.3.101.')
    parser.add_option('--dst-port',
                      help='Destination host port, eg. 623.',
                      type=int)

    return parser.parse_args()

(options, args) = parse_args()


def recv():
    sock_src = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_dst = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_addr = (options.bind_address, options.port)
    dst_addr = (options.dst_ip, options.dst_port)
    sock_src.bind(recv_addr)

    dos_count = 0

    while True:
        data, addr = sock_src.recvfrom(1024)

        # check banned ip address
        if(addr[0] in rejected_ip):
            continue

        arr = list(data)
        packet_entropy = calc_entropy(arr)
        if(packet_entropy > 5.0):
            
            print("[!] WARNING: Packet's entropy higher than expected.")
            dos_count += 1

            if(dos_count == MAX_HIGH_ENTROPY_PACKETS):
                print("_________________________________________")
                print("____[!] UDP FLOOD ATTACK DETECTED [!]____")
                print("_________________________________________")
                print(" IP address: "+ addr[0]+" was banned !")

                rejected_ip.append(addr[0])
                dos_count = 0 

            #drop packet
            continue

        if not data:
            logger.error('an error occured')
            break

        #logger.debug('received: {0!r} from {1}'.format(data, addr))
        sock_dst.sendto(data, dst_addr)
        data, _  = sock_dst.recvfrom(1024)
        sock_src.sendto(data, addr)

    sock_src.close()
    sock_dst.close()


if __name__ == '__main__':
    parse_args()
    try:
        recv()
    except KeyboardInterrupt:
        exit(0)
    # print(calc_entropy([1,3,5,2,3,5,10,13,54]))

#sudo python3 udp_proxy.py --bind-address 0.0.0.0 --port 777 --dst-ip 0.0.0.0 --dst-port 31337
