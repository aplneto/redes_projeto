#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo de configuração dos consoles

"""

from Crypto.PublicKey import RSA
import socket
import base64

class Console(object):
    """Superclasse Console
    
    Classe base para os terminais de cliente e servidor.
    
    Attributes:
        logged (bool): True caso o usuário tenha realizado o login com sucesso,
            False caso contrário
    
    """
    def __init__(self, **kwargs):
        """Método construtor do console
        
        Args:
            ip (str): endereço ip
            port (int): porta
        
        Kwargs:
            sock (socket): socket de comunicação
        
        """
        self.sock = kwargs.get('sock',
                               socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM))
    
    def run(self):
        """Método run difere entre o Console do Host e o do Client
        
        O Método run controla o comportamento do objeto como um todo.
        Todo o comportamento de um console individual deve ser definido dentro
        do método run.
        
        """
        raise NotImplemented
    
    @staticmethod
    def start_key(key_file):
        """Método de inicialização das chaves
        
        Esse método inicializa a chave privada e prepara, também, a chave
        pública para envio.
        
        Args:
            key_file (str): endereço do arquivo da chave privada
        """
        try:
            keyfile = open(key_file, 'rb')
        except FileNotFoundError:
            private_key = RSA.generate(1024)
        else:
            private_key = RSA.importKey(keyfile.read())
            keyfile.close()
        finally:
            public_key = private_key.publickey().exportKey()
            return private_key, public_key
    
    @staticmethod
    def receive_key(sock):
        """Troca de chaves no início da comunicação
        
        Ao se conectarem, servidor e cliente trocam suas chaves públicas um com
        o outro. Esse método retorna um objeto do tipo RSA público a partir da
        chave pública recebida através de um socket.
        
        Args:
            sock (socket.socket): socket pelo qual a chave é recebida
        
        Returns:
            _RSAobj: chave pública para criptografia.
        
        """
        k = sock.recv(1024)
        key = RSA.importKey(k)
        return key
    
    @staticmethod
    def send(sock, publickey, msg):
        """Método send envia strings simples através do socket
        
        O Método send é o método usado apara enviar mensagens simples através
        de um socket. Dentro desse método ocorrem as criptografias RSA e base64
        antes do envio."
        
        Args:
            sock (socket.socket): socket pelo qual a mensagem é enviada
            publickey (_RSAobj): objeto RSA que criptografa a mensagem
            msg (str): mensagem a ser enviada
        
        """
        msg = msg.encode()
        msg = publickey.encrypt(msg, 3.14159265359)
        msg = base64.a85encode(msg[0])
        sock.sendall(msg)
    
    @staticmethod
    def receive(sock, privatekey):
        """Método receive recebe mensagens simples através do socket
        
        É através desse método que o usuário recebe mensagens simples através
        do socket. As mensagens chegam criptografadas e a descriptografia
        acontece dentro do método receive.
        
        Args:
            sock (socket.socket): socket pelo qual a mensagem é recebida
            privatekey (_RSAobj): objeto RSA que decifra a mensagem
        
        Returns:
            (str) mensagem decifrada
        
        """
        msg = sock.recv(1024)
        msg = base64.a85decode(msg)
        msg = privatekey.decrypt(msg)
        return msg.decode()
    
    def upload(self, file):
        """
        """
        raise NotImplemented
    
    def download(self):
        """
        """
        raise NotImplemented
    
    def __repr__(self):
        return "{0}({1}, {2}, key_file = {3})".format(self.__class__.__name__,
                self.sock.__repr__(), self.client.__repr__(),
                repr(self.key_file))