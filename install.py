### install.py ###
# -*- coding: utf-8 -*-

# encontra caminho atual
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

print('Instalando/atualizando módulos')
req = os.path.dirname(os.path.realpath(__file__))+'\\requirements.txt'

versao = 'python'
for v in ('python37','pythoncom'):
	t = os.system(v+' -m pip')
	if t == 0:
		versao = v
		break

os.system(versao+' -m pip --disable-pip-version-check install -r "'+req+'" --quiet')