#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script do Host
"""

from pathlib import Path

class Host(object):
    '''
    '''
    def __init__(self, root = "./HOST", **kwagrs):
        self.root = Path(root)
        if kwagrs.get('autoconfig', False):
            self.__autoconfig()
        else:
            self.__config()
    
    def __autoconfig(self):
        self.usuarios = dict()
    
    def __config(self, *args):
        self.usuarios = dict()
    
    def __cadastro(self, login, senha):
        if login in self.usuarios:
            return "2"
        else:
            self.usuarios[login] = senha
    
    def __login(self, login, senha):
        raise NotImplemented