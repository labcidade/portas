### install.py ###

# encontra caminho atual
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# atualiza pip para a versão requerida
print('Atualizando pip')
os.system('python -m pip --disable-pip-version-check install -U pip==18.0')

print('Atualizando módulos')
from pip._internal import main as pipmain
req = str(os.path.dirname(os.path.realpath(__file__)))+'/requirements.txt'
pipmain(['--disable-pip-version-check','install','-r',req,'--quiet'])