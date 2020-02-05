### var.py ###

import os
import platform
import sys
import io
import requests
import zipfile

# identifica versão de python
versao = str(sys.version_info[0])+str(sys.version_info[1])

# encontra o caminho de instalação dos pacotes de python
arquitetura = platform.architecture()[0]
versao_extensa = 'Python'+ versao
pythonpaths = [a for a in list(sys.path) if a]
pythonpath = [b for b in pythonpaths if versao in b][0]
pythondir = '/'.join(pythonpath.split('\\')[:pythonpath.split('\\').index('Python')+1])

# cria o caminho do webdriver
if arquitetura == '64bit':
	webdriverdir = pythondir+'/'+versao_extensa+'/Lib/site-packages/selenium/webdriver'
else:
	webdriverdir = pythondir+'/'+versao_extensa+'-32/Lib/site-packages/selenium/webdriver'

webdriverpath = webdriverdir + '/chromedriver.exe'

# instala webdriver
try:
	assert 'chromedriver.exe' in os.listdir(webdriverdir)
except AssertionError:
	s = requests.Session()
	r = s.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE')
	url_zip = 'https://chromedriver.storage.googleapis.com/'+ r.text +'/chromedriver_win32.zip'
	r = s.get(url_zip)
	z = zipfile.ZipFile(io.BytesIO(r.content))
	z.extractall(webdriverdir)