# -*- coding: utf-8 -*-
### portas.py ###

import os
import re
import csv
import zipfile
import threading
import queue
import ctypes
import requests
import datetime
import requests
import hashlib
import pandas
from zipfile import ZipFile, ZIP_DEFLATED
from bs4 import BeautifulSoup
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

_parent = os.path.dirname(os.path.realpath(__file__))
ico = _parent+'\\gui\\icone_martelo.ico'

# lista arquivos de configuração especial
_dics = os.path.dirname(os.path.realpath(__file__))+'\\dics'

requests.packages.urllib3.disable_warnings()
root = Tk()
root.iconbitmap(ico)
root.withdraw()

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

# função para checar se pasta é template
def _template_ok(path):
	try:
		for v in os.listdir(path):
			dpath = os.path.join(path,v)
			d = _ler_dic(dpath)
			assert d
			return True
	except:
		return False

# função para ler dicionários
def _ler_dic (path):
	assert os.path.isfile(path)
	assert path.endswith('.txt')
	dout = {}
	with open(path, encoding='utf-8') as p:
		for l in p:
			c,v=l.split('\t')
			dout[c]=v.replace('\n','').replace('\r','')
	return dout

# obtém metadados de arquivo pz
def _obter_meta(path):
	dmeta = {}
	with zipfile.ZipFile(path,'r') as file:
		with file.open('meta.txt') as meta:
			for l in meta:
				m = l.decode('utf-8')
				m = m.replace('/r','')
				c,v=m.split('\t')
				dmeta[c]=v.replace('\n','').replace('\r','')
	return dmeta

# prepara o template de uma pesquisa a partir de um arquivo portas
def _preparar_template(pf,pasta_dics):
	dmeta = _obter_meta(pf)
	alvozip = pf.replace('.portas','.zip')
	os.rename(pf,alvozip)

	try:
		with zipfile.ZipFile(alvozip,'r') as file:
			vars_zip = [x.replace('template/','') for x in file.namelist() if x.startswith('template/')]
			info_zip = [x for x in file.infolist() if x.filename.startswith('template/')]
			vars_zip.sort()
			templates = os.listdir(pasta_dics)
			rivais = [x for x in templates if x.startswith(dmeta['template'])]
			r1 = ['_'.join(x.split('_')[:-1]) for x in rivais if '_' in x and x.split('_')[-1].isdigit()]
			r2 = [x for x in rivais if '_' not in x]
			r = r1+r2
			nrivais = r.count(dmeta['template'])
			if nrivais == 0:
				sufixo = ''
			else:
				sufixo = '_' + str(nrivais)
			
			if dmeta['template'] in rivais:
				pasta_rival = pasta_dics+'\\'+dmeta['template']
				vars_rivais = [x for x in os.listdir(pasta_rival)]
				vars_rivais.sort()
				if vars_zip != vars_rivais:
					novo_template = pasta_dics+'\\'+dmeta['template']+sufixo
					print(novo_template)
					os.mkdir(novo_template)
					for f in info_zip:
						f.filename = os.path.basename(f.filename)
						file.extract(f,novo_template)
			else:
				novo_template = pasta_dics+'\\'+dmeta['template']+sufixo
				print(novo_template)
				os.mkdir(novo_template)
				for f in info_zip:
					f.filename = os.path.basename(f.filename)
					file.extract(f,novo_template)
	
	finally:
		os.rename(alvozip,pf)
		return dmeta['template']

# encontra um arquivo portas e retorna caminho e dados
def _achar_portas():
	while True:
		try:
			alvo = askopenfilename(filetypes=[("Arquivos Porta","*.portas")],title='Selecione o arquivo .portas')
			alvozip = alvo.replace('.portas','.zip')
			os.rename(alvo,alvozip)
			arqzip = zipfile.ZipFile(alvozip,'r')
			arquivos_no_zip = arqzip.namelist()
			assert 'data.csv' in arquivos_no_zip
			assert 'meta.txt' in arquivos_no_zip
			meta = _obter_meta(alvozip)
			break
		except AssertionError:
			continue
		finally:
			arqzip.close()
			os.rename(alvozip,alvo)
	return alvo, meta

# abre explorer para achar pasta
def _achar_pasta():
	alvo = askdirectory(title='Selecione a pasta')
	return alvo

# extrai os dados de um arquivo portas
def _extrair_csv(pf,destino):
	assert destino.endswith('.csv')
	alvozip = pf.replace('.portas','.zip')
	os.rename(pf,alvozip)

	try:
		with zipfile.ZipFile(alvozip,'r') as zfile:
			with open(destino, "wb") as file: 
				file.write(zfile.read('data.csv'))
	finally:
		os.rename(alvozip,pf)

# conta os resultados de uma pesquisa
def _contar_resultados(url_base):
	try:
		s = requests.Session()
		r = s.get(url_base)
		h = BeautifulSoup(r.content,'html.parser')
		r2 = h.find_all('div',{'id':'resultados'})
		assert len(r2) > 0
		x = h.findAll('td',{'bgcolor':'#EEEEEE'})[-2].getText()
		x = x.split()[-1]
		meta = int(x)
		return meta
	except:
		return 0

# troca arquivo csv do portas por xlsx
def _trocar_csv(arq_csv):
	assert arq_csv.endswith('.csv')
	df = pandas.read_csv(arq_csv,encoding='utf-8',sep='|')
	writer = pandas.ExcelWriter(arq_csv.replace('.csv','.xlsx'))
	df.to_excel(writer,index = False)
	writer.save()
	os.remove(arq_csv)

# define erro de entrada
class EntradaIncorreta(Exception):
    pass


'''
CLASSE PESQUISA
Objeto de configuração de busca
Utilizado na função executar
'''
class pesquisa:
	def __init__(self,nome=None,url=None,ciclo=None,robos=None,
			limite=None,indice=0,ignorados=0,arq=None,dics=None,
			completa=False,retomada=False,original=None,salvar_xlsx=False):
		self.nome=nome
		self.url=url
		self.ciclo=ciclo
		self.robos=robos
		self.limite=limite
		self.indice=indice
		self.ignorados=ignorados
		self.arq=arq
		self.dics=dics
		self.completa=False # introdução de recaptcha no site impossibilitou a busca
		self.retomada=retomada
		self.original=original
		self.salvar_xlsx=salvar_xlsx


'''
CLASSE RELATÓRIO
Objeto de reporte da pesquisa
Utilizado na função executar
'''
def relatar(pesquisa,registro=0):
	indice = pesquisa.indice + registro
	if pesquisa.dics:
		template = pesquisa.dics
	else:
		template = '*'
	relato = 'nome\t' + pesquisa.nome +'\n'+\
		'indice\t' + str(indice) +'\n'+\
		'ignorados\t' + str(pesquisa.ignorados) +'\n'+\
		'template\t' + str(os.path.basename(template)) +'\n'+\
		'url\t'+str(pesquisa.url)
	return relato


'''
CLASSE ITEMREGISTRO
Objeto unidade de dados
Usado pela função _robo
'''
class itemregistro:
	def __init__(self,item_em_html):
		self.dic = {}
		self.dados = item_em_html.find_all("tr")
		self.completo = True
		self.avancado = False
		horario = datetime.datetime.now().isoformat()
		dia = '/'.join(horario[:10].split('-')[::-1])
		hora = datetime.datetime.now().isoformat()[11:19]
		self.dic['Hora registro'] = dia+' '+hora

		for a in ["Processo","Classe","Assunto","Magistrado","Comarca","Foro","Vara","Data de Disponibilização"]:
			self.dic[a] = ''

		# registra o número identificador do processo
		self.dic["Processo"] = _limpar_html(self.dados[0])		

		# extrai a ficha com os dados principais do processo
		if len(self.dados) == 8:
			self.dic["Classe"]=''
			for tr in self.dados[1:7]:
				tr_limpo = _limpar_html(tr).split(":")
				self.dic[tr_limpo[0].strip()] = tr_limpo[-1].strip()
		elif len(self.dados) == 9:
			for tr in self.dados[1:8]:
				tr_limpo = _limpar_html(tr).split(":")
				self.dic[tr_limpo[0].strip()] = tr_limpo[-1].strip()
		else:
			self.completo =	False

		self.resumo = self.dados[-1].find_all("span")[-1].get_text().upper()
		self.dic["Comprimento resumo"] = len(self.resumo.replace("\n","").replace("\t",""))

	# função para procurar uma série de valores de dic em alvo e retornar chave para campo
	def buscaralvo(self,campo,dic,alvo):
		assert type(dic) == dict
		self.dic[campo] = ''
		for chave, valor in dic.items():
			if chave in alvo:
				self.dic[campo] = valor
				break

	# função para registrar partes do processo
	def partes(self):

		dicpartes = {
		'Requerente/Requerido':["\nREQUERENTE","\nREQUERENTES"],
		'Embargante/Embargado':["\nEMBARGANTE","\nEMBARGANTES"],
		'Autor/Réu':["\nAUTOR","\nAUTORA","\nAUTORES","\nAUTORAS"]}
		
		self.dic['Tipo partes'] = ''
		self.dic['Parte 1'] = ''
		self.dic['Parte 2'] = ''
		

		for key, lista in dicpartes.items():
			try:
				assert self.dic['Tipo partes'] == ''
				for termo in lista:
					if termo in self.resumo:
						self.dic['Tipo partes'] = key
						self.dic['Parte 1'] = _limpar_lista(self.resumo[self.resumo.index(termo):].replace(":","").replace(";","").replace("(A)","").replace("(RÉ)","").replace("(ES)","").replace("(S)","").split(termo)[1].split("\n"))[0].strip()
						self.parte1 = self.dic['Parte 1'] + ' '
						break
			except AssertionError:
				break


		if self.dic['Tipo partes']:
			for termo in ("\nREQUERIDO","\nREQUERIDA","\nREQUERIDOS","\nREQUERIDAS","\nEMBARGADO","\nEMBARGADA","\nEMBARGADOS","\nEMBARGADAS","\nRÉU","\nRÉUS","\nRÉ"):
				if termo in self.resumo:
					self.dic['Parte 2'] = _limpar_lista(self.resumo[self.resumo.index(termo):].replace(":","").replace(";","").replace("(A)","").replace("(RÉ)","").replace("(ES)","").replace("(S)","").split(termo)[1].split("\n"))[0].strip()
					self.parte2 = self.dic['Parte 2'] + ' '
					break

	# função que aponta se há mais de duas pessoas/itens enumerados no alvo
	def contarparte(self,campo,alvo):
		x = ''
		for tipo in ("E OUTROS","E OUTRAS"):
			if tipo in alvo:
				x = 'Sim'
				
		if not x:
			if alvo.count(",") - alvo.count("CPF") > 1:
				x = 'Sim'
		self.dic[campo] = x

	# função para criar definição vazia no dicionário
	def campovazio(self,campo):
		self.dic[campo] = ''

	# função para encontrar valores de aluguel
	def aluguel(self):
		self.dic["Contagem R$"] = self.resumo.count('R$')

		# se classe for sobre despejo e houver valor monetário, procura valor da dívida e valor mensal do aluguel
		self.dic["Aluguel (R$)"] = ''
		self.dic["Aluguel atualizado (R$)"] = ''
		self.dic["Dívida do requerido (R$)"] = ''
		self.dic["Aluguel NA"] = ''
		self.dic["Aluguel atualizado NA"] = ''
		self.dic["Dívida do requerido NA"] = ''

		if 'DESPEJO' in self.dic['Classe'].upper() and self.dic["Contagem R$"]>0:
						
			# procura valores de aluguel
			for frase in ['ALUGUEL MENSAL','MENSAL','VALOR DO ALUGUEL','VALOR ATUAL DO ALUGUEL']:
				if frase in self.resumo:
					trechos = [a.split(',')[0] for a in self.resumo.split(frase)]
					trechos_seg = [a.split(',')[1] for a in self.resumo.split(frase)]
							
					# analisa cada trecho com as frases-chave
					for n in trechos:
						trecho_seg = trechos_seg[trechos.index(n)]
						if 'R$' in n and 'CR$' not in n:
							try:
								self.dic["Aluguel (R$)"] = [int(v) for v in n[n.index('R$')+1:].replace('.','').split() if v.isdigit()][0]
								self.dic["Aluguel NA"] = ''
								break
							except IndexError:
								pass
						else:
							try:
								self.dic["Aluguel NA"] = [int(v) for v in n.replace('.','').split() if v.isdigit()][0]
							except IndexError:
								pass

						
					# Registra atualização do valor do aluguel
					if 'ATUAL' in trecho_seg :
						if 'R$' in trecho_seg:
							try:
								self.dic["Aluguel atualizado (R$)"] = [int(v) for v in trecho_seg[trecho_seg.index('R$'):].replace('.','').split() if v.isdigit()][0]
								self.dic["Aluguel atualizado NA"] = ''
							except IndexError:
								pass
						else:
							try:
								self.dic["Aluguel atualizado NA"] = [int(v) for v in trecho_seg.replace('.','').split() if v.isdigit()][0]						
							except IndexError:
								pass

				if self.dic["Aluguel (R$)"]:
					break

			# Procura valores de dívida
			for frase in ['DÉBITO','DÍVIDA','PERFAZ','TOTAL','DEVEDOR','ATRASO','CONDEN','A PAGAR']:
				if frase in self.resumo:
					trechos = [a.split(',')[0] for a in self.resumo.split(frase)]
								
					# Analisa cada trecho com as frases-chave
					for n in trechos:
						if 'R$' in n and 'CR$' not in n:
							try:
								self.dic["Dívida do requerido (R$)"] = [int(v) for v in n[n.index('R$'):].replace('.','').split() if v.isdigit()][0]
								self.dic["Dívida do requerido NA"] = ''
								break
							except IndexError:
								pass
						else:
							try:
								self.dic["Dívida do requerido NA"] = [int(v) for v in n.replace('.','').split() if v.isdigit()][0]
							except IndexError:
								pass

				if self.dic["Dívida do requerido (R$)"]:
					break

	# função para encontrar localização
	def endereco(self):
		self.dic['Endereço'] = ''
		self.dic['Ref Endereço'] = ''
		for termo in (" LOCALIZADO"," SITUADO"):
			try:
				if termo in self.resumo:
					self.dic['Ref Endereço'] = 'Sim'
					texto = self.resumo[self.resumo.index(termo):self.resumo.index(termo)+150]
					texto = texto.replace(termo,'')
					if texto[:2] == 'S ':
						texto = texto[2:]
					texto = texto.replace('NESTA CIDADE','').replace('NESTA CAPITAL','').replace('NESTA COMARCA','').replace('ENDEREÇO','').replace(' SITO ','').replace(':','').replace('/',' ')
					while '  ' in texto:
						texto = texto.replace('  ',' ')
					texto = re.split(', | -|- |;| –|– ',texto)
					texto = [a.split('+') for a in texto]
					texto = [a for b in texto for a in b]
					texto = [a for a in texto if a and a != ' ']
					logradouro = texto[0].replace('À','').replace(' Á ','').replace(' NA ','').replace(' NO ','').replace(' A ','')
					logradouro = logradouro.strip()
					numero = ''
					
					try:
						while True:
							try:
								if ' SP-' in logradouro or ' BR-' in logradouro or ' SP ' in logradouro or ' BR ' in logradouro or 'RODOVIA' in logradouro or 'ROD.' in logradouro:
									kmlista = [a for a in texto if 'KM' in a or 'QUILÔMETRO' in a][0]
									if 'KM' in kmlista:
										kmlista = kmlista[kmlista.index('KM'):]
										kmlista = kmlista.replace('KM','')
									else:
										kmlista = kmlista[kmlista.index('QUILÔMETRO'):]
										kmlista = kmlista.replace('QUILÔMETRO','')
									numero = 'KM '+[v for v in kmlista.replace('.',' ').split() if v.isdigit()][0]
									break
							except IndexError:
								pass

							if ' Nº' in logradouro:
								numero = [v for v in logradouro.split(' Nº')[-1].replace('.','').replace(',','').split() if v.isdigit()][0]
								logradouro = logradouro[:logradouro.index(' Nº')]
							elif ' N.' in logradouro:
								numero = [v for v in logradouro.split(' N.')[-1].replace('.','').replace(',','').split() if v.isdigit()][0]
								logradouro = logradouro[:logradouro.index(' N.')]
							elif ' N°' in logradouro:
								numero = [v for v in logradouro.split(' N°')[-1].replace('.','').replace(',','').split() if v.isdigit()][0]
								logradouro = logradouro[:logradouro.index(' N°')]
							elif ' NO.' in logradouro:
								numero = [v for v in logradouro.split(' NO.')[-1].replace('.','').replace(',','').split() if v.isdigit()][0]
								logradouro = logradouro[:logradouro.index(' NO.')]
							else:
								numero = [v for v in texto[1].replace('.','').split() if v.isdigit()][0]
							break
					
					except IndexError:
						texto = [a.split('.') for a in texto]
						texto = [a for b in texto for a in b]
						for x in texto:
							try:
								nlista = [v for v in x if v.isdigit()]
								if any(nlista):
									numero = ''.join(nlista)
									break
								else:
									continue
							except IndexError:
								continue
						if numero and numero[0] in logradouro:
							logradouro = logradouro[:logradouro.index(numero[0])].strip()
						for x in (' Nº',' N.',' N°',' NO.'):
							logradouro = logradouro.replace(x,'')

					endfinal = str(logradouro+', '+numero)
					endfinal = endfinal.replace(r'\N','').replace('\n','')
					self.dic['Endereço'] = endfinal
					break
			except:
				if termo in self.resumo:
					self.dic['Ref Endereço'] = 'Sim'
				continue

	# função para encontrar sentenças
	def sentencas(self,dic):
		assert type(dic) == dict

		# Encontra as sentenças
		self.dic["Sentença"] = ''
		self.dic["Contagem sentenças"] = ''
		sentencas = []

		try:
			for chave, valor in dic.items():
				if chave in self.resumo:
					sentencas += [valor]
			if len(sentencas) == 0:
				for tipo in ("JULGO EXTINTA","JULGA-SE EXTINTA","JULGAR EXTINTA", "EXTINGO"):
					if tipo in self.resumo:
						sentencas += ['Extinção']
						break

			# Escreve o texto das sentenças
			textosentencas = ', '.join(sentencas)
			self.dic["Sentença"] = textosentencas
			self.dic["Contagem sentenças"] = len(sentencas)
		except:
			pass

	# faz consulta avançada do processo (desativado)
	def busca_avancada(self):
		self.dic["Situação"] = ''
		self.dic["Valor da ação (R$)"] = ''
		self.dic["Data distribuição"] = ''
		self.dic["Dias em tramitação"] = ''
		dt = {}
		for x in range(5):
			try:
				assert self.dic["Processo"]
				n = str(self.dic["Processo"])
				sessao2 = requests.Session()
				r = sessao2.get('https://esaj.tjsp.jus.br/cpopg/open.do',verify=False)
				
				try:
					cookie = list(r.cookies)[0].value
					req = 'https://esaj.tjsp.jus.br/cpopg/search.do;jsessionid='+cookie+'?conversationId=&dadosConsulta.localPesquisa.cdLocal=-1&cbPesquisa=NUMPROC&dadosConsulta.tipoNuProcesso=UNIFICADO&numeroDigitoAnoUnificado='+n[0:15]+'&foroNumeroUnificado='+n[-4:]+'&dadosConsulta.valorConsultaNuUnificado='+n+'&dadosConsulta.valorConsulta=&uuidCaptcha='
					assert r.ok
					assert r.cookies
				except AssertionError:
					req = 'https://esaj.tjsp.jus.br/cpopg/search.do?conversationId=&dadosConsulta.localPesquisa.cdLocal=-1&cbPesquisa=NUMPROC&dadosConsulta.tipoNuProcesso=UNIFICADO&numeroDigitoAnoUnificado='+n[0:15]+'&foroNumeroUnificado='+n[-4:]+'&dadosConsulta.valorConsultaNuUnificado='+n+'&dadosConsulta.valorConsulta=&uuidCaptcha='
				
				r = sessao2.get(req,verify=False)
				assert r.ok
				sopa = BeautifulSoup(r.content,'html.parser').find_all('table',{"class":"secaoFormBody"})[1]
				sessao2.close()

				try:
					self.dic["Situação"] = sopa.find('span',{'style':'color: red; padding-left: 6px;'}).get_text()
				except AttributeError:
					pass
				
				for a in sopa.find_all('tr'):
					try:
						x = a.find_all('td')
						if len(x)==2:
							dt[x[0].get_text().replace('\n','')] = x[1].get_text().replace('\n','')
					except:
						continue

				try:
					valoracao = [int(v) for v in dt['Valor da ação:'].replace('.','').replace(',','').split() if v.isdigit()][0]/100
					self.dic["Valor da ação (R$)"] = str(valoracao).replace('.',',')
				except:
					pass
				try:
					self.dic["Data distribuição"] = dt['Distribuição:'][:10]
				except:
					pass
				try:
					abertura = [int(x) for x in self.dic["Data distribuição"].split('/')]
					fim = [int(x) for x in self.dic["Data de Disponibilização"].split('/')]
					delta = datetime.date(fim[2],fim[1],fim[0]) - datetime.date(abertura[2],abertura[1],abertura[0])
					delta = int(delta.days)
					if delta < 0:
						delta = 0
					self.dic["Dias em tramitação"] = str(delta)
				except:
					pass
				self.avancado = True
				break
			except:
				self.avancado = False
				try:
					sessao2.close()
				except:
					pass


'''
FUNÇÃO EXECUTAR
Objeto de execução de busca
Pode ser configurado por parâmetros ou pelo método configurar()
Utilizado na função cumprir
'''
def executar(pesquisa):
	print('[portas] Iniciando execução')
	# variáveis de execução
	tamanho_fila = pesquisa.ciclo//10
	timeout = pesquisa.robos * 90	
	contagem = ignorados = 0

	# providencia nome do arquivo
	dir_out = os.path.dirname(pesquisa.arq)
	basename = os.path.basename(pesquisa.arq)
	rivais = os.listdir(dir_out)
	csv_rivais = [x.replace('_resultados.csv','') \
		for x in rivais if x.endswith('_resultados.csv')]
	csv_rivais = [x for x in csv_rivais\
		if x.startswith(basename) and (len(basename)==(len(x)-4)\
		or len(basename)==(len(x)-5))]
	lc = len(csv_rivais)
	if basename+'_resultados.csv' in os.listdir(dir_out):
		lc += 1

	portas_rivais = [x.replace('.portas','') for x in rivais if x.endswith('.portas')]
	portas_rivais = [x for x in portas_rivais\
		if x.startswith(basename) and (len(basename)==(len(x)-4) or len(basename)==(len(x)-5))]
	lp = len(portas_rivais)
	if basename+'.portas' in os.listdir(dir_out):
		lp += 1

	n_rivais = max(lc,lp)
	if n_rivais == 0:
		sufixo = ''
	else:
		sufixo = ' ({})'.format(str(n_rivais))

	nome_out = pesquisa.arq + sufixo
	nowiso = str(datetime.datetime.now().isoformat())
	nowisohash = hashlib.sha1(nowiso.encode('utf-8')).hexdigest()[:10]
	csv_int = nome_out + nowisohash + '.csv'
	csv_out = nome_out + '_resultados.csv'
	portas_out = nome_out + '.portas'
	txt_out = nome_out + '.txt'
	zip_out = nome_out + '.zip'

	if pesquisa.retomada and pesquisa.original:
		_extrair_csv(pesquisa.original,csv_int)
		ctypes.windll.kernel32.SetFileAttributesW(csv_int, 2)

	# define página de início
	i_pag = (pesquisa.indice//10)+1
	pag1 = i_pag
	i_inicio = pesquisa.indice%10
	inicio = True
	tarefas = queue.Queue()

	# configura dicionários de mineração
	masterdic = {}
	for d in os.listdir(_dics):
		nome = d.replace('.txt','')
		d = _ler_dic(os.path.join(_dics,d))
		masterdic[nome] = d

	mastercustom = {}
	if pesquisa.dics:
		for d in os.listdir(pesquisa.dics):
			nome = d.replace('.txt','')
			d = _ler_dic(os.path.join(pesquisa.dics,d))
			mastercustom[nome] = d
	else:
		mastercustom = None

	'''
	FUNÇÃO _ROBO
	Componente de multiprocessamento
	Utilizada internamente na função cumprir
	'''
	def _robo(tarefas,matriz,parciais,cadeado,cadeado2,cod):
		bandeira = False
		prefixo = '[portas._robo #{}] '.format(str(cod+1))
		while not tarefas.empty():
			tarefa = tarefas.get()
			partida = datetime.datetime.now()
			
			cadeado2.acquire()
			if pesquisa.limite:
				if parciais.count('contagem')>pesquisa.limite:
					cadeado2.release()
					tarefas.task_done()
					continue
			if bandeira:
				cadeado2.release()
				tarefas.task_done()
				continue
			cadeado2.release()

			try:
				# solicita dados de mudança de página
				ts = prefixo+'Acessando página '+str(tarefa)+'\t'
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
					ts = prefixo+'\nO servidor levou tempo demais para responder. A execução será terminada em breve.\n'
					print(ts)
					cadeado2.acquire()
					parciais.append('terminar')
					cadeado2.release()
					tarefas.task_done()
					continue

				# checa se página tem conteúdo
				if len(itens_na_pagina) == 0:
					ts = prefixo+'Página '+str(tarefa)+' vazia!'
					print(ts)
					bandeira = True
					continue

				# se for a primeira busca, define o primeiro item a partir 
				if tarefa == pag1:
					itens_na_pagina = itens_na_pagina[i_inicio:]

				# loop de mineração dos itens na página
				for itemhtml in itens_na_pagina:
					try:
						u = itemregistro(itemhtml)

						u.partes()
						u.buscaralvo('Razão parte 1', masterdic['razao'], u.parte1)
						u.buscaralvo('Razão parte 2', masterdic['razao'], u.parte2)
						u.contarparte('Parte 2 múltipla',u.dic['Parte 2'])
						u.buscaralvo('Grupo parte 1', masterdic['grupo'], u.dic['Parte 1'])
						u.buscaralvo('Grupo parte 2', masterdic['grupo'], u.dic['Parte 2'])
									
						if u.dic['Grupo parte 1'] == 'Instituição financeira':
							u.buscaralvo('Descrição parte 1',masterdic['financeiros'], u.dic['Parte 1'])
						elif u.dic['Grupo parte 1'] == 'Autarquia/Empresa pública':
							u.buscaralvo('Descrição parte 1',masterdic['autarquias'], u.dic['Parte 1'])
						elif u.dic['Grupo parte 1'] == 'Estado':
							u.buscaralvo('Descrição parte 1',masterdic['estado'], u.dic['Parte 1'])
						else:
							u.campovazio('Descrição parte 1')

						u.buscaralvo('RAJ',masterdic['rajs'],u.dic["Comarca"])
						u.buscaralvo('Justiça gratuita',{'Sim':["\nJUSTIÇA GRATUITA\n"]},u.resumo)
						u.aluguel()
						u.endereco()
						u.sentencas(masterdic['sentencas'])

						# executa template, se houver
						if mastercustom:
							for tema, termos in mastercustom.items():
								u.buscaralvo(tema,termos,u.resumo)

						# executa busca avançada (desativado)
						if pesquisa.completa:
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

					# ignora item se houver erro na execução
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
				ts = prefixo+'Página '+str(tarefa)+' registrada!\t'
				print(ts)
					
			except:
				cadeado2.acquire()
				parciais.append('terminar')
				cadeado2.release()
				tarefas.task_done()
				break

			tarefas.task_done()

	try:
		c = 1
		while True:
			if pesquisa.limite and contagem >= pesquisa.limite:
				print('[portas] Pesquisa chegou ao limite!\n')
				break

			matriz = []
			parciais = []
			cadeado_A = threading.Lock()
			cadeado_B = threading.Lock()

			print('[portas] Iniciando execução do ciclo',str(c))

			for pag in range(i_pag,i_pag+tamanho_fila):
				tarefas.put(pag)

			# distribui trabalho para os estagiários
			for a in range(pesquisa.robos):
				trabalho = threading.Thread(target=_robo,args=(tarefas,matriz,parciais,cadeado_A,cadeado_B,a))
				trabalho.daemon = True
				trabalho.start()

			tarefas.join()
			print('[portas] Juntando tarefas...\n')

			# analisa continuação da execução
			if 'terminar' in parciais:
				print('[portas] Um erro inesperado ocorreu. Fechando a pesquisa...')
				break

			if parciais.count('erroavancado') > 0.9 * parciais.count('contagem'):
				print('[portas] A busca avançada não retornou os resultados esperados!')
				print('[portas] Finalizando pesquisa...')
				break

			# limpa matriz de resultados
			matriz = [x for x in matriz if type(x) is dict]
			chaves = matriz[0].keys()
			print('[portas] Matriz ok!')

			# cria arquivos se for início de execução
			if inicio and pesquisa.retomada==False:
				with open(csv_int, 'w', encoding = "utf-8", newline='') as saida:
					dict_writer = csv.DictWriter(saida,chaves,delimiter='|')
					dict_writer.writeheader()
				ctypes.windll.kernel32.SetFileAttributesW(csv_int, 2)
				print('[portas] Despacho criado!')

			# Salva os dados no arquivo de saída
			with open(csv_int, 'a', encoding = "utf-8",newline='') as saida:
				dict_writer = csv.DictWriter(saida,chaves,delimiter='|')
				dict_writer.writerows(matriz)
			print('[portas] Dados anexados ao despacho!')

			print('[portas]',len(matriz),"processos salvos!\n")
			inicio = False
			ignorados += parciais.count('ignorado')
			pesquisa.ignorados += ignorados
			contagem += parciais.count('contagem')
			i_pag += parciais.count('pagina')

			if 'bandeira' in parciais:
				print('[portas] TODOS OS DADOS DISPONÍVEIS FORAM RASPADOS!')
				break

			yield contagem
			c += 1

	finally:
		if inicio:
			print('[portas] Nenhum item foi registrado!')
		# salva o arquivo de metadados
		relato = relatar(pesquisa,contagem)
		with open(txt_out,'w',encoding='utf-8') as relatorio:
			relatorio.write(relato)
		# desoculta arquivos
		ctypes.windll.kernel32.SetFileAttributesW(csv_int, 128)

		# maneja os arquivos finais
		zip_final = zipfile.ZipFile(zip_out,'w',ZIP_DEFLATED)
		zip_final.write(txt_out, 'meta.txt')
		zip_final.write(csv_int, 'data.csv')
		if pesquisa.dics:
			for file in os.listdir(pesquisa.dics):
				if file.endswith('.txt'):
					n = os.path.basename(file)
					zip_final.write(pesquisa.dics+'\\'+file, 'template\\'+file)
		zip_final.close()
		os.remove(txt_out)
		try:
			os.remove(pesquisa.arq+'resultados.csv')
		except OSError:
			pass
		os.rename(csv_int, csv_out)
		os.rename(zip_out, portas_out)

		if pesquisa.salvar_xlsx:
			_trocar_csv(csv_out)

		# Dá o aviso de finalização da execução
		print("[portas] Raspagem finalizada!")
		print("         Itens registrados:", contagem - ignorados)
		print("         Itens ignorados:", ignorados)
		print("         Itens já registrados na pesquisa:",pesquisa.indice + contagem)