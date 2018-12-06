#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo do client

"""

from console import Console
import os
import sys
import pathlib

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
    
    def __init__(self, host_ip = "localhost", host_port = 4400,
                 key_file = ".pvtkey.txt"):
        """Método construtor do cliente
        
        Inicia um socket em uma porta livre
        
        Args:
            host_ip (str): endereço de IP do servidor
            host_port (int): porta do servidor
            key_file (str): arquivo com as informações da cahve
        """
        Console.__init__(self, key_file = key_file)
        self.peer = (host_ip, host_port)
        self.usr = 'guest'
    
    def connect(self):
        """Método connect
        
        Abre uma conexão com o servidor de armazenamento de arquivos
        
        Args:
            host (str): endereço do servidor
            port (int): número de porta do servidor
        
        """
        try:
            self.sock.connect(self.peer)
        except ConnectionRefusedError:
            print("Erro!\nServidor indisponível.")
        else:
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
                self.__getattribute__(cmd[0])(*cmd[1:])
                del cmd
            except AttributeError:
                print(self.receive())
            except TypeError:
                print(self.receive())
        self.sock.close()
        print("Conexão Encerrada!")
    
    def show(self):
        msg = self.receive()
        while msg != "EOF":
            print(msg)
            self.send('ack')
            msg = self.receive()
    
    def share(self, usr):
        print(self.receive())
        
    def login(self, usr, psw):
        """Rotina de login
        
        """
        msg = self.receive()
        if msg == '1':
            self.usr = usr
            print("Seja bem-vindo, " + usr + ".")
        else:
            print(msg)
    
    def signup(self, usr, psw):
        """Rotina de cadastro
        
        """
        msg = self.receive()
        if msg == '1':
            print(usr + " cadastrado com sucesso.")
            self.send('ack')
            self.login(usr, psw)
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
    
    def post(self, file_address):
        """Método de post de arquivos diretamente no diretório do cliente
        
        Envia um arquivo através do método 
        """
        ack = self.receive()
        size = os.path.getsize(file_address)
        print("Enviando "+str(size)+" bytes")
        for b in self.send_file(file_address):
            sys.stdout.write('\r'+str(b)+" bytes enviados")
    
    def get(self, filename):
        """Método de get de arquivos do servidor
        
        """
        p = pathlib.Path(os.path.expanduser("~"))
        p = p.joinpath("Downloads").joinpath(filename)
        for b in self.receive_file(str(p)):
            sys.stdout.write('\r'+str(b)+" bytes recebidos")
        print(filename+' salvo em '+p)

    def delete(self, file):
        print(self.receive())
        
if __name__ == "__main__":
    cliente = Client()
    cliente.connect()