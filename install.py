### install.py ###
# -*- coding: utf-8 -*-

# encontra caminho atual
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# testa a variável ambiente para python
for v in ('python37','python'):
	t = os.system(v+' -m pip')
	if t == 0:
		versao = v
		break

print('Instalando/atualizando módulos')
req = os.path.dirname(os.path.realpath(__file__))+'\\requirements.txt'
os.system('python -m pip --disable-pip-version-check install -r "'+req+'" --quiet')
