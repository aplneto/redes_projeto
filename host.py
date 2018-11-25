#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo do Servidor de arquivos TCP

Esse módulo contém a implementação do objeto Host que controla o lado da
conexão do servidor.

Todo:
    * Implementar os Consoles múltiplos no método Host.start()
    * Terminar a finalização segura de conexão no método Host.end()
    * Terminar de listar os erros e tentar contornar o erro de porta em uso
    * Ajustar quando os terminais são deletados ao finalizar o console

Example:
    >> servidor = Host()
    >> servidor.start()
    
"""

import socket
import base64
from console import Console, makethread

class Host():
    """Classe do servidor que receberá os comandos e arquivos dos clientes
    
    Servidor TCP de armazenamento de arquivos. O servidor escuta na mesma porta
    por novas conexões, estabelecendo uma conexão de mão-dupla com o cliente.
    
    Attributes:
        HOST (str): valor padrão do servidor host para conexões locais
        PORT (int): valor de porta padrão para o servidor 4400
    
    Methods: run, stop
    
    Undocumented:
        backlog, backlog_setter, timeout, timeout_setter, running, start
        
    """
    HOST = "127.0.0.1"
    PORT = 4400
    def __init__(self, host_ip = HOST, port = PORT, root = "", **kwargs):
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
            dbuser (str): endeço alternativo para o banco de dados de
                usuários
            backlog (int): tamanho da fila de conexões não-aceitas.
            timeout (float): intervaloda busca por novas conexões do socket do
                servidor
        
        """
        self.host_name = (host_ip, port)
        self.root = root
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.bind(self.host_name)
        self.__run = False        
        self.__backlog = kwargs.get('backlog', 0)
        self.__timeout = kwargs.get('timeout', 0.5)
        try:
            self.usr_dict = Host.load_users(kwargs.get('usr.config',
                                                       'file_usr'))
        except FileNotFoundError:
            self.usr_dict = dict()
    
    @property
    def running(self):
        return self.__run
    
    @property
    def backlog(self):
        return self.__backlog
    
    @property
    def timeout(self):
        return self.__timeout
    
    @backlog.setter
    def backlog(self, integer):
        if type(integer) is not int:
            raise ValueError ("backlog deve ser inteiro")
        else:
            self.__backlog = integer
    
    @timeout.setter
    def timeout(self, long):
        if type(long) is int or type(long) is float:
            self.__timeout = float(long)
        else:
            raise ValueError ("timeout deve ser um número")

    @makethread
    def start(self):
        self.connection.listen(self.backlog)
        self.connection.settimeout(self.timeout)
        self.__run = True
        while self.__run:
            try:
                con, client = self.connection.accept()
            except socket.timeout:
                continue
            else:
                Host.Terminal(con, client, self).start()
        self.connection.close()                
    
    def stop(self):
        """Método usado para finalizar o servidor com segurança
        
        Finaliza o socket principal e inicia o processo de finalização dos
        terminais abertos.
        
        """
        self.__run = False
    
    def __repr__(self):
        return "{0}({1}, {2}, {3})".format(self.__class__.__name__,
                self.host_name[0].__repr__(), self.host_name[1],
                self.root.__repr__())
    
    def export_settings(self, filename):
        """Função para exportar as configurações do servidor para um arquivo
        
        As configurações são criptografadas com Base64 para evitar que usuários
        inexperientes percam seus dados.
        
        Args:
            filename (str): endereço do arquivo onde as configurações serão
                salvas
        
        """
        host_ip = "host_ip@{}".format(self.host_name[0])
        port = "port@{}".format(self.host_name[1])
        root = "root@{}".format(self.root)
        backlog = "backlog@{}".format(self.__backlog)
        timeout = "timeout@{}".format(self.__timeout)
        with open(filename, 'w') as file:
            file.write(base64.a85encode(host_ip.encode()).decode()+'\n')
            file.write(base64.a85encode(port.encode()).decode()+'\n')
            file.write(base64.a85encode(root.encode()).decode()+'\n')
            file.write(base64.a85encode(backlog.encode()).decode()+'\n')
            file.write(base64.a85encode(timeout.encode()).decode())

    @staticmethod
    def load_host(filename):
        """Função que carrega um host de um arquivo
        
        Essa função permite criar um novo objeto do tipo Host a partir de um
        arquivo que contenha as configurações salvas anteriormente.
        
        Args:
            filename (str): endereço do arquivo de configurações
        
        Returns:
            Host: objeto do tipo Host com as configurações salvas no arquivo.
        
        """
        configurations = dict()
        with open(filename, 'r') as file:
            code = file.readline()
            while code:
                line = base64.a85decode(code.encode()).decode()
                settings = line.split('@')
                configurations[settings[0]] = settings[1]
                code = file.readline()
        host_ip = configurations['host_ip']
        port = int(configurations['port'])
        root = configurations['root']
        backlog = int(configurations['backlog'])
        timeout = float(configurations['timeout'])
        return Host(host_ip, port, root, backlog = backlog, timeout = timeout)

    @staticmethod
    def save_users(dict_, filename):
        """Função para exportar os usuários de um servidor para um arquivo
        
        A função varre o dicionário de usuários que tem o seguinte formato:
            chaves: números inteiros que representam o hash das senhas de seus
                respectivos usuários
            valores: strings contendo os nomes de usuário
        Por fim, a função criptografa as strings usando Base64.
        
        Args:
            filename (str): endereço do arquivo onde os usuários serão salvos
        
        """
        with open(filename, 'w') as file:
            for h in dict_:
                str_ = '@'.join(dict_[h])
                str_ = str(h)+'@'+str_
                code = base64.a85encode(str_.encode())
                file.write(code.decode()+'\n')
    
    @staticmethod
    def load_users(fileusers):
        """Retorna um dicionário contendo como chaves o hash das senhas dos
        usuários e como valores os logins de cada um dos usuários.
        
        Args:
            fileusers (str): endereço do arquivo de usuários
        
        Returns:
            dict: dicionário contendo como chaves hash de senhas e valores os
                nomes de usuário
        """
        dict_usr = dict()
        with open(fileusers, 'r') as file:
            for line in file:
                info = base64.a85decode(line.encode())
                info = info.decode().split('@')
                dict_usr[int(info[0])] = tuple(info[1:])
        return dict_usr
    
    # Configuração da classe Host.Terminal abaixo

    class Terminal(Console):
        """Terminal do Servidor
        
        O terminal do servidor controla o acesso e autenticação dos usuários.
        Cada terminal é responsável pelo tratamento do acesso de um usuário
        individualmente.
        
        Attributes:
            CMD_DICT (dict): dicionário relacionando comandos e funções
        
        """
        def __init__(self, sock, client, host):
            """Método Construtor
            
            Args:
                sock (socket): sockete de comunicação com o cliente
                client (tuple): par IP/Porta de conexão com o cliente
                root (str): endereço da pasta raiz do servidor
            
            """
            Console.__init__(self, sock, client)
            self.host = host
        
        def run(self):
            """Fluxo de execução principal do Terminal
            
            As mensagens do Client são tratadas como comandos que são
            convertidos na execução de métodos do host. O objetivo do método
            __tratar é definir a qual método cada comando equivale.
            
            """
            self.send("Bem-vindo ao Servidor de arquivos TCPy")
            while True:
                try:
                    cmd = self.receive()
                    if cmd == "sair":
                        break
                    func = Host.Terminal.CMD_DICT.__getitem__(cmd)
                except KeyError:
                    self.send("comando_invalido")
                else:
                    func(self)
        
        def __sendhelp(self):
            """Método que envia para o usuário uma relação dos comandos
            
            Envia para o usuário uma lista dos comandos disponíveis seguida
            de uma breve descrição dos comandos.
            """
            self.send('help')

        def __login(self):
            """Método de autenticação do usuário
            
            Método pelo o qual o usuário autentica o acesso de uma conta já
            existente no servidor.
                        
            """            
            self.send("login")
            
            usr = self.receive()
            psw = int(self.receive())
            
            try:
                profile = self.host.usr_dict[psw]
            except KeyError:
                self.send("--0")
            else:
                if usr in profile:
                    self.usr = profile[0]
                    self.send("--1")
                else:
                    self.send("--0")
        
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
            
            Tenta se comunicar com o client, enviando uma mensagem para a
            finalização da conecção. Em seguida fecha e deleta o socket.
            """
            try:
                self.send("@end")
            except ConnectionResetError:
                pass
            finally:
                self.sock.close()
        
        CMD_DICT = {'login':__login, 'ajuda':__sendhelp, 'help':__sendhelp}

if __name__ == "__main__":
    servidor = Host()
    servidor.start()