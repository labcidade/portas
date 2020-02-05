### test.py ###

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import install

from labicidade_portas import portas

p = portas.pesquisa()
p.configurar()