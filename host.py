#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo do Servidor de arquivos TCP

Esse módulo contém a implementação do objeto Host que controla o lado da
conexão do servidor.

Attributes:
    pass

Todo:
    * Implementar os Consoles múltiplos no método Host.start()
    * Terminar a finalização segura de conexão no método Host.end()
    * Terminar de listar os erros e tentar contornar o erro de porta em uso
"""

import pathlib
import socket
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

class Host(object):
    """Classe do servidor que receberá os comandos e arquivos dos clientes
    
    Servidor TCP de armazenamento de arquivos. O servidor escuta na mesma porta
    por novas conexões, estabelecendo uma conexão de mão-dupla com o cliente.
    
    Attributes:
        HOST (str): valor padrão do servidor host para conexões locais
        PORT (int): valor de porta padrão para o servidor 4400
        
    """
    HOST = "127.0.0.1"
    PORT = 4400
    def __init__(self, host_ip = HOST, port = PORT, root = "./root", **kwagrs):
        """Método construdor do Host
        
        O Host é configurado através de um ip, um valor de porta e um diretório
        onde os arquivos dos usuários serão armazenados.
        
        Args:
            host_ip (str): IP do Host, configurado por padrão para coneões
                locais '127.0.0.1'
            port (int): valor de porta para conexão com o servidor, por padrão
                4400
            root (str): caminho para o diretório raiz onde os arquivos dos
                usuários serão salvos, sendo './root' por padrão
        
        """
        self.__host_name = (host_ip, port)
        self.__root = pathlib.Path(root)
        self.__connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connection.bind(self.__host_name)
            
    @make_thread
    def start(self, backlog):
        """Método start abre o servidor para conexões
        
        Args:
            backlog (int): número de conexões não aceitas permitidas antes do
                sistema recusar novas conexões.
            
        """
        self.__connection.listen(backlog)
        while True:
            con, client = self.__connection.accept()
            while True:
                mensagem = con.recv(1024)
                print(mensagem)
    
    def end(self):
        """Método usado para finalizar o servidor com segurança
        """
        self.__connection.close()
            
    class Console(threading.Thread):
        """Classe auxiliar Console permite conexões simultâneas
        
        Cada objeto Console é reposnável por tratar a conexão com um client
        individualmente.
        É necessário autenticação, antes que o cliente tenha acesso a qualquer
        comando. Esta autenticação é feita através do método __login.
        
        """
        def __init__(self, conexao, cliente):
            threading.Thread.__init__(self)
            self.__comm = conexao #: novo socket
            self.__client = cliente
            self.__usr = ''
        
        def run (self):
            logged = False
            while not logged:
                self.__login()
        
        def __login(self):
            pass
        