#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo de configuração dos consoles

"""

import threading

def make_thread(func):
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

@make_thread
def printer(sock):
    """Método de impressão das informações recebidas
    
    Método que controla as informações recebidas
    
    """
    while True:
        mensagem = sock.recv(1024)
        mensagem = mensagem.decode()
        if not mensagem:
            sock.close()
            print("Conexão Encerrada")
            break
        with threading.Lock():
            print(mensagem)
            sock.send("recebido".encode())

class Console(threading.Thread):
    """Superclasse Console
    
    Classe base para os terminais de cliente e servidor.
    
    """
    def __init__(self, sock, cliente):
        """Método construtor do console
        
        Args:
            conexao (socket): socket de comunicação entre cliente e servidor
            client (tuple): tupla contendo os valores de ip e porta do cliente
        
        """
        threading.Thread.__init__(self)
        self.sock = sock #: novo socket
        self.client = cliente
    
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
    
    def enviar_str(self, msg):
        """Método enviar_str envia mensagens simples através do socket
        
        O Método enviar_str é o método usado apara enviar mensagens simples
        através de um socket.
        
        Todo:
            * Inserir a criptografia no envio de mensagens
        
        """
        msg = msg.encode()
        self.sock.send(msg)
    
    def __repr__(self):
        return "{0}({1}, {2})".format(self.__class__.__name__,
                self.sock.__repr__(), self.client.__repr__())