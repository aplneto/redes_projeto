#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo principal do programa

Módulo principal do servidor de arquivos TCP, tanto para cliente quanto para
servidor.

Todo:
    * terminar auto_config()
    
"""

from host import Host
from client import Client

__authors__ = "Antônio Neto, Isac Silva, Ivan Lima, Pedro Rodolfo"
__copyright__ = "Copyright 2018, Universidade Federal de Pernambuco"
__credits__ = []

__license__ = "MIT"
__version__ = "alpha"
__email__ = ["apln2@cin.ufpe.br", "its@cin.ufpe.br", "ifsl2@cin.ufpe.br",
             "prgs@cin.ufpe.br"]
__status__ = "development"

CONFIG_FILE = "config.txt"

def auto_config(tcon = 'client'):
    """Função auxiliar de configuração de conexão
    
    Essa função permite a criação automática de um novo servidor TCP ou a
    conexão a um servidor tcp existente.
    
    Args:
        tcon (str): string que discrimina o tipo de conexão, 'client' ou 'host'
    
    Raises:
        ValueError: se o parâmetro ``tcon`` for diferente de 'client' ou 'host'
    
    """
    raise NotImplemented