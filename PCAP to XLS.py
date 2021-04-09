# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 21:31:30 2020

@author: thang
"""


import pandas as pd
import struct

connection_list = []
packet_list = []
ip_list = []
packets_per_proto = [0, 0, 0, 0]

list_file = ['D:\FIL\Bot-Analysis\PCAP\DDoS\IoT_Dataset_HTTP_DDoS__00001_20180604190104.pcap']

def main():
    count = -1
    for file in list_file:
        f = open(file, 'rb')
        buffer = f.read(24) #Global header
        #Check magic number
        if(buffer[0] == 212):
            print('Little endianness\n')
        else:
            print('Big endianness\n')
    
        #The following code assumed the byte were arranged in little endianness order
        write_data = []
        buffer = f.read(16)
        while(buffer):
            count += 1
            if(count == 300000):
                break
            new_packet = packet()
            seconds, micro_seconds, saved_length = struct.unpack('< I I I', buffer[:12])
            new_packet.record_time = seconds + micro_seconds / 1000000
            buffer = f.read(saved_length)
            ether_proto, data = ethernet_frame(buffer)
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
                (src, dest) = arp_packet(data)
                new_packet.ip1 = src
                new_packet.ip2 = dest
                new_packet.packet_length = 28
                new_packet.proto = 2
            else:
                buffer = f.read(16)
                continue
            
            packets_per_proto[new_packet.proto - 1] += 1
            packet_list.append(new_packet)
            (src_2_dest_packets, src_2_dest_bytes, dest_2_src_packets, dest_2_src_bytes, total_packets_tran, total_bytes_tran) = connection_control(new_packet)
            packet_control(new_packet.record_time)
            (src_total_packets, src_total_bytes, dest_total_packets, dest_total_bytes) = ip_control(new_packet.ip1, new_packet.ip2, new_packet.packet_length)
            if (new_packet.ip1[0:13] == '192.168.100.1'):
                if(new_packet.ip2[0:11] == '192.168.100'):
                    label = 1
            elif (new_packet.ip2[0:13] == '192.168.100.1'):
                if(new_packet.ip1[0:11] == '192.168.100'):
                    label = 1
            else:
                label = 0
        
            features = [new_packet.record_time, new_packet.ip1, new_packet.port1, new_packet.ip2,
                        new_packet.port2, new_packet.packet_length, new_packet.proto,
                        src_2_dest_packets, src_2_dest_bytes, dest_2_src_packets, dest_2_src_bytes,
                        total_packets_tran, total_bytes_tran, src_total_packets, src_total_bytes,
                        dest_total_packets, dest_total_bytes, 
                        packets_per_proto[new_packet.proto - 1], label]
            write_data.append(features)
            buffer = f.read(16)
        
    write_file = pd.DataFrame(write_data, columns = ['Stime','Source IP', 'Source port', 'Dest IP', 'Dest port', 'Packet length', 'Protocol', 'S2D packets', 'S2D bytes', 'D2S packets', 'D2S bytes', 'Total packets in transaction', 'Total bytes in transaction', 'Source total packets', 'Source total bytes', 'Dest total packets', 'Dest total bytes', 'Packets per protocol', 'Label'])
    write_file.to_excel('DDoS_HTTP.xlsx', index = None)
    
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
                   return item.src2dest_packets, item.src2dest_bytes, item.dest2src_packets, item.dest2src_bytes, item2.total_packets, item2.total_bytes
            new_transaction = connection.transaction()
            new_transaction.port1 = new_packet.port1
            new_transaction.port2 = new_packet.port2
            new_transaction.total_packets = 1
            new_transaction.total_bytes = new_packet.packet_length
            (item.transaction_list).append(new_transaction)
            return item.src2dest_packets, item.src2dest_bytes, item.dest2src_packets, item.dest2src_bytes, 1, new_packet.packet_length
        elif ((item.ip1 == new_packet.ip2) & (item.ip2 == new_packet.ip1)):
            item.dest2src_bytes += new_packet.packet_length
            item.dest2src_packets += 1
            for item2 in item.transaction_list:
                if((item2.port1 == new_packet.port2) & (item2.port2 == new_packet.port1)):
                   item2.total_bytes += new_packet.packet_length
                   item2.total_packets += 1
                   return item.dest2src_packets, item.dest2src_bytes, item.src2dest_packets, item.src2dest_bytes, item2.total_packets, item2.total_bytes
            new_transaction = connection.transaction()
            new_transaction.port1 = new_packet.port2
            new_transaction.port2 = new_packet.port1
            new_transaction.total_packets = 1
            new_transaction.total_bytes = new_packet.packet_length
            (item.transaction_list).append(new_transaction)
            return item.dest2src_packets, item.dest2src_bytes, item.src2dest_packets, item.src2dest_bytes, 1, new_packet.packet_length
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
        if (time - packet.record_time > 10):
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
                            item2.total_packets -= 1
                            item2.total_bytes -= packet.packet_length
                            if(item2.total_packets == 0):
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
                            item2.total_packets -= 1
                            item2.total_bytes -= packet.packet_length
                            if(item2.total_packets == 0):
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

    
