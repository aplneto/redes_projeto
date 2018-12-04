#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo do client

"""

from console import Console

class Client(Console):
    """Classe do objeto Cliente
    
    Cliente tcp do servidor de armazenamento de arquivos
    
    Attributes:
        CMD_DICT (dict): dicionário de comandos do cliente
    
    Methods:
        pass
    
    Undocumented:
        receive_key, receive, send
    """
    CMD_DICT = {}
    
    def __init__(self, host_ip = "127.0.0.1", host_port = 4400,
                 key_file = ".pvtkey.txt"):
        """Método construtor do cliente
        
        Inicia um socket em uma porta livre
        
        Args:
            host_ip (str): endereço de IP do servidor
            host_port (int): porta do servidor
            key_file (str): arquivo com as informações da cahve
        """
        Console.__init__(self)
        self.peer = (host_ip, host_port)
        self.privatekey, self.publickey = Console.start_key(key_file)
        self.usr = 'guest'

    def receive(self):
        return Console.receive(self.sock, self.privatekey)
    
    def receive_key(self):
        return Console.receive_key(self.sock)
    
    def send(self, msg):
        Console.send(self.sock, self.publickey, msg)
    
    def connect(self):
        """Método connect
        
        Abre uma conexão com o servidor de armazenamento de arquivos
        
        Args:
            host (str): endereço do servidor
            port (int): número de porta do servidor
        
        """
        self.sock.connect(self.peer)
        self.active = True
        tmp = self.publickey
        self.publickey = self.receive_key()
        self.sock.send(tmp)
        self.run()
        
    def run(self):
        """Fluxo de execução do programa do cliente
        
        A cada comando enviado pelo cliente, este aguarda uma resposta do
        servidor. Todas as respostas possíveis do servidor constam no
        dicionário de comandos do Terminal.
        
        """
        print("Conexão Estabelecida com " + str(self.peer[0]))
        print("\nDigite 'ajuda' para aprender sobre os comandos disponíveis.")
        print('\n'+self.receive())
        while True:
            msg = input('\n'+self.usr+": ")
            self.send(msg)
            cmd = msg.split(' ')
            if cmd[0] == 'sair':
                break
            try:
                self.__getattribute__(cmd[0])()
            except AttributeError:
                print(self.receive())
        self.sock.close()
        print("Conexão Encerrada!")
    
    def login(self):
        """Rotina de login
        
        """
        msg = self.receive()
        if msg == '1':
            self.send('1')
            self.usr = self.receive()
        else:
            print(msg)
    
    def signup(self):
        """Rotina de cadastro
        
        """
        msg = self.receive()
        if msg == '1':
            self.login()
        else:
            print(msg)
    
    def ajuda(self):
        """Rotina de recebimento de ajuda
        
        """
        msg = self.receive()
        while msg != '0':
            print(msg)
            self.send('ok')
            msg = self.receive()
            

if __name__ == "__main__":
    cliente = Client()
    cliente.connect()