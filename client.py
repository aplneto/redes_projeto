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
    def __init__(self, host_ip = "127.0.0.1", host_port = 4400):
        """Método construtor do cliente
        
        Inicia um socket em uma porta livre
        
        """
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__host = (host_ip, host_port)
        self.terminal = None
    
    def connect(self):
        """Método connect
        
        Abre uma conexão com o servidor de armazenamento de arquivos
        
        Args:
            host (str): endereço do servidor
            port (int): número de porta do servidor
        
        """
        self.__sock.connect(self.__host)
        self.active = True
        self.terminal = Client.Terminal(self.__sock, self.__sock.getsockname())
        self.terminal.start()
    
    # Client.Terminal
    
    class Terminal(Console):
        """Classe do terminal do cliente
        
        Attributes:
            CMD_DICT (dict): Dicionário que associa os comandos recebidos do
            servidor com os métodos do objeto Terminal.
        
        """        
        def __init__(self, sock, client):
            Console.__init__(self, sock, client)
        
        def run(self):
            """Fluxo de execução do programa do cliente
            
            A cada comando enviado pelo cliente, este aguarda uma resposta do
            servidor. Todas as respostas possíveis do servidor constam no
            dicionário de comandos do Terminal.
            
            """
            print("Digite 'help' ou 'ajuda' se precisar de ajuda.\n")
            print(self.receive())
            while True:
                msg = input("\n{0}: ".format(self.usr))
                self.send(msg)                
                if msg == "sair":
                    break                    
                cmd = self.receive()
                if cmd == "@end":
                    break
                else:
                    Client.Terminal.CMD_DICT.__getitem__(cmd)(self)
                    
            self.sock.close()
            print("Até mais!")
        
        def __comando_invalido(self):
            """Imrpime na tela uma mensagem de erro simples
            
            """
            print("Comando inválido")

        def show_help(self):
            """Função para imprimir na tela ajuda com o menu
            
            """
            print("\n'sair': finaliza a execução do cliente")
            print("'login': faz login numa conta existente")
            print("'signup': cadastra uma nova conta no servidor")
            if self.usr != "guest":
                pass # Acrescentar a ajuda das funções depois do login
        
        def __login(self):
            """Rotina de login do usuário
            
            """
            usr = input("\nlogin: ")
            self.send(usr)
            psw = input("senha: ")
            self.send(psw)
            result = self.receive()
            if result == "--1":
                self.usr = self.receive()
            else:
                print("Nome de usuário ou senha incorretos! Tente novamente.")
        
        CMD_DICT = {'login':__login, 'help': show_help,
                    'comando_invalido': __comando_invalido}

if __name__ == "__main__":
    cliente = Client()
    cliente.connect()