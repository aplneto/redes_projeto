#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script do client
"""

from console import make_thread
import socket
import threading

class Client(object):
    """Classe do objeto Cliente
    
    Cliente tcp do servidor de armazenamento de arquivos
    
    """
    def __init__(self):
        """Método construtor do cliente
        
        Inicia um socket em uma porta livre
        
        """
        self.__tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__active = False
    
    def conectar(self, host = "127.0.0.1", port = 4400):
        """Método conectar
        
        Abre uma conexão com o servidor de armazenamento de arquivos
        
        Args:
            host (str): endereço do servidor
            port (int): número de porta do servidor
        
        """
        self.__tcp.connect((host, port))
        self.__active = True