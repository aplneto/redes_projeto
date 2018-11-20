#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo do Servidor de arquivos TCP

Esse módulo contém a implementação do objeto Host que controla o lado da
conexão do servidor.

Attributes:
    COMANDOS (dict): dicionário de comandos do usuário

Todo:
    * Implementar os Consoles múltiplos no método Host.start()
    * Terminar a finalização segura de conexão no método Host.end()
    * Terminar de listar os erros e tentar contornar o erro de porta em uso
    
"""

import socket
from console import Console, make_thread
from userdatabase import DataBase

COMANDOS = dict()

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
    def __init__(self, host_ip = HOST, port = PORT, root = "./root", **kwargs):
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
            
        Kwargs:
            'dbuser' (str): endeço alternativo para o banco de dados de
                usuários
        
        """
        self.host_name = (host_ip, port)
        self.root = root
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.bind(self.host_name)
        self.__run = False        
        self.__databse = DataBase(kwargs.get('./root/database.bf', 'dbuser'))
        self.__clients = list()
            
    @make_thread
    def iniciar(self, backlog = 0, timeout = 0.5):
        """Método start abre o servidor para conexões
        
        Args:
            backlog (int): tamanho da fila de conexões não-aceitas.
            timeout (float): intervalo de busca de novas conexões do socket
                principal
        
        """
        self.connection.listen(backlog)
        self.connection.settimeout(timeout)
        self.__run = True
        while self.__run:
            try:
                con, client = self.connection.accept()
            except socket.timeout as timeout:
                continue
            else:
                self.__clients.append(Host.Terminal(con, client, self.root))
        self.connection.close()
    
    def finalizar(self):
        """Método usado para finalizar o servidor com segurança
        
        """
        self.__run = False
    
    def __repr__(self):
        return "{0}({1},{2},{3})".format(self.__class__.__name__,
                self.host_name[0].__repr__(), self.host_name[1],
                self.root.__repr__())
    
    class Terminal(Console):
        """Terminal do Servidor
        
        O terminal do servidor controla o acesso e autenticação dos usuários.
        Cada terminal é responsável pelo tratamento do acesso de um usuário
        individualmente.
        
        """
        def __init__(self, sock, client, root):
            """Método Construtor
            
            Args:
                sock (socket): sockete de comunicação com o cliente
                client (tuple): par IP/Porta de conexão com o cliente
                root (str): endereço da pasta raiz do servidor
            
            """
            Console.__init__(self, sock, client)
            self.root = root
            self.__logged = False
        
        def run(self):
            raise NotImplemented
        
        def __login(self, usr, psw):
            """Método de autenticação do usuário
            
            Método pelo o qual o usuário autentica o acesso de uma conta já
            existente no servidor.
            
            Args:
                usr (str): nome de usuário, único para cada usuário.
                psw (str): senha de acesso ao usuário
            
            Returns:
                bool: True se a autenticação for bem-sucedida e False se não
                    for
            
            """
            raise NotImplemented
        
        def __signin(self, usr, psw):
            """Método de criação de uma nova conta de usuário
            
            O método __signin é a rotina pela qual o usuário cria uma nova
            conta de acesso ao servidor.
            
            Args:
                usr (str): nome de usuário deve ser único para cada usuário.
                    Não é possível criar uma nova conta com um nome de usuário
                    já existente. Deve conter pelo menos três caracteres.
                psw (str): a senha deve conter pelo menos 8 caracteres e um
                    número inteiro.
            
            Raises:
                KeyError: se o nome de usuário já existir
                ValuError: se a senha ou nome de usuário não estiverem no
                    formato correto:
            
            Returns:
                bool: True se o cadastro for efetuado com sucesso.
            
            """
            raise NotImplemented
        
        def __signout(self):
            """Método de finalização segura do Terminal.
            
            """
            raise NotImplemented
        
        def shutdown(self):
            """Método de encerramento do Terminal.
            
            """