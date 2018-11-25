#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo de configuração dos consoles

"""

import threading

def makethread(func):
    """Função que transforma uma função qualquer numa Thread
    
    Args:
        func (function): função a ser transformada em Thread
    
    """
    def _thread(*args, **kwargs):
        """Decorador interno da função
        
        Args:
            *args (tuple): tupla de argumentos da função
            **kwargs (dict): dicionários de palavras-chave da função
        
        """
        pcs = threading.Thread(target = func, args = args, kwargs = kwargs)
        pcs.start()
    return _thread

class Console(threading.Thread):
    """Superclasse Console
    
    Classe base para os terminais de cliente e servidor.
    
    Attributes:
        logged (bool): True caso o usuário tenha realizado o login com sucesso,
            False caso contrário
    
    """
    def __init__(self, socket, client):
        """Método construtor do console
        
        Args:
            socket (socket): socket de comunicação entre cliente e servidor
            client (tuple): tupla contendo os valores de ip e porta do cliente
        
        """
        threading.Thread.__init__(self)
        self.sock = socket
        self.client = client
        self.usr = "guest"
    
    def run(self):
        """Método run difere entre o Console do Host e o do Client
        
        O Método run controla o comportamento da Thread como um todo, é o
        método executado uma vez que o método Console.start() é chamado.
        Todo o comportamento de um console individual deve ser definido dentro
        do método run.
        
        Example:
            Para observar o comportamento básico de uma dessas threads, veja a
            função printer.
        
        """
        raise NotImplemented
    
    def decrypt(self, msg):
        raise NotImplemented
    
    def encrypt(self, msg):
        raise NotImplemented
    
    def send(self, msg):
        """Método send envia strings simples através do socket
        
        O Método send é o método usado apara enviar mensagens simples através
        de um socket. Dentro desse método ocorrem as criptografias RSA e base64
        antes do envio."
        
        Args:
            msg (str): mensagem a ser enviada
        
        """
        self.sock.send(msg.encode())
    
    def receive(self):
        """Método receive recebe mensagens simples através do socket
        
        É através desse método que o usuário recebe mensagens simples através
        do socket. As mensagens chegam criptografadas e a descriptografia
        acontece dentro do método receive.
        
        Returns:
            (str) mensagem legível e decifrada
        
        """
        msg = self.sock.recv(1024)
        return msg.decode()
    
    def upload(self, file):
        """
        """
        raise NotImplemented
    
    def download(self):
        """
        """
        raise NotImplemented
        
    def __tratar(self, mensagem):
        """Método de tratamento das strings recebidas
        
        As strings recebidas podem ser mensagens a ser impressas ou comandos
        a serem recebidos e convertidos em métodos do objeto. Como cada objeto
        possui seu próprio dicionário de comandos, esse método deve ser
        implementado em cada uma das implementações dos terminais de Host e
        Client.
        
        Args:
            mensagem (str): mensagem recebida
        
        """
        raise NotImplemented
    
    def __repr__(self):
        return "{0}({1}, {2})".format(self.__class__.__name__,
                self.sock.__repr__(), self.client.__repr__())