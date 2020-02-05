### portas.py ###

import sys
import os
import io
import re
import csv
import zipfile
import threading
import queue
import ctypes
import requests
import datetime
import requests
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
from labcidade_portas.var import webdriverpath

# lista arquivos de configuração especial
_parent = os.path.dirname\
	(os.path.dirname(os.path.realpath(__file__)))+'\\dics'
_templates = [x for x in os.listdir(_parent) \
	if os.path.isdir(os.path.join(_parent,x))]
if not _templates:
	_templates = [None]

# função que formada cadeias de texto simples
def _limpar(texto):
	texto = str(texto)
	textolimpo = texto.replace("\n","").replace("\t","").replace(":","")\
		.replace(";","").replace("(A)","").replace("(RÉ)","")\
		.replace("(ES)","").replace("(S)","").strip()
	return textolimpo

# função que formata texto em html
def _limpar_html(texto_html):
	texto = str(texto_html.get_text())
	textolimpo = texto.replace("\n","").replace("\t","")\
		.replace(r'\N','').replace("\T","").strip()
	return textolimpo

# função que retira itens vazios de listas
def _limpar_lista(lista):
	listalimpa = [s for s in lista if s]
	for item in ('A','S'):
		while item in listalimpa:
			listalimpa.remove(item)
	return listalimpa

# função para ler dicionários
def _ler_dic (path):
	assert os.path.isfile(path)
	assert path.endswith('.txt')
	dout = {}
	with open(path) as p:
		for l in p:
			(c,v)=l.split()
			d[c]=[v]
	return dout

# obtém metadados de arquivo pz
def _obter_meta(path):
	with open (path,'b') as file:
		arqzip = zipfile.ZipFile(file)
		meta = arqzip.read('meta.txt')
		dmeta =_ler_dic(meta)
	return dmeta

# abre o webdriver e encontra uma url
def _achar_url():
	browser = selenium.webdriver.Chrome(webdriverpath)
	browser.get('https://esaj.tjsp.jus.br/cjpg/')
	print("\nConfigure sua pesquisa na janela.\nCaso já possua a url de uma pesquisa configurada, abra-a no navegador")
	print("Quando terminar, aperte enter")

	# Pede configuração de pesquisa no browser
	while True:
		try:
			input('>>> ')
			browser.find_element_by_xpath("//*[@value='Consultar']").click()
			break
		except:
			print('FECHE TODAS AS JANELAS DE SELEÇÃO NO NAVEGADOR ANTES DE CONTINUAR...')
			continue

	url = browser.current_url
	browser.quit()
	return url

	# Ordena as datas em sequência ascendente
	self.url = self.url.replace("ordenacao=DESC","ordenacao=ASC")

# abre explorer para achar arquivo de extensão "ext"
def _achar_arq(ext):
	while True:
		try:
			Tk().withdraw()
			alvo = askopenfilename()
			assert alvo.endswith(ext)
			break
			if ext == 'tjsp':
				arqzip = zipfile.ZipFile(alvo)
				arquivos_no_zip = arqzip.namelist()
				assert 'cache.csv' in arquivos_no_zip 
				assert 'meta.txt' in arquivos_no_zip
		except AssertionError:
			print ('Arquivo não é do formato .{}'.format(ext))
			continue
	return alvo

# abre explorer para achar pasta
def _achar_pasta():
	Tk().withdraw()
	alvo = askdirectory()
	return alvo

# define erro de entrada
class EntradaIncorreta(Exception):
    pass


'''
CLASSE PESQUISA
Objeto de configuração de busca
Pode ser configurado por parâmetros ou pelo método configurar()
Utilizado na função cumprir
'''
class pesquisa:
	def __init__(self,tipo='n',nome=None,url=None,
			limite=None,indice=0,arq=None,dics=None):

		if tipo not in ['n','a','r']:
			raise EntradaIncorreta('Tipo deve ser "n" (nova), "a" (atualizar) ou "r" (retomar)')
		
		if tipo in ['a','r'] and not arq:
			raise EntradaIncorreta('"arq" deve ser especificado')
		
		if tipo in ['a','r'] and not os.path.isfile(arq):
			raise EntradaIncorreta('arquivo "arq" não existe')
		
		if arq and arq[-5] != '.tjsp':
			raise EntradaIncorreta('Arquivo não tem formato .tjsp')
			
		if dics and dics not in _templates:
			raise EntradaIncorreta('Template customizado de campos não encontrado')
		
		self.ok = False

		# localiza os arquivos, se houver
		if arq:
			self.raiz = os.path.dirname(arq)
			self.cache = self.raiz + '/cache.csv'
		else:
			self.raiz = None
			self.cache = None
		
		# configura pesquisa se houver parâmetros
		if tipo == 'r' and arq:
			d = _obter_meta(arq)
			self.nome = d['nome']
			self.url = d['url']
			self.limite = limite
			self.indice = int(d['pesquisados'])
			self.arq = arq
			self.dics = d['dics']
			self.ignorados = d['ignorados']
			self.ok = True
		elif tipo == 'a' and arq:
			d = _obter_meta(arq)
			self.nome = d['nome']
			self.url = d['url']
			self.limite = limite
			self.indice = 0
			self.arq = arq
			self.dics = d['dics']
			self.ignorados = 0
			self.ok = True
		else:
			self.nome = nome
			self.url = url
			self.limite = limite
			self.indice = indice
			self.arq = arq
			self.dics = dics
			self.ignorados = 0
			if nome and url and arq:
				self.ok = True

	# configura a pesquisa manualmente
	def configurar(self):
		print('INICIANDO CONFIGURAÇÃO DE PESQUISA...')

		# define tipo de pesquisa
		while True:
			print('\nQual tipo de pesquisa você deseja realizar?\
				\n"n": Nova pesquisa\
				\n"r": Retomar pesquisa\
				\n"a": Atualizar pesquisa')
			self.tipo = input('>>> ')
			if self.tipo in ['n','a','r']:
				break
			else:
				print('Tipo inválido\n')
				continue

		# define um limite para a pesquisa
		while True:
			print('\nDeseja definir um número máximo de processos a raspar? <s/n>')
			xxx = input('>>> ')
			if xxx in ('s','n'):
				break
			else:
				print('Valor inválido')
				continue
		
		if xxx == 's':
			while True:
				try:
					limite = input('\nDigite o limite: ')
					self.limite = int(limite)
					break
				except:
					print('O valor não é um número inteiro')
					continue
		
		# configura uma atualização ou retomada
		if self.tipo in ['a','r']:
			print('Selecione na janela o arquivo .tjsp com os dados da pesquisa a continuar.')
			self.arq = _achar_arq('.tjsp')
			self.raiz = os.path.dirname(self.arq)
			self.cache = self.raiz + '/cache.csv'
		
			d=_obter_meta(self.arq)

			if self.tipo == 'a':
				self.url = d['url']
				self.nome = d['nome']
				self.indice = 0
				self.ignorados = 0
				self.dics = d['dics']
				self.ok = True
			if self.tipo == 'r':
				self.url = d['url']
				self.nome = d['nome']
				self.indice = 0
				self.ignorados = 0
				self.dics = d['dics']
				arquivo_zip.extract('cache.csv',self.raiz)
				ctypes.windll.kernel32.SetFileAttributesW(self.cache, 2)
				self.ok = True

		# configura uma pesquisa nova
		if self.tipo == 'n':
			print('\nDigite um nome para sua pesquisa')
			self.nome = str(input('>>> '))
			print('\nAgora escolha na janela uma pasta onde deve ser salvo o resultado da raspagem')
			self.raiz = _achar_pasta()
			self.arq = self.raiz + '/{}.tjsp'.format(self.nome)
			self.cache = self.raiz + '/cache.csv'
			print(">>>",self.raiz)
			self.indice = 0
			self.ignorados = 0		
			self.url = _achar_url()

			# configura template
			print('\nDigite um template customizado de campos de pesquisa\
				\nTemplates disponíveis:',_templates,\
				'\nDeixe vazio para usar apenas campos básicos')
			while True:
				try:
					d = input('>>> ')
					if d:
						assert d in _templates
						self.dics = d
					else:
						self.dics = None
					break
				except AssertionError:
					print('Template não localizado\n')
					continue

			self.ok = True


'''
FUNÇÃO _ROBO
Objeto de configuração de busca
Pode ser configurado por parâmetros ou pelo método configurar()
Utilizado na função cumprir
'''
def _robo(tarefas,matriz,parciais,cadeado,cadeado2):
	while not tarefas.empty():
		tarefa = tarefas.get()
		partida = datetime.datetime.now()
		
		cadeado2.acquire()
		if 'bandeira' in parciais:
			cadeado2.release()
			tarefas.task_done()
			cadeado2.release()
			continue
		cadeado2.release()

		try:
			# solicita dados de mudança de página
			ts = 'Acessando página '+str(tarefa)+'...'
			print(ts)
			while True:
					try:
						sessao = requests.Session()
						sessao.trust_env=False
						resposta = sessao.get(pesquisa.url,verify=False)
						pagina = sessao.get('https://esaj.tjsp.jus.br/cjpg/trocarDePagina.do?pagina='+str(tarefa)+'&conversationId=',verify=False)
						itens_na_pagina = [a for a in BeautifulSoup(pagina.content,'html.parser').find_all("tr",{"class":"fundocinza1"})[:10]]
						assert pagina.text != '\nSessão Expirada\n' and pagina.ok
						sessao.close()
						break
					except AssertionError:
						agora = datetime.datetime.now()
						if (agora-partida).total_seconds() > timeout:
							itens_na_pagina = None
							break
						else:
							continue

			# checa se página tem conteúdo
			if type(itens_na_pagina) != list:
				print('\nO servidor levou tempo demais para responder. A raspagem será terminada em breve.\n')
				cadeado2.acquire()
				parciais.append('terminar')
				cadeado2.release()
				tarefas.task_done()
				continue

			# checa se página tem conteúdo
			if len(itens_na_pagina) == 0:
				ts = 'Página '+str(tarefa)+' vazia!'
				print(ts)
				cadeado2.acquire()
				parciais.append('bandeira')
				cadeado2.release()
				tarefas.task_done()
				continue

			# se for a primeira busca, define o primeiro item a partir 
			if tarefa == pag1:
				itens_na_pagina = itens_na_pagina[i_inicio:]

			# loop de raspagem dos itens na página
			for itemhtml in itens_na_pagina:

				try:
					u = itemraspado(itemhtml)
					u.partes()
					u.buscaralvo('Razão parte 1', dic_razao, u.parte1)
					u.buscaralvo('Razão parte 2', dic_razao, u.parte2)
					u.contarparte('Parte 2 múltipla',u.dic['Parte 2'])
					u.buscaralvo('Grupo parte 1', dic_grupos, u.dic['Parte 1'])
					u.buscaralvo('Grupo parte 2', dic_grupos, u.dic['Parte 2'])
								
					if u.dic['Grupo parte 1'] == 'Instituição financeira':
						u.buscaralvo('Descrição parte 1',dic_financeiros, u.dic['Parte 1'])
					elif u.dic['Grupo parte 1'] == 'Autarquia/Empresa pública':
						u.buscaralvo('Descrição parte 1',dic_autarquias, u.dic['Parte 1'])
					elif u.dic['Grupo parte 1'] == 'Estado':
						u.buscaralvo('Descrição parte 1',dic_estado, u.dic['Parte 1'])
					else:
						u.campovazio('Descrição parte 1')

					u.buscaralvo('RAJ',dic_rajs,u.dic["Comarca"])
					u.buscaralvo('Justiça gratuita',{'Sim':["\nJUSTIÇA GRATUITA\n"]},u.resumo)
					u.buscaralvo('Imobiliário',{'Sim':["IMÓVEL","IMÓVEIS","MATRÍCULA","APARTAMENTO","IMOVEL","IMOVEIS","TERRENO","EDIFÍCIO","EDIFICIO","PRÉDIO","LOTEAMENTO"," LOTE "," LOTES "," LOTE."," LOTES."," LOTE,"," LOTES,"]},u.resumo)
					u.buscaralvo('Invasor',{'Plural':["INVASORES"],'Singular':["INVASOR","INVASÃO","INVADID"]},u.resumo)
					u.buscaralvo('Sublocação',{'Sim':["SUBLOCA","SUBLOCÁ"]},u.resumo)
					u.buscaralvo('Ambiental',{'Sim':["PROTEÇÃO AMBIENTAL","DANO AMBIENTAL","RISCO AMBIENTAL","PRESERVAÇÃO AMBIENTAL","IRREGULARIDADE AMBIENTAL","PROTEÇÃO PERMANENTE","PRESERVAÇÃO PERMANENTE","DE MANANCIA"]},u.resumo)
					u.buscaralvo('Uso imóvel',dic_usos,u.resumo)
					u.aluguel()
					u.endereco()
					u.sentencas(dic_sentencas)

					try:
						u.busca_avancada()
					except:
						u.campovazio("Situação")
						u.campovazio("Valor da ação (R$)")
						u.campovazio("Data distribuição")

					if not u.avancado:
						cadeado.acquire()
						parciais.append('erroavancado')
						cadeado.release()

					cadeado.acquire()
					matriz.append(u.dic)
					cadeado.release()

				# ignora item se houver erro na raspagem
				except:
					cadeado2.acquire()
					parciais.append('ignorado')
					cadeado2.release()
					
				cadeado2.acquire()
				parciais.append('contagem')
				cadeado2.release()

			cadeado2.acquire()
			parciais.append('pagina')
			cadeado2.release()
			ts = 'Página '+str(tarefa)+' raspada!'
			print(ts)
				
		except:
			cadeado2.acquire()
			parciais.append('terminar')
			cadeado2.release()
			tarefas.task_done()
			break

		tarefas.task_done()


'''
FUNÇÃO CUMPRIR
Objeto de configuração de busca
Pode ser configurado por parâmetros ou pelo método configurar()
Utilizado na função cumprir
'''