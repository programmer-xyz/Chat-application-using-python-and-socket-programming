'''
This module defines the behaviour of server in your Chat Application
'''
import sys
from client import Client
import getopt
import socket
import util
from queue import Queue
# import time
from threading import Thread
import math
import random
import datetime
# from goto import goto, comefrom, label

MAX_NUM_CLIENTS = 10
# recv_msg = ''
class Server:
    '''
    This is the main Server Class. You will to write Server code inside this class.
    '''

    def __init__(self, dest, port, window):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))
        self.window = window
        # to store queue of messages of a given client
        self.clients = {}
        self. client_msg_list = {}
        self.size = 4096

        self.recv_msg = ''
        # to store messages of a current givrrn client
        self.client_messages = {}
        # ack num of the current given client this is current ack num addr vs ack_num
        # ack received
        self.ack_num_next = {}
        #one we get from client
        self.ack_behji= {}
        # validated
        self.ack_gotten = {}
        # dict to store time of each packet
        self.time_of_each_packet = {}


    def join_func(self, user_name, address):
        '''join.'''
        if len(self.clients) == 10:
            msg_send = util.make_message('err_server_full', 2, )
            msg_pack2 = util.make_packet('data', 0, msg_send)
            # msg_send.encode("utf-8")
            self.sock.sendto(msg_pack2.encode('utf-8'), address)
            print("disconnected: server full")
        elif user_name in self.clients.values():
            msg_send = util.make_message('err_username_unavailable', 2,)
            msg_pack = util.make_packet('data', 0, msg_send)
            # msg_send.encode("utf-8")
            self.sock.sendto(msg_pack.encode('utf-8'), address)
            print("disconnected: username not available")
        else:
            self.clients[address] = user_name
            print("join:", user_name)

    def dic_search(self, user_list, msg, user_name):
        '''search client'''
        msg = user_name + ': ' + msg
        for user in user_list:
            if user in self.clients.values():
                msg_send2 = util.make_message('forward_message', 4 , msg)
                # msg_packet = util.make_packet('data', 0, msg_send2)
                addr = self.ret_user_addr(user)
                # self.sock.sendto(msg_packet.encode('utf-8'), addr)
                self.make_chunks(msg_send2, addr)
            else:
                # msg: <sender username> to non-existent user <recv. username>
                send = 'msg: ' + user_name +  ' to non-existent user ' + user
                print(send)

    def rem_duplicates_list(self, user_list):
        '''A dup'''
        user_list = list(dict.fromkeys(user_list))
        return user_list

    def dict_search_file(self, user_list, msg, user_name, file_name):
        '''search'''
        msg = user_name + ': '+ file_name + ' \n'  + msg
        print(msg)
        for user in user_list:
            if user in self.clients.values():
                # print('msg:', user_name)
                msg_send2 = util.make_message('forward_file', 4 , msg)
                # msg_packet = util.make_packet('data', 0, msg_send2)
                addr = self.ret_user_addr(user)
                # self.sock.sendto(msg_packet.encode('utf-8'), addr)
                self.make_chunks(msg_send2, addr)
            else:
                s_s = 'file: ' + user_name +  ' to non-existent user ' + user
                print(s_s)

    def ret_user_addr(self, name):
        '''addr'''
        user_addr = 0
        res = not bool(self.clients)
        if res is False:
            key_list = list(self.clients.keys())
            val_list = list(self.clients.values())
            pos = val_list.index(name)
            user_addr = key_list[pos]
        return user_addr

    def start_manager(self, client_addr, seq_num):
        '''addr'''
        msg_queue = Queue(0)
        self.client_msg_list[client_addr] = msg_queue
        # put next ack num in ack dict
        self.ack_behji[client_addr] = seq_num + 1
        seq_num_send = self.ack_behji[client_addr]
        #send ack
        util.msg_sender(self.sock, client_addr, seq_num_send)

    def client_handler2(self, message_packet, client_addr):
        # message is a packet
        '''addr'''
        # self.client_msg_list[client_addr].put(message_packet)
        # get the top ele in queue if it is wrong no send ack if right the
        # concatinate to string and store string in dict
        end_recv = False
        recv_msg = ''
        recv_control = False
        msg_type, seq_num, _str_msg, _check_sum = util.msg_decoder(message_packet)
        seq_num = int(seq_num)
        data_start = False
        if msg_type == 'ack':
            # if client_addr not in self.client_msg_list.keys():
            self.ack_num_next[client_addr] = seq_num

        elif msg_type == 'start':
            # self.client_msg_list[client_addr].put(message_packet)
            # if client_addr not in self.client_msg_list.keys():
            # new message by person new queue
            recv_control = True
            self.start_manager(client_addr, seq_num)

        elif msg_type == 'data':
            if self.ack_behji[client_addr] == seq_num:
                self.client_msg_list[client_addr].put(message_packet)
                if data_start == False:
                    data_start = True

                self.ack_behji[client_addr] = self.ack_behji[client_addr] + 1
                if recv_control == True:
                    recv_control = False

            util.msg_sender(self.sock, client_addr, self.ack_behji[client_addr])

        elif msg_type == 'end':
           # self.universal = True

            ack_list = list(self.ack_behji.keys())
            if client_addr in ack_list:
                # recv_msg = ''
                if self.ack_behji[client_addr] == seq_num:

                    while 1:
                        if self.client_msg_list[client_addr].empty():
                            break
                        else:
                            msg_type, _seq_num, str_msg, _check_sum = util.msg_decoder(self.client_msg_list[client_addr].get())
                            recv_msg =  recv_msg + str_msg

                    num = self.ack_behji[client_addr] + 1
                    util.msg_sender(self.sock, client_addr, num)
                    del self.ack_behji[client_addr]
                    # del self.client_msg_list[client_addr]
                    end_recv = True
                    return recv_msg
                else:
                    util.msg_sender(self.sock, client_addr, self.ack_behji[client_addr])

        if end_recv == False:
            return " "

        elif end_recv == True:
            return recv_msg

    def sending_packet(self, type, seq_num, msg_to_send, client_address):
        '''addr'''
        msg_packet = util.make_packet(type, seq_num, msg_to_send)
        self.sock.sendto(msg_packet.encode('utf-8'), client_address)

    def ack_timer_khatam(self, time_elapsed):
        '''ans'''
        ans = False
        if datetime.datetime.now() - time_elapsed > datetime.timedelta(seconds = 0.5):
            ans = True
            return ans
        else:
            ans = False
            return ans

    def sending_start(self, client_address, start_seq_num, msg_packet):
        '''add'''
        temp_ack_storer = {}
        ack_control = False

        while 1:

            if self.ack_num_next[client_address]== start_seq_num + 1:
                break

            if ack_control is True:
                ack_control= False

            temp_ack_storer[client_address] = start_seq_num

            if self.ack_timer_khatam(self.time_of_each_packet[client_address]):
                temp_ack_storer[client_address] = start_seq_num + 1
                self.sock.sendto(msg_packet.encode('utf-8'), client_address)
                ack_control = True
                self.time_of_each_packet[client_address] = datetime.datetime.now()


    def data_retransmission(self, client_address):
        '''abc'''
        temp_timer = False
        while not self.ack_timer_khatam(self.time_of_each_packet[client_address]):

            if temp_timer is True:
                temp_timer = False

            if self.ack_num_next[client_address] == self.ack_gotten[client_address] + 1:
                temp_timer = True
                self.ack_gotten[client_address] = self.ack_gotten[client_address] + 1
                self.ack_num_next[client_address] = -1
                break


    def data_transmission(self, client_address, last_seq_num, start_seq_num, chunks):
        '''aggr'''
        #timer per packet stores the bool validation of each data
        # packet on whether it has been received correctly
        msg_control = False
        retransmission_count = 0
        while self.ack_gotten[client_address] != last_seq_num -1:
             # to change the status os the packet recieve validation after each iteration
            if msg_control is False:
                msg_control= True

            i = self.ack_gotten[client_address] - start_seq_num - 1
            retransmission_count = retransmission_count + 1
            packet = util.make_packet("data", self.ack_gotten[client_address], chunks[i])
            self.sock.sendto(packet.encode('utf-8'), client_address)
            msg_control = True
            self.time_of_each_packet[client_address] = datetime.datetime.now()
            self.data_retransmission(client_address)

            if msg_control is True:
                msg_control= False


    def make_chunks(self, msg, client_address):
        '''thr'''
        t_var = Thread(target= self.make_chunks2, args = (msg, client_address))
        t_var.daemon = True
        t_var.start()

    def end_sender(self, client_address, last_seq_num, packet):
        # While right ack not received keep on sending acks
        ack_control = False
        while 1:
            if self.ack_num_next[client_address] == last_seq_num:
                break

            if ack_control is True:
                ack_control = False

            if self.ack_timer_khatam(self.time_of_each_packet[client_address]):
                self.sock.sendto(packet.encode('utf-8'), client_address)
                ack_control = True
                self.time_of_each_packet[client_address] = datetime.datetime.now()

    def make_chunks2(self, msg, client_address):
        '''addr'''
        #msg is string
        seq_num = random.randint(1, 100000)
        start_seq_num = seq_num
        x_var = sys.getsizeof(msg)
        num_of_packets = math.ceil(x_var / util.CHUNK_SIZE)
        chunk_siz_chars=math.ceil(len(msg) / num_of_packets)
        # return num of characters taht should be in each packet
        chunks = [msg[i:i+ chunk_siz_chars] for i in range(0, len(msg), chunk_siz_chars)]
        # print(chunks) # list of packet content

        _num = seq_num + 1
        #chunk[0]
        num_of_data_packets = len(chunks)
        last_seq_num =  start_seq_num + num_of_data_packets + 2
        # find start end and data seq numbers

        self.ack_gotten[client_address] = -1
        self.ack_num_next[client_address] = -1


        msg_packet = util.make_packet('start', seq_num,)
        self.sock.sendto(msg_packet.encode('utf-8'), client_address)
        self.time_of_each_packet[client_address] = datetime.datetime.now()

        #retransmit start till ack recved for start
        self.sending_start(client_address, start_seq_num, msg_packet)

        self.ack_gotten[client_address] = self.ack_num_next[client_address]

        self.ack_num_next[client_address] = -1


        self.data_transmission(client_address, last_seq_num, start_seq_num, chunks)

        # Create & Send End Packet + Record Timestamp
        packet = util.make_packet("end", last_seq_num - 1, "")
        self.sock.sendto(packet.encode('utf-8'), client_address)
        self.time_of_each_packet[client_address] = datetime.datetime.now()

        self.end_sender(client_address, last_seq_num, packet)

        # Reset Server State
        self.ack_num_next[client_address] = -1
        self.ack_gotten[client_address] = -1


    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it
        '''
        user_name = ''
        # global recv_msg
        # recv_msg = ''
        print("connecting to server")

        while 1:

            message, client_address = self.sock.recvfrom(self.size)

            msg_ans = self.client_handler2(message, client_address)
           # self.client_messages[client_addr] = self.client_messages[client_addr] + recv_msg
            if msg_ans != " ":

                # message_list = self.client_messages[client_address].split()
                message_list = msg_ans.split()
                message_type = message_list[0]
                # line_list = self.client_messages[client_address].split('\n')
                line_list = msg_ans.split('\n')

                if message_type == 'join':
                    #add user name and address
                    self.join_func(message_list[-1], client_address)

                elif message_type == 'request_users_list':
                    user_name = self.clients[client_address]
                    print("request_users_list:", user_name)
                    list1 = list(self.clients.values())
                    sorted_list = sorted(list1)
                    str_msg = ' '.join(sorted_list)
                    msg_send = util.make_message('response_users_list', 3, str_msg)
                    self.make_chunks(msg_send, client_address)
                    # msg_send = util.make_packet('data', 0, msg_send)
                    # self.sock.sendto(msg_send.encode("utf-8"), client_address)

                elif message_type == 'send_message':
                    num_of_users = int(message_list[3])
                    # print(num_of_users)
                    user_name = self.clients[client_address]
                    print("msg:", user_name)
                    end_index = 4 + (num_of_users)
                    user_list = message_list[4 : end_index]
                    user_list = self.rem_duplicates_list(user_list)
                    msg = message_list[end_index: ]
                    msg = ' '.join(msg)
                    # print(user_list)
                    self.dic_search(user_list, msg, user_name)

                elif message_type == 'disconnect':
                    print('disconnected:',self.clients[client_address])
                    self.clients.pop(client_address)

                elif message_type == 'send_file':
                    num_of_users = int(message_list[3])
                    user_name = self.clients[client_address]
                    #msg received from client without user names
                    end_index = 5 + (num_of_users)
                    user_list = message_list[4 : end_index-1]
                    user_list = self.rem_duplicates_list(user_list)
                    # msg = message_List[end_index: ]
                    line_msg = line_list[1:]
                    file_name = message_list[end_index - 1]
                    msg = '\n'.join(line_msg)
                    print(msg)
                    print("file:", user_name)
                    self.dict_search_file(user_list, msg, user_name, file_name)

                elif message_type == 'garbage':
                    m_str = 'disconnected: ' + self.clients[client_address] +' sent unknown command'
                    print(m_str)
                    msg_send = util.make_message('err_unknown_message', 2, )
                    self.make_chunks(msg_send, client_address)
                    # msg_send = util.make_packet('data', 0, msg_send)
                    # self.sock.sendto(msg_send.encode("utf-8"), client_address)
                    self.clients.pop(client_address)


if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"
    WINDOW = 3

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW = a

    SERVER = Server(DEST, PORT, WINDOW)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
