#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo do client

"""

from console import Console
import socket

class Client(Console):
    """Classe do objeto Cliente
    
    Cliente tcp do servidor de armazenamento de arquivos
    
    """
    def __init__(self, host_ip = "127.0.0.1", host_port = 4400):
        """Método construtor do cliente
        
        Inicia um socket em uma porta livre
        
        """
        Console.__init__(self,
                         socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                         (host_ip, host_port))
    
    def connect(self):
        """Método connect
        
        Abre uma conexão com o servidor de armazenamento de arquivos
        
        Args:
            host (str): endereço do servidor
            port (int): número de porta do servidor
        
        """
        self.sock.connect(self.client)
        self.active = True
        self.run()
        
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
                self.CMD_DICT.__getitem__(cmd)(self)
                
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
        if result == "1":
            self.usr = usr
        else:
            print("Nome de usuário ou senha incorretos! Tente novamente.")
    
    def __signin(self):
        """Rotina de cadastro de novo usuário
        
        """
        code = 1
        while code:
            usr = input("\nInsira o nome de usuário: ")
            self.send(usr)
            code = int(self.receive())
            if code:
                print("Nome de usuário já cadastrado.")
        psw = input("\nDigite sua senha: ")
        self.send(psw)
        print("Cadastro efetuado com sucesso")
        
    
    CMD_DICT = {'login':__login, 'help': show_help,
                'comando_invalido': __comando_invalido, "signin": __signin}

if __name__ == "__main__":
    cliente = Client()
    cliente.connect()
    cliente.run