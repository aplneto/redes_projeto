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

from console import Console, makethread
import base64
import pathlib
import os

COMMAND_DICT = {}

TERMINAL_HELP = {"conexões": "mostra quantas conexões estão ativas no momento",
                 "finalizar": "fecha o servidor para conexões futuras"}

HELP_DICT = {"sair" : "efetuar logoff e encerrar a execução do programa",
             "login": "efetuar login", "signup": "efetuar cadastro"}

class Host(Console):
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
            key_file (str): endereço do arquivo contendo a chave privada do
                servidor. Por padrão ".pvtkey.txt"
            file_usr (str): endeço do arquivo de texto contendo os usuários já
                cadastrados no servidor. Por padrão ".usr.txt"
        
        """
        Console.__init__(self)
        self.name = (host_ip, port)
        self.privatekey, self.publickey = Console.start_key(kwargs.get(
                'key_file', '.pvtkey.txt'))
        self.sock.bind(self.name)
        self.root = pathlib.Path(root)
        if not os.path.exists(root):
            self.root.mkdir()
        
        self.__run = False        
        
        try:
            self.usr_dict = Host.load_users(kwargs.get('file_usr',
                                                       '.usr.txt'))
        except FileNotFoundError:
            self.usr_dict = dict()
        
        self.__kwargs = kwargs
        
        self.client_count = 0

    @makethread
    def run(self, backlog = 0, timeout = 0.5):
        """Método de execução principal do servidor.
        
        Esse método coloca o servidor no modo de escuta, aceitando conexões de
        acordo com o backlog e timeout fornecidos como parâmetro.
        
        Args:
            backlog (int): tamanho da fila de conexões não-aceitas.
            timeout (float): intervaloda busca por novas conexões do socket do
                servidor
        
        """
        self.sock.settimeout(timeout)
        self.sock.listen(backlog)
        self.__run = True
        while self.__run:
            try:
                sock, client = self.sock.accept()
            except:
                pass
            else:
                print("Conexão estabelecida com: " + ', '.join(
                        str(x) for x in client))
                self.client_count += 1
                self.menu(sock)
    
    @makethread
    def menu(self, sock):
        """Menu principal de acesso de cada usuário
        
        Warnings:
            Atenção as funções anônimas desse método, estas são apenas ajustes
                nos métodos estáticos da classe Console.
                Para mais detalhes veja a documentação dos métodos receive e
                send na classe console.
        """
        sock.send(self.publickey)
        public_key = self.receive_key(sock)
        
        receive = lambda: Console.receive(sock, self.privatekey)
        send = lambda msg: Console.send(sock, public_key, msg)
        
        logged = False
        send("TCPy Server beta!\nFaça login ou cadastre-se para continuar.")
        while not logged:
            cmd = receive()
            if cmd == "sair":
                break
            elif cmd == "login":
                send("login")
            elif cmd == "signup":
                send("signup")
            elif cmd == "ajuda" or cmd == "help":
                for comando in HELP_DICT:
                    send(comando.__repr__() + ": " + HELP_DICT[comando])
                    tmp = receive()
                send('%end')
            else:
                send("Comando inválido!")
            
        sock.close()
        self.client_count -= 1
    
    def login(self, receive, send):
        """Método de Login
        
        Método que controla a rotina de login no servidor.
        
        Args:
            receive (function): função anônima responsável pelo recebimento de
                mensagens do cliente.
            send (function): função anônima responsável pelo envio de mensagens
                pelo socket do cliente.
        
        Returns:
            bool: True se o login for bem sucedido e False se não for.
        
        """
        raise NotImplemented
    
    def signup(self, receive, send):
        """Método de Cadastro
        
        Método que controla a rotina de cadastro no servidor, criando uma nova
        pasta para o usuário dentro da pasta root do servidor, assim como um
        relatório de banco de dados "files.bd" no interior da pasta.
        
        Args:
            receive (function): função anônima responsável pelo recebimento de
                mensagens do cliente.
            send (function): função anônima responsável pelo envio de mensagens
                pelo socket do cliente.
        
        """
        raise NotImplemented
    
    def start(self):
        """Método de controle do Servidor
        
        Funciona como um console para o servidor, onde o usuário digita os
        comandos e o servidor executa.
        """
        print("\nDigite 'help' ou 'ajuda' se precisar de ajuda.\n")
        while True:
            comando = input("\nadmin: ")
            
            if comando == "iniciar":
                self.run()
            elif comando == "conexões":
                print(self.client_count)
            elif comando == "sair":
                print("Finalizando servidor.")
                self.stop()
                break
            elif comando == "ajuda" or comando == "help":
                for cmd in TERMINAL_HELP:
                    print(cmd.__repr__() + ': ' + TERMINAL_HELP[cmd])
    
    def stop(self, **kwargs):
        """Método usado para finalizar o servidor com segurança
        
        Finaliza o socket principal e inicia o processo de finalização dos
        terminais abertos.
        
        Kwargs:
            file_usr (str): endereço do arquivo de texto onde os usuários serão
                salvos, 'usr.config' por padrão.
            file_config (str): endereço onde as configurações do host serão
                salvas, 'host.config' por padrão.
        """
        self.__run = False
        self.sock.close()
        
        self.export_settings(kwargs.get('file_config', 'host.config'))
        Host.save_users(self.usr_dict, kwargs.get('file_usr', 'usr.config'))
        
        key_file = open(self.__kwargs.get('key_file', '.pvtkey.txt'), 'wb')
        key_file.write(self.privatekey.exportKey())
        key_file.close()
    
    def export_settings(self, filename):
        """Função para exportar as configurações do servidor para um arquivo
        
        As configurações são criptografadas com Base64 para evitar que usuários
        inexperientes percam seus dados.
        
        Args:
            filename (str): endereço do arquivo onde as configurações serão
                salvas
        
        """
        host_ip = "host_ip@{}".format(self.name[0])
        port = "port@{}".format(self.name[1])
        root = "root@{}".format(self.root)
        
        with open(filename, 'w') as file:
            file.write(base64.a85encode(host_ip.encode()).decode()+'\n')
            file.write(base64.a85encode(port.encode()).decode()+'\n')
            file.write(base64.a85encode(root.encode()).decode()+'\n')
            for key in self.__kwargs:
                line = key + '@' + str(self.__kwargs[key])
                file.write(base64.a85encode(line.encode()).decode()+'\n')

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
        configurations['port'] = int(configurations['port'])
        return Host(**configurations)

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
                str_ = h+'@'+dict_[h]
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
                dict_usr[info[0]] = info[1]
        return dict_usr
    
    def __repr__(self):
        return ', '.join(["{0}({1}, {2}, {3})".format(self.__class__.__name__,
                self.name[0].__repr__(), self.name[1].__repr__(),
                self.root.name.__repr__(),  )]+[', '.join('{}: {}'.format
                        (x, self.__kwargs[x]) for x in self.__kwargs)])

if __name__ == "__main__":
    servidor = Host()
    servidor.start()