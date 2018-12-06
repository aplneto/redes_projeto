#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo de configuração dos consoles

"""

from Crypto.PublicKey import RSA
import socket
import os
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
        
        Kwargs:
            sock (socket): socket de comunicação
            key_file (str): arquivo para inicialização de par de chaves
        
        """
        self.sock = kwargs.get('sock',
                               socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM))
        key_file = kwargs.get('key_file', '')
        if key_file:
            self.privatekey, self.publickey = Console.start_key(key_file)
    
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
        
        Returns:
            (tuple) uma tupla contendo um par _RSAobj (chave privada) e byte 
            (inicializador da chave pública)
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
    
    def receive_key(self):
        """Troca de chaves no início da comunicação
        
        Ao se conectarem, servidor e cliente trocam suas chaves públicas um com
        o outro. Esse método retorna um objeto do tipo RSA público a partir da
        chave pública recebida através de um socket.
        
        Returns:
            (_RSAobj) chave pública para criptografia.
        
        """
        k = self.sock.recv(1024)
        key = RSA.importKey(k)
        return key
    
    def send(self, msg):
        """Método send envia strings simples através do socket
        
        O Método send é o método usado apara enviar mensagens simples através
        de um socket. Dentro desse método ocorrem as criptografias RSA e base64
        antes do envio."
        
        Args:
            msg (str ou bytes): mensagem a ser enviada
        
        """
        msg = self.encrypt(msg)
        self.sock.send(msg)
    
    def receive(self, b = 160):
        """Método receive recebe mensagens simples através do socket
        
        É através desse método que o usuário recebe mensagens simples através
        do socket. As mensagens chegam criptografadas e a descriptografia
        acontece dentro do método receive.
        
        Args:
            b (int): quantidade de bytes a serem recebidos
        
        Returns:
            (str) mensagem decifrada
        
        """
        msg = self.decrypt(self.sock.recv(b))
        return msg.decode()
    
    def encrypt(self, msg):
        """Criptografia de uma string ou trecho de bytes
        
        Args:
            msg (str ou bytes): string ou bytes a serem criptografados.
        
        Returns:
            (bytes) segmento de bytes criptografados
        
        """
        if isinstance(msg, str):
            msg = msg.encode()
        msg = self.publickey.encrypt(msg, 3.14159265359)
        msg = base64.a85encode(msg[0])
        return msg
    
    def decrypt(self, msg):
        """Método de conversão de um trecho criptografado
        
        Args:
            msg (bytes): trecho de mensagem a ser decifrado
        
        Returns:
            (bytes): trecho de bytes decifrados
        """
        msg = base64.a85decode(msg)
        msg = self.privatekey.decrypt(msg)
        return msg
        

    def send_file(self, filename):
        """Rotina de envio de arquivos através de sockets
        
        Esse método controla o envio sequencial de segmentos de um arquivo
        através de um socket, gerando a cada envio um número inteiro referente
        a quantidade de bytes enviados até o momento.
        Método deve ser usado como um gerador. Veja exemplo abaixo.
        
        Example:
            
            for b in self.sendfile('alice.txt'):
                if b == -1:
                    print("Houve um erro na transferência")
                else:
                    print(str(b) + "de " str(file_size) "bytes enviados")
        
        Args:
            filename (str): endereço do arquivo
            
        Yields:
            (int) quantidade de bytes enviados ou -1, em caso de erro
        
        """
        size = os.path.getsize(filename)
        self.send(str(size))
        sent = 0
        file = open(filename, 'rb')
        while sent < size:
            nxt = file.read(1024)
            self.sock.send(self.encrypt(nxt))
            sent += len(nxt)
            yield sent
        file.close()
            
            
    
    def receive_file(self, filename):
        """Rotina de recebimento de arquivos através de sockets
        
        Esse método controla o recebeimendo de sementos de arquivos através de
        um socket. O método gera a quantidade de bytes recebidos a cada nova
        mensagem recebida do socket, por tanto, deve ser usado como um gerador.
        
        Example:
            
            for b in receive_file(filename):
                print(str(b) + " de " str(filesize) " bytes recebidos.")
        
        Args:
            filename(str): nome do arquivo
        
        Yields:
            (int) quantidade de bytes recebidos
        """
        size = int(self.receive())
        file = open(filename, 'wb')
        rcvd = 0
        while rcvd < size:
            nxt = self.decrypt(self.sock.recv(160))
            rcvd += len(nxt)
            file.write(nxt)
            yield rcvd
        file.close()
            
    def __repr__(self):
        return "{0}({1}, {2}, key_file = {3})".format(self.__class__.__name__,
                self.sock.__repr__(), self.client.__repr__(),
                repr(self.key_file))