#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo do client

"""

from console import Console
import socket

class Client(object):
    """Classe do objeto Cliente
    
    Cliente tcp do servidor de armazenamento de arquivos
    
    """
    def __init__(self):
        """Método construtor do cliente
        
        Inicia um socket em uma porta livre
        
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active = False
        self.terminal = None
    
    def conectar(self, host = "127.0.0.1", port = 4400):
        """Método conectar
        
        Abre uma conexão com o servidor de armazenamento de arquivos
        
        Args:
            host (str): endereço do servidor
            port (int): número de porta do servidor
        
        """
        self.sock.connect((host, port))
        self.active = True
        self.terminal = Client.Terminal(self.sock, (host, port))
        self.terminal.start()
    
    class Terminal(Console):
        """Classe do terminal do cliente
        
        """
        def __init__(self, sock, host):
            Console.__init__(self, sock, host)
            self.usr = ""
        
        def run(self):
            while True:
                mensagem = input()
                self.enviar_str(mensagem)
                output = self.sock.recv(1024)
                output = output.decode()
                print(output)
                if mensagem == "terminate":
                    self.sock.close()
                    print("Conexão encerrada!")
                    break
        
        def login(self):
            pass
            