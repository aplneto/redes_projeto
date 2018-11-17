#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script do client
"""

import socket

class Client(object):
    def __init__(self):
        '''
        :param host: IP do cliente, definido como 127.0.0.1 para conexões locais
        '''
        self.__tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def conectar(self, host = "127.0.0.1", port = 4400):
        self.__tcp.connect((host, port))

if __name__ == "__main__":
    me = Client()
    me.conectar()