import socket
import struct
import textwrap
import binascii
import pandas

TAB_1 = '\t - '
TAB_2 = '\t\t - '
TAB_3 = '\t\t\t - '
TAB_4 = '\t\t\t\t - '

DATA_TAB_1 = '\t   '
DATA_TAB_2 = '\t\t   '
DATA_TAB_3 = '\t\t\t   '
DATA_TAB_4 = '\t\t\t\t   '

# Unpack Ethernet Frame
def ethernet_frame(data):
    dest_mac, src_mac, proto = struct.unpack('!6s6sH', data[:14])
    return get_mac_addr(dest_mac), get_mac_addr(src_mac), socket.htons(proto), data[14:]

# Format MAC Address
def get_mac_addr(bytes_addr):
    bytes_str = map('{:02x}'.format, bytes_addr)
    mac_addr = ':'.join(bytes_str).upper()
    return mac_addr

# Unpack IPv4 Packets Received
def ipv4_Packet(data):
    version_header_len = data[0]
    version = version_header_len >> 4
    header_len = (version_header_len & 15) * 4
    total_length, ttl, proto, src, target = struct.unpack('!2xH4xBB2x4s4s', data[:20])
    return total_length, version, header_len, ttl, proto, ipv4(src), ipv4(target), data[header_len:]

# Return Formatted IP Address
def ipv4(addr):
    return '.'.join(map(str, addr))


# Unpack for any ICMP Packet
def icmp_packet(data):
    icmp_type, code, checksum = struct.unpack('!BBH', data[:4])
    return icmp_type, code, checksum, data[4:]

# Unpack for any TCP Packet
def tcp_seg(data):
    (src_port, destination_port, sequence, acknowledgement, flags) = struct.unpack('!HHLLxs', data[:14])
    return src_port, destination_port, sequence, acknowledgement, bytes.hex(flags)
# Unpacks for any UDP Packet
def udp_seg(data):
    src_port, dest_port, length = struct.unpack('!HHH2x', data[:8])
    return src_port, dest_port, length, data[8:]

# Formats the output line
def format_output_line(prefix, string, size=80):
    size -= len(prefix)
    if isinstance(string, bytes):
        string = ''.join(r'\x{:02x}'.format(byte) for byte in string)
        if size % 2:
            size-= 1
            return '\n'.join([prefix + line for line in textwrap.wrap(string, size)])

data_buffer = pandas.DataFrame(columns=['Source MAC', 'Destination MAC','NetworkProto','SourceIP', 'DestinationIP',
                                'TTL','Proto','SourcePort','DestinationPort','SeqNum','AckNum','Flags'])
count = 0
conn = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
while True:
    raw_data, addr = conn.recvfrom(65536)
    dest_mac, src_mac, eth_proto, data = ethernet_frame(raw_data)
    print('\n Ethernet Frame: ')
    print(TAB_1 + 'Destination: {}, Source: {}, Protocol: {}'.format(dest_mac, src_mac, eth_proto))
    if eth_proto == 8:
        (total_length, version, header_length, ttl, proto, src, target, data2) = ipv4_Packet(data)
        print(TAB_1 + "IPV4 Packet:")
        print(TAB_2 + 'Version: {}, Header Length: {}, TTL: {}, Total Length: {}'.format(version, header_length, ttl, total_length))
        print(TAB_3 + 'protocol: {}, Source: {}, Target: {}'.format(proto, src, target))

        # ICMP
        if proto == 1:
            icmp_type, code, checksum, data3 = icmp_packet(data2)
            print(TAB_1 + 'ICMP Packet:')
            print(TAB_2 + 'Type: {}, Code: {}, Checksum: {},'.format(icmp_type, code, checksum))
            print(TAB_2 + 'ICMP Data:')
            print(format_output_line(DATA_TAB_3, data3))

        # TCP
        elif proto == 6:
            src_port, destination_port, sequence, acknowledgement, flags = tcp_seg(data2)
            print(TAB_1 + 'TCP Segment:')
            print(TAB_2 + 'Source Port: {}, Destination Port: {}'.format(src_port, destination_port))
            print(TAB_2 + 'Sequence: {}, Acknowledgment: {}'.format(sequence, acknowledgement))
            print(TAB_2 + 'Flags: {}'.format(flags))
            # print(TAB_3 + 'URG: {}, ACK: {}, PSH: {}'.format(flag_urg, flag_ack, flag_psh))
            # print(TAB_3 + 'RST: {}, SYN: {}, FIN:{}'.format(flag_rst, flag_syn, flag_fin))
            new_data = pandas.DataFrame([[src_mac, dest_mac, eth_proto, src, target, ttl, total_length,proto, src_port, destination_port, sequence, acknowledgement, flags, None]],
            columns= ['Source MAC', 'Destination MAC','NetworkProto','SourceIP', 'DestinationIP','TTL','TotalLength','Proto','SourcePort','DestinationPort','SeqNum','AckNum','Flags','UDPLength'])
            data_buffer = data_buffer.append(new_data, ignore_index=True)
            new_data.to_csv('data.csv',mode = 'a',index = False, header = False)
        
        # UDP
        elif proto == 17:
            src_port, dest_port, length, data3 = udp_seg(data2)
            print(TAB_1 + 'UDP Segment:')
            print(TAB_2 + 'Source Port: {}, Destination Port: {}, Length: {}'.format(src_port, dest_port, length))
            new_data = pandas.DataFrame([[src_mac, dest_mac, eth_proto, src, target, ttl, total_length, proto, src_port, dest_port, None, None, None, length]],
            columns= ['Source MAC', 'Destination MAC','NetworkProto','SourceIP', 'DestinationIP','TTL', 'TotalLength','Proto','SourcePort','DestinationPort','SeqNum','AckNum','Flags', 'UDPLength'])
            data_buffer = data_buffer.append(new_data, ignore_index= True)
            new_data.to_csv('data.csv',mode = 'a',index = False, header = False)
        # Other IPv4
        else:
            print(TAB_1 + 'Other IPv4 Data:')
            print(format_output_line(DATA_TAB_2, data2))

    else:
        print('Ethernet Data:')
        print(format_output_line(DATA_TAB_1, data))