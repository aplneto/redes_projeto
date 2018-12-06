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

from console import Console
import base64
import pathlib
import os
import threading
import ntpath
import datetime

# Dicionário que armazenará os usuários cadastrados
USR_DICT = dict()

# Dicionário de ajuda do terminal
TERMINAL_HELP = {"conexões": "mostra quantas conexões estão ativas no momento",
                 "finalizar": "fecha o servidor para conexões futuras e "+
                 "sai do menu",
                 "iniciar": "abre o servidor para novas conexões"}

# Dicionário de ajuda pré-login
HELP_DICT = {"sair" : "efetuar logoff e encerrar a execução do programa",
             "login <usr> <psw>": "efetuar login usando o valor de <usr>"
             + " e <psw> como senha",
             "signup <usr> <psw>": "efetua cadastro como <usr>" +
             " usando <psw> como senha"}

# Dicionário de comandos principais
MENU_DICT = {'post <file>': 'faz o upload de um arquivo para o servidor',
             'get <file>': 'faz o download de um arquivo do servidor',
             'put <file>': 'faz upload da versão mais recente de um arquivo',
             'share <file> <usr>': 'compartilha um arquivo com um usuário',
             'show': 'lista todos os arquivos disponíveis'}

CLIENT_COUNTER = 0
CLIENT_LIST = list()

# Funções Auxlilares

def makethread(func):
    """Função que transforma uma função qualquer numa Thread
    
    Args:
        func (function): função a ser transformada em Thread
    
    Returns:
        (function) wrapper da função a ser transformada em thread
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

# Classe Principal do Servidor

class Host(Console, threading.Thread):
    """Classe do servidor que receberá os comandos e arquivos dos clientes
    
    Servidor TCP de armazenamento de arquivos. O servidor escuta na mesma porta
    por novas conexões, estabelecendo uma conexão de mão-dupla com o cliente.
    
    Attributes:
        HOST (str): valor padrão do servidor host para conexões locais
            'localhost'
        PORT (int): valor de porta padrão para o servidor 4400
        
    """
    HOST = "localhost"
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
        Console.__init__(self, key_file = kwargs.get('key_file',
                                                     '.pvtkey.txt'))
        threading.Thread.__init__(self)
        self.host_name = (host_ip, port)
        self.sock.bind(self.host_name)
        
        self.root = pathlib.Path(root)
        if not os.path.exists(root):
            self.root.mkdir()
        
        try:
            usr_dict = Host.load_users(kwargs.get('file_usr',
                                                       '.usr.txt'))
        except FileNotFoundError:
            usr_dict = dict()
        
        finally:
            USR_DICT.update(usr_dict)
        
        self.__kwargs = kwargs
        self.__run = False

    def run(self, backlog = 0, timeout = 0.5):
        """Método de execução principal do servidor.
        
        Esse método coloca o servidor no modo de escuta, aceitando conexões de
        acordo com o backlog e timeout fornecidos como parâmetro.
        
        Args:
            backlog (int): tamanho da fila de conexões não-aceitas.
            timeout (float): intervaloda busca por novas conexões do socket do
                servidor
        
        """
        global CLIENT_COUNTER
        self.sock.settimeout(timeout)
        self.sock.listen(backlog)
        self.__run = True
        print("Aguardando conexões...")
        while self.__run:
            try:
                sock, client = self.sock.accept()
            except:
                pass
            else:
                print("Conexão estabelecida com: " + ', '.join(
                        str(x) for x in client))
                CLIENT_COUNTER += 1
                tmp = ClientHandler(sock, client, self.publickey, self.privatekey,
                                    self.root)
                tmp.start()
                CLIENT_LIST.append(tmp)
    
    @staticmethod
    def Menu(host):
        """Método de controle de Servidores
        
        Funciona como um console para o servidor, onde o usuário digita os
        comandos e o servidor executa.
        """
        global CLIENT_COUNTER
        running = False
        
        print("\nDigite 'help' ou 'ajuda' se precisar de ajuda.\n")
        while True:
            comando = input("\nadmin: ")
            
            if comando == "iniciar":
                if running:
                    print("Servidor já em execução!")
                else:
                    host.start()
            elif comando == "conexões":
                print(CLIENT_COUNTER)
            elif comando == "finalizar":
                print("Finalizando servidor.")
                host.stop()
                running = False
                break
            elif comando == "clientes":
                for h in CLIENT_LIST:
                    print(h.usr)
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
        
        self.export_settings(kwargs.get('file_config', '.host.txt'))
        Host.save_users(USR_DICT, kwargs.get('file_usr', '.usr.txt'))
        
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
        host_ip = "host_ip@{}".format(self.host_name[0])
        port = "port@{}".format(self.host_name[1])
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
            (Host) objeto do tipo Host com as configurações salvas no arquivo.
        
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
            (dict) dicionário contendo como chaves hash de senhas e valores os
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
                self.host_name[0].__repr__(), self.host_name[1].__repr__(),
                self.root.name.__repr__(),  )]+[', '.join('{}: {}'.format
                        (x,
                         self.__kwargs[x].__repr__()) for x in self.__kwargs)])

# Classe auxiliar do Servidor

class ClientHandler(Console, threading.Thread):
    def __init__(self, socket, client, publickey, privatekey, root):
        """Método construtor do ajudante
        
        Esse método realiza a troca de chaves com o cliente.
        
        Args:
            socket (socke.socket): socket pelo qual a comunicação acontecerá
            publickey (bytes): inicializador da chave pública (fornecido pelo
                Host)
            root (pathlib.Path):
        """
        Console.__init__(self, sock = socket)
        threading.Thread.__init__(self)
        self.client = client
        self.privatekey = privatekey
        self.sock.send(publickey)
        self.publickey = self.receive_key()
        self.root = self.directory = root
        self.usr_bd = dict()
        self.running = True
        self.usr = 'guest'

    def run(self):
        """Processo principal da Thread do Handler
        
        """
        global CLIENT_COUNTER
        
        self.send("TCPy Server\nFaça login ou cadastre-se para continuar.")
        while True:
            msg = self.receive()
            cmd = msg.split(' ')
            if cmd[0] == "sair":
                break
            try:
                self.__getattribute__(cmd[0])(*cmd[1:])
                del cmd
            except TypeError:
                self.send("Parâmetros incorretos!\nUse o comando 'ajuda'" +
                          " para mais informações!")
            except AttributeError:
                self.send("Comando inválido!")
        self.sock.close()
        CLIENT_COUNTER -= 1
        self.running = False
    
    def ajuda(self):
        """ Método de envio de ajuda do servidor.
        
        """
        if self.usr == 'guest':
            for key in HELP_DICT:
                msg = key.__repr__() + ': ' + HELP_DICT[key]
                self.send(msg)
                ack = self.receive()
            self.send('0')
        else:
            for key in MENU_DICT:
                msg = key.__repr__() + ': ' + MENU_DICT[key]
                self.send(msg)
                ack = self.receive()
            self.send('0')
            
    def login(self, usr, psw):
        """Método de Login
        
        Método que controla a rotina de login no servidor.
        
        Args:
            usr (str): nome de usuário para tentativa de acesso
            psw (str): senha do usuário
        
        """
        if self.usr == 'guest':
            if usr in USR_DICT:
                if USR_DICT[usr] == psw:
                    self.usr = usr
                    self.send('1')
                    self.directory = self.root.joinpath(usr)
                    self.usr_bd.update(
                            self.recover_bdfile(
                                    str(self.directory.joinpath(usr+'.bd'))))
                    print(self.usr + 'efetuou login de' + str(self.client))
                else:
                    self.send("Senha incorreta!")
            else:
                self.send("Nome de usuário desconhecido!")
        else:
            self.send("Comando inválido!")
    
    def logout(self):
        """Método de Logout
        
        Warnings:
            Incompleto
        """
        usr = self.usr
        self.usr = 'guest'
        del self.directory
        self.directory = self.root
        del self.usr_bd
        self.usr_bd = dict()
        self.send("Até mais " + usr + ".")
    
    def signup(self, usr, psw):
        """Método de Cadastro
        
        Método que controla a rotina de cadastro no servidor, criando uma nova
        pasta para o usuário dentro da pasta root do servidor, assim como um
        relatório de banco de dados "files.bd" no interior da pasta.
        
        Args:
            usr (str): nome de usuário a ser cadastrado deve ser único
            psw (str): senha de acesso do usuário
            
        """
        if self.usr == 'guest':
            if usr in USR_DICT:
                self.send("Usuário já cadastrado")
            else:
                self.send("1")
                USR_DICT[usr] = psw
                _dir = self.directory.joinpath(usr)
                try:
                    _dir.mkdir()
                except FileExistsError:
                    pass
                finally:
                    bd = open(str(_dir.joinpath(usr+'.bd')), 'w')
                    bd.close()
                ack = self.receive()
                self.login(usr, psw)
        else:
            self.send("Comando inválido!")
    
    def post(self, file_address):
        """Método que controla o upload de um arquivo
        
        Esse método controla o upload de um arquivo para o diretório do usuário
        sem se preocupar com qual a versão do arquivo.
        
        Args:
            file_address (str): endereço do arquivo na máquina do cliente
            
        """
        self.send("ack")
        filename = ntpath.basename(file_address)
        count = 0
        for b in self.receive_file(str(self.directory.joinpath(filename))):
            count += b
            print(count)
        print(str(count) + ' bytes recebidos de '+ str(self.client))
        self.usr_bd[filename] = (self.usr, str(datetime.datetime.now()))
            
    def recover_bdfile(bdfilename):
        """Método para recuperar o dicionário de arquivos de um usuário
        
        Os dicionários de arquivos possuem como chave o nome do arquivo e como
        valor uma tupla contendo o auto e a data da última atualização do
        arquivo.
        
        Args:
            bdfilename (str): nome do arquivo .bd do usuário
            
        Returns:
            (dict) dicionário no formato:
                dict[(nome do arquivo)] = (proprietário, última modificação)
            
        """
        bd_dict = dict()
        file = open(bdfilename, 'rb')
        for line in file:
            line = base64.a85decode(line).decode()
            info = line.split(' ')
            bd_dict[info[0]] = tuple(info[1:])
        file.close()
        return bd_dict
    
    @staticmethod
    def generate_bdfile(bdfilename, bd_dict):
        """Método que cria um arquivo .bd a partir de um dicionário de arquivos
        
        O arquivo é protegido com criptografia de base64.
        
        Args:
            bdfilename (str): nome do arquivo .bd para o qual o dicionário será
                salvo.
            bd_dict (dict): dicionário a ser salvo.
        
        """
        file = open(bdfilename, 'wb')
        for key in bd_dict:
            text_line = key + ' ' + ' '.join(bd_dict[key]) + '\n'
            text_line = base64.a85encode(text_line.encode())
            file.write(text_line)
        file.close()
    
    def __repr__(self):
        """Método repr usado apenas para observação.
        
        """
        return "Client: "+self.usr +", running: " + str(self.running)

if __name__ == "__main__":
    servidor = Host()
    servidor.start()