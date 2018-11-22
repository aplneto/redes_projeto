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
        
        Attributes:
            CMD_DICT (dict): Dicionário que associa os comandos recebidos do
            servidor com os métodos do objeto Terminal.
        
        """        
        def __init__(self, sock, host):
            Console.__init__(self, sock, host)
            self.usr = ""
        
        def run(self):
            mensagem = self.sock.recv(1024)
            print("Digite 'help' ou 'ajuda' se precisar de ajuda.\n")
            print(mensagem.decode())
            while True:
                mensagem = input("Eu: ")
                self.sock.send(mensagem.encode())
                mensagem = self.sock.recv(1024)
                self.__tratar(mensagem.decode())
        
        def __tratar(self, mensagem):
            """Método para tratar as mensagens recebidas do servidor
            
            Args:
                Mensagem (str): mensagem com comandos recebidas do servidor
            
            """
            try:
                mtd = Client.Terminal.CMD_DICT.__getitem__(mensagem)
            except KeyError:
                print(mensagem)
            else:
                mtd(self)
        
        def ajuda(self):
            """Comando para o recebimento e impressão das mensagens de ajuda
            
            """
            print(self.sock.recv(1024).decode())
        
        CMD_DICT = {'--help':ajuda}