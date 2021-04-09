# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 10:30:39 2020

@author: thang
"""

import socket
import struct
import time

connection_list = []
packet_list = []
ip_list = []
packets_per_proto = [0, 0, 0, 0]


def main():
    global packets_per_proto
    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    #conn = socket.socket(socket.AF_INET, socket.SOCK_RAW)
    while True:
        data, addr = conn.recvfrom(65536)
        new_packet = packet()
        new_packet.record_time = time.time()
        ether_proto, data = ethernet_frame(data)
        
        #IPv4
        if ether_proto == 2048:
            packet_length, proto, src, dest, data = ipv4_packet(data)
            new_packet.packet_length = packet_length
            new_packet.ip1 = src
            new_packet.ip2 = dest
            #ICMP
            if proto == 1:
                new_packet.proto = 4
                new_packet.port1 = -1
                new_packet.port2 = -1
            #TCP
            elif (proto == 6):
                src_port, dest_port = struct.unpack('! H H', data[:4])
                new_packet.port1 = src_port
                new_packet.port2 = dest_port
                new_packet.proto = 1
            #UDP
            elif (proto == 17):
                src_port, dest_port = struct.unpack('! H H', data[:4])
                new_packet.port1 = src_port
                new_packet.port2 = dest_port
                new_packet.proto = 3
                
        #ARP
        elif ether_proto == 2054:
            new_packet.port1 = -1
            new_packet.port2 = -1
            src, dest = arp_packet(data)
            new_packet.ip1 = src
            new_packet.ip2 = dest
            new_packet.packet_length = 28
            new_packet.proto = 2
            
        packets_per_proto[new_packet.proto - 1] += 1
            
        #IPv6
        #elif ether_proto == 34525
        packet_list.append(new_packet)
        (src_2_dest_packets, src_2_dest_bytes, dest_2_src_packets, dest_2_src_bytes, to_pkts_tr, to_by_tr) = connection_control(new_packet)
        packet_control(new_packet.record_time)
        (src_total_packets, src_total_bytes, dest_total_packets, dest_total_bytes) = ip_control(new_packet.ip1, new_packet.ip2, new_packet.packet_length)
        print('\n\nPacket')
        print('\nSource: {}, Source_port: {}, Dest: {}, Dest_port: {}'.format(new_packet.ip1, new_packet.port1, new_packet.ip2, new_packet.port2))
        print('\nProto: {}, Packet length: {}'.format(new_packet.proto, new_packet.packet_length))
        print('\nS2D_packets: {}, S2D_bytes :{}, D2S_packets: {}, D2S_bytes: {}'.format(src_2_dest_packets, src_2_dest_bytes, dest_2_src_packets, dest_2_src_bytes))
        print('\nTotal_packets_transaction: {}, Total_bytes_transaction: {}'.format(to_pkts_tr, to_by_tr))
        print('\nSrc_packets: {}, Src_bytes: {}, Dest_packets: {}, Dest_bytes: {}'.format(src_total_packets, src_total_bytes, dest_total_packets, dest_total_bytes))
            
def ethernet_frame(data):
    src_mac, dest_mac, ether_proto = struct.unpack('! 6s 6s H', data[:14])
    return ether_proto, data[14:]

#Unpack IPv4 packet
def ipv4_packet(data):
    version_header_length = data[0]
    header_length = (version_header_length & 15) * 4
    packet_length, proto, src, target = struct.unpack("! 2x H 5x B 2x 4s 4s", data[:20])
    return packet_length, proto, ipv4(src), ipv4(target), data[header_length:]

#Returns properly IPv4 address
def ipv4(addr):
    return '.'.join(map(str,addr))
 
def arp_packet(data):
    src, target = struct.unpack('! 14x 4s 6x 4s', data[:28])
    return ipv4(src), ipv4(target)

class connection:
    ip1 = ''
    ip2 = ''
    src2dest_packets = 0
    src2dest_bytes = 0
    dest2src_packets = 0
    dest2src_bytes = 0
    transaction_list = []
    class transaction:
        port1 = 0
        port2 = 0
        total_packets = 0
        total_bytes = 0
        
class packet:
    record_time = 0
    ip1 = ''
    port1 = 0
    ip2 = ''
    port2 = 0
    packet_length = 0
    proto = 0
class ip_addr:
    ip = ''
    total_bytes = 0
    total_packets = 0
    
def connection_control(new_packet):
    global connection_list
    for item in connection_list:
        if ((item.ip1 == new_packet.ip1) & (item.ip2 == new_packet.ip2)):
            item.src2dest_bytes += new_packet.packet_length
            item.src2dest_packets += 1
            for item2 in item.transaction_list:
                if((item2.port1 == new_packet.port1) & (item2.port2 == new_packet.port2)):
                   item2.total_bytes += new_packet.packet_length
                   item2.total_packets += 1
                   break
            new_transaction = connection.transaction()
            new_transaction.port1 = new_packet.port1
            new_transaction.port2 = new_packet.port2
            new_transaction.total_packets = 1
            new_transaction.total_bytes = new_packet.packet_length
            (item.transaction_list).append(new_transaction)
            return item.src2dest_packets, item.src2dest_bytes, item.dest2src_packets, item.dest2src_bytes, item2.total_packets, item2.total_bytes
        elif ((item.ip1 == new_packet.ip2) & (item.ip2 == new_packet.ip1)):
            item.dest2src_bytes += new_packet.packet_length
            item.dest2src_packets += 1
            for item2 in item.transaction_list:
                if((item2.port1 == new_packet.port2) & (item2.port2 == new_packet.port1)):
                   item2.total_bytes += new_packet.packet_length
                   item2.total_packets += 1
                   break
            new_transaction = connection.transaction()
            new_transaction.port1 = new_packet.port2
            new_transaction.port2 = new_packet.port1
            new_transaction.total_packets = 1
            new_transaction.total_bytes = new_packet.packet_length
            (item.transaction_list).append(new_transaction)
            return item.dest2src_packets, item.dest2src_bytes, item.src2dest_packets, item.src2dest_bytes, item2.total_packets, item2.total_bytes
    new_connection = connection()
    new_connection.transaction_list = []
    new_connection.ip1 = new_packet.ip1
    new_connection.ip2 = new_packet.ip2
    new_connection.src2dest_packets = 1
    new_connection.src2dest_bytes = new_packet.packet_length
    new_transaction = connection.transaction()
    new_transaction.port1 = new_packet.port1
    new_transaction.port2 = new_packet.port2
    new_transaction.total_packets = 1
    new_transaction.total_bytes = new_packet.packet_length
    (new_connection.transaction_list).append(new_transaction)
    connection_list.append(new_connection)
    return 1, new_packet.packet_length, 0, 0, 1, new_packet.packet_length
    
def packet_control(time):
    global packet_list
    global connection_list
    global packets_per_proto
    i = -1
    for packet in packet_list:
        if (time - packet.record_time > 60):
            i += 1
            j = -1
            for item in connection_list:
                j = j + 1
                if ((item.ip1 == packet.ip1) & (item.ip2 == packet.ip2)):
                    item.src2dest_packets -= 1
                    item.src2dest_bytes -= packet.packet_length
                    k = -1
                    for item2 in item.transaction_list:
                        k += 1
                        if((item2.port1 == packet.port1) & (item2.port2 == packet.port2)):
                            item2.total_packet -= 1
                            item2.total_bytes -= packet.packet_length
                            if(item2.total_packet == 0):
                                del connection_list[j].transaction_list[k]
                            break
                    break
                elif ((item.ip1 == packet.ip2) & (item.ip2 == packet.ip1)):
                    item.dest2src_packets -=1
                    item.dest2src_bytes -= packet.packet_length
                    k = -1
                    for item2 in item.transaction_list:
                        k += 1
                        if((item2.port1 == packet.port2) & (item2.port2 == packet.port1)):
                            item2.total_packet -= 1
                            item2.total_bytes -= packet.packet_length
                            if(item2.total_packet == 0):
                                del connection_list[j].transaction_list[k]
                            break
                    break
                if ((item.src2dest_packets == 0) & (item.dest2src_packets == 0)):
                    del connection_list[j]
                        
            j = -1
            for item in ip_list:
                j += 1
                if(packet.ip1 == item.ip):
                    item.total_bytes -= packet.packet_length
                    item.total_packets -= 1
                    if (item.total_packets == 0):
                        del ip_list[j]
                    break
        else:
            break
    if (i >= 0):
        for item in packet_list[0:i + 1]:
            packets_per_proto[item.proto - 1] -= 1
        del packet_list[0:i + 1]
            
def ip_control(src_ip, dest_ip, packet_length):
    global ip_list
    check = 0
    ip1_total_bytes = 0
    ip1_total_packets = 0
    ip2_total_bytes = 0
    ip2_total_packets = 0
    for item in ip_list:
        if(item.ip == src_ip):
            item.total_bytes += packet_length
            item.total_packets += 1
            check = 1
            ip1_total_bytes = item.total_bytes
            ip1_total_packets = item.total_packets
            break
    if (check == 0):
        new_ip = ip_addr()
        new_ip.ip = src_ip
        new_ip.total_bytes = packet_length
        new_ip.total_packets = 1
        ip_list.append(new_ip)
        ip1_total_bytes = packet_length
        ip1_total_packets = 1
        
    for item in ip_list:
        if(item.ip == dest_ip):
            ip2_total_bytes = item.total_bytes
            ip2_total_packets = item.total_packets
            break
    return ip1_total_packets, ip1_total_bytes, ip2_total_packets, ip2_total_bytes

main()
        