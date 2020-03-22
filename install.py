### install.py ###
# -*- coding: utf-8 -*-

# encontra caminho atual
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

print('Atualizando módulos')
req = os.path.dirname(os.path.realpath(__file__))+'\\requirements.txt'
os.system('python -m pip --disable-pip-version-check install -r '+req+' --quiet')