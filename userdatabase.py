#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo de controle do banco de dados do usuário

"""

class DataBase:
    """Objeto DataBase
    
    Controla o armazenamento e proteção de dados de usuários, como nome de
    usuário e senha.
    
    Attributes:
        DATABASE_LOCAL (str): endereço padrão do banco de dados.
    
    """
    DATABASE_LOCAL = "root/users.bf"
    def __init__(self, local = DATABASE_LOCAL):
        """Método Construtor
        
        Args:
            local (str): endereço do arquivo de banco de dados
        
        """
        self.local = local
        self.__usr = dict()
    
    def __contains__(self, usr):
<<<<<<< HEAD
        return usr in self.__usr
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.local.__repr__())
=======
        return usr in self.__usr
>>>>>>> 484e4ac42f016cb9c468bfab912315426f81b66b
