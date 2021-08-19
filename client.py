'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import math
import time
from queue import Queue
import util
import datetime

'''
Write your code inside this class.
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen
for incoming messages in this function.
'''
class Client:
    '''
    This is the main Client Class.
    '''
    def __init__(self, username, dest, port, window_size):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.name = username
        self.window = window_size
        self.size = 4096
        self.control = True
        self.ack = False
        self.message_packets = Queue(0)
        self.universal = False
        self.string_storage = ''
        self.ack_list = []
        self.curr_ack_num = 0
        self.curr_seq_num = 0
        # self.ackQueue = Queue(0)
        #############################
        self.ack_num_next = -1
        self.packet_correct = -1
        self.ack_gotten = -1
        self.ack_behji = -1
        # dict to store time of each packet
        self.time_of_each_packet = -1


    def print_help(self):
        '''addr'''
        print("message sending Input: msg <number_of_users> <username1> <username2> … <message>")
        print("accessing list Input: list")
        print("accessing list Input: list")
        print("file sending Input: file <number_of_users> <username1> <username2> … <file_name>")
        print("to quit Input: quit")

    def send_error(self):
        '''addr'''
        # print('disconnected: server received an unknown command')
        msg_send2 = util.make_message('garbage', 2,)
        msg_packet = util.make_packet('data', 0, msg_send2)
        msg_packet = msg_packet.encode('utf-8')
        self.sock.sendto(msg_packet,  (self.server_addr, self.server_port))
        self.control = False

    def check_error_msg(self, msg_list):
        '''addr'''
        check = True
        leng = len(msg_list)
        # num_of_users = int(msg_list[1])
        if leng == 1:
            # print('disconnected: server received an unknown command')
            check = False
        else:
            if msg_list[1] in ['1', '2', '3', '4' ,'5' ,'6' ,'7' , '8', '9']:
                check = True
            else:
                check = False
        if check is False:
            # print('disconnected: server received an unknown command')
            self.send_error()
        return check

    def sending_packet(self, type, seq_num, msg_to_send):
        '''addr'''
        msg_packet = util.make_packet(type, seq_num, msg_to_send)
        self.sock.sendto(msg_packet.encode('utf-8'),  (self.server_addr, self.server_port))


    def ack_timer_khatam(self, time_elapsed):
        ans = False
        if(datetime.datetime.now() - time_elapsed > datetime.timedelta(seconds = 0.5)):
            ans = True
            return ans
        else:
            ans = False
            return ans

    def start_sender(self, start_seq_num, msg_packet):

        ack_control = False
        while 1:
            if self.ack_num_next == start_seq_num + 1:
                break

            if ack_control is True:
                ack_control= False

            if self.ack_timer_khatam(self.time_of_each_packet):
                ack_control = True
                self.sock.sendto(msg_packet.encode('utf-8'), (self.server_addr, self.server_port))
                self.time_of_each_packet = datetime.datetime.now()

    def end_sender(self, last_seq_num, packet):
        ack_control = False
        while 1:

            if self.ack_num_next == last_seq_num:
                break

            if ack_control is True:
                ack_control= False

            if self.ack_timer_khatam(self.time_of_each_packet):
                ack_control = True
                self.sock.sendto(packet.encode('utf-8'), (self.server_addr, self.server_port))
                self.time_of_each_packet = datetime.datetime.now()

    def data_retranmission(self):
        temp_timer = False
        while not self.ack_timer_khatam(self.time_of_each_packet):

            if temp_timer is True:
                temp_timer = False

            if self.ack_num_next == self.ack_gotten + 1:
                temp_timer = True
                self.ack_gotten = self.ack_gotten + 1
                self.ack_num_next = -1
                break

    def data_transmission(self, last_seq_num, start_seq_num, chunks):
        '''and'''
        msg_control = False
        while self.ack_gotten != last_seq_num -1:
            if msg_control is False:
                msg_control= True

            i = self.ack_gotten - start_seq_num - 1
            # print("index:", index)
            packet = util.make_packet("data", self.ack_gotten, chunks[i])
            self.sock.sendto(packet.encode('utf-8'), (self.server_addr, self.server_port))
            self.time_of_each_packet  = datetime.datetime.now()
            self.data_retranmission()
            if msg_control is True:
                msg_control= False

    # client address is server address here
    def make_chunks(self, msg):
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

        self.ack_gotten = -1
        self.ack_num_next = -1

        msg_packet = util.make_packet('start', seq_num,)
        self.sock.sendto(msg_packet.encode('utf-8'), (self.server_addr, self.server_port))
        self.time_of_each_packet = datetime.datetime.now()

        self.start_sender(start_seq_num, msg_packet)


        self.ack_gotten = self.ack_num_next

        self.ack_num_next = -1

        self.data_transmission(last_seq_num, start_seq_num, chunks)

        # Create & Send End Packet + Record Timestamp
        packet = util.make_packet("end", last_seq_num - 1, "")
        self.sock.sendto(packet.encode('utf-8'), (self.server_addr, self.server_port))
        self.time_of_each_packet = datetime.datetime.now()

        self.end_sender(last_seq_num, packet)

        self.ack_num_next = -1
        self.ack_gotten = -1

    # were not using thsi
    def make_chunks2(self, msg):
        '''str'''
        #msg is string
        seq_num = random.randint(1, 100000)
        x_var = sys.getsizeof(msg)
        num_of_packets = math.ceil(x_var / util.CHUNK_SIZE)

        chunk_siz_chars=math.ceil(len(msg) / num_of_packets)
        # return num of characters taht should be in each packet
        chunks = [msg[i:i+ chunk_siz_chars] for i in range(0, len(msg), chunk_siz_chars)]
        # list of packet content
        packet_queue = Queue(0)
        num = seq_num + 1

        # making start packet
        msg_packet = util.make_packet('start', seq_num, )
        packet_queue.put(msg_packet)
        # self.sock.sendto(msg_packet.encode('utf-8'),  (self.server_addr, self.server_port))
        # time.sleep(0.5)

        '''while self.ack == False:
            self.sock.sendto(msg_packet.encode('utf-8'),  (self.server_addr, self.server_port))
            time.sleep(0.5)
        self.ack = False'''

        for chunk in chunks:
        # for chunk in chunks[1: len(chunks) - 1]:
            msg_packet1 = util.make_packet('data', num, chunk)
            packet_queue.put(msg_packet1)
            num = num + 1

        msg_packet2 = util.make_packet('end', num,)
        packet_queue.put(msg_packet2)

        while packet_queue.empty() is False:
            packet = packet_queue.get()
            # print("thsi,   ", packet)
            _msg_type, seq_num1, _str_msg, _check_sum = util.parse_packet(packet)
            self.curr_seq_num = int(seq_num1)
            self.sock.sendto(packet.encode('utf-8'),  (self.server_addr, self.server_port))
            time.sleep(0.5)

            if self.ack is False:
                while self.ack is False:
                    self.sock.sendto(packet.encode('utf-8'),  (self.server_addr, self.server_port))
                    time.sleep(0.5)
                self.ack = False
            else:
               self.ack = False



    def start(self):
        '''
        Main Loop is here
        Start by sending the server a JOIN message.
        Waits for userinput and then process it
        '''
        user_name = util.make_message('join', 1, self.name)
        self.make_chunks(user_name)

        while self.control:
            msg_send = input()
            # print(msg_send)
            list_msg = msg_send.split()
            # print(list_msg[-1])
            length = len(list_msg)

            if length > 1 and list_msg[0] in ['list', 'quit', 'help']:
                print('disconnected: server received an unknown command')
                self.send_error()
                self.control = False
                break
            elif list_msg[0] == 'list':
                msg_send2 = util.make_message('request_users_list', 2,)
                self.make_chunks(msg_send2)

            elif list_msg[0] == 'msg':
                if self.check_error_msg(list_msg):
                    msg_send2 = util.make_message('send_message', 4 , msg_send)
                    self.make_chunks(msg_send2)
                else:
                    print('disconnected: server received an unknown command')
                    self.control = False
                    break
            elif list_msg[0] == 'help':
                self.print_help()
            elif list_msg[0] == 'quit':
                print('quitting')
                msg_send2 = util.make_message('disconnect', 1 , self.name)
                self.make_chunks(msg_send2)
                self.control = False
                self.sock.close()
                sys.exit()
                break
            elif list_msg[0] == 'file':
                if self.check_error_msg(list_msg):
                    file1 = open(list_msg[-1], "r")
                    file_content = file1.read()
                    file_send = ' '.join(list_msg)
                    msg_send = file_send + '\n' + file_content
                    msg_send2 = util.make_message('send_file', 4 , msg_send)
                    self.make_chunks(msg_send2)
                else:
                    print('disconnected: server received an unknown command')
                    self.control = False
                    break
            else:
                print('incorrect userinput format')

    def start_manage(self, client_addr, seq_num):
        self.message_packets = Queue(0)
        # put next ack num in ack dict
        self.ack_behji = seq_num + 1

        seq_num_send = self.ack_behji
        #send ack
        util.msg_sender(self.sock, client_addr, seq_num_send)

    def packet_type_manager(self, message_packet, client_addr):
        # message is a packet
        '''addr'''
        # self.client_msg_list[client_addr].put(message_packet)
        # get the top ele in queue if it is wrong no send ack if right the
        # concatinate to string and store string in dict
        recv_msg = ''
        end_recv = False
        msg_type, seq_num, _str_msg, _check_sum = util.msg_decoder(message_packet)
        seq_num = int(seq_num)
        if msg_type == 'ack':
            self.ack_num_next = seq_num

        elif msg_type == 'start':
            # self.client_msg_list[client_addr].put(message_packet)
            # if client_addr not in self.client_msg_list.keys():
            # new message by person new queue
            self.start_manage(client_addr, seq_num)

        elif msg_type == 'data':
            if self.ack_behji == seq_num:
                self.message_packets.put(message_packet)
                # update current ack num
                num = seq_num + 1
                self.ack_behji = num
                #sends ack
            util.msg_sender(self.sock, client_addr, self.ack_behji)

        elif msg_type == 'end':
           # self.universal = True
            if self.ack_behji== seq_num:
                # recv_msg = ''

                while 1:
                    if self.message_packets.empty():
                        break
                    else:
                        msg_type, _seq_num, str_msg, _check_sum = util.msg_decoder(self.message_packets.get())
                        recv_msg =  recv_msg + str_msg

                num = self.ack_behji + 1
                util.msg_sender(self.sock, client_addr, num)
                end_recv = True
                return recv_msg
            else:
                util.msg_sender(self.sock, client_addr, self.ack_behji)

        if end_recv == False:
            return " "
        else:
            return recv_msg



    def packet_reciver1(self, c_decoded_packet):

        msg_type, _seq_num, _str_msg, _check_sum = util.msg_decoder(c_decoded_packet)
        if msg_type == 'ack':
            return
        #get the top ele in queue if it is wrong no send ack if right the
        # concatinate to string and store string in dict
        if msg_type == 'start':
            if self.message_packets.empty() is True:
                self.message_packets.put(c_decoded_packet)
                #send ack
                # util.msg_sender(self.sock, client_addr)
        elif msg_type == 'data':
            self.message_packets.put(c_decoded_packet)
            #send ack
            # util.msg_sender(self.sock, client_addr)
        elif msg_type == 'end':
            self.message_packets.put(c_decoded_packet)
            self.universal = True
            #send ack
            # util.msg_sender(self.sock, client_addr)

        '''msg_type, _seq_num, str_msg, _check_sum = util.msg_decoder(c_decoded_packet)
        print(str_msg)
        # m_type, s_no, data, sum = util.parse_packet(c_decoded_packet)
        self.message_packets.put(c_decoded_packet)
        if msg_type == 'end':
            self.universal = True
        return'''
        return

    def process_acks(self, packet):
        # print("packet is ", packet)
        _msg_type, seq_num, _str_msg, _check_sum = util.msg_decoder(packet)
        self.ack_seq_num = int(seq_num)
        if int(seq_num) == self.curr_seq_num + 1:
            return True
        else:
            return False

    def receive_handler(self):
        '''
        Waits for a message from server and process it accordingly
        '''
        while self.control:
            message, _ = self.sock.recvfrom(self.size)
            message1 = message
            message = message.decode("utf-8")
            _pac_type, _seq_num, _recv_msg, _check_sum = util.parse_packet(message)

            recv = self.packet_type_manager(message1, (self.server_addr, self.server_port) )

            if recv != ' ':

                message_list = recv.split(" ")
                message_type = message_list[0]
                # print(message_List)
                line_list = recv.split('\n')
                # print("look  ", line_list)

                if message_type == 'response_users_list':
                    user_list = message_list[2:]
                    user_list2 = ' '.join(user_list)
                    print("list:", user_list2)
                elif message_type == 'err_server_full':
                    print("disconnected: server full")
                    self.control = False
                    self.sock.close()
                    sys.exit()
                    break
                elif message_type == 'err_username_unavailable':
                    print("disconnected: username not availablel")
                    self.control = False
                    self.sock.close()
                    sys.exit()
                    break
                elif message_type == 'forward_message':
                    msg = message_list[2:]
                    msg2 = ' '.join(msg)
                    msg3 = 'msg: ' + msg2
                    print(msg3)
                elif message_type == 'err_unknown_message':
                    print('disconnected: server received an unknown command')
                    self.control = False
                    self.sock.close()
                    sys.exit()
                    break
                elif message_type == 'forward_file':
                    print_statement = 'file: ' + message_list[2] +' '+ message_list[3]
                    print(print_statement)
                    name_f = self.name +'_' + message_list[3]
                    stuff_write_file = line_list[1:]
                    str_msg2 = '\n'.join(stuff_write_file)
                    file1 = open(name_f, "w")
                    file1.write(str_msg2)
                    file1.close()



# Do not change this part of code
if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=","window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    WINDOW_SIZE = 3
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW_SIZE = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT, WINDOW_SIZE)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
