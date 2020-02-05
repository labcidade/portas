# classe de raspagem do item
class itemraspado:
	def __init__(self,item_em_html):
		self.dic = {}
		self.dados = item_em_html.find_all("tr")
		self.completo = True
		self.avancado = False
		horario = datetime.datetime.now().isoformat()
		dia = '/'.join(horario[:10].split('-')[::-1])
		hora = datetime.datetime.now().isoformat()[11:19]
		self.dic['Início raspagem'] = dia+' '+hora

		for a in ["Processo","Classe","Assunto","Magistrado","Comarca","Foro","Vara","Data de Disponibilização"]:
			self.dic[a] = ''

		# registra o número identificador do processo
		self.dic["Processo"] = limpar_html(self.dados[0])		

		# extrai a ficha com os dados principais do processo
		if len(self.dados) == 8:
			self.dic["Classe"]=''
			for tr in self.dados[1:7]:
				tr_limpo = limpar_html(tr).split(":")
				self.dic[tr_limpo[0].strip()] = tr_limpo[-1].strip()
		elif len(self.dados) == 9:
			for tr in self.dados[1:8]:
				tr_limpo = limpar_html(tr).split(":")
				self.dic[tr_limpo[0].strip()] = tr_limpo[-1].strip()
		else:
			self.completo =	False

		self.resumo = self.dados[-1].find_all("span")[-1].get_text().upper()
		self.dic["Comprimento resumo"] = len(self.resumo.replace("\n","").replace("\t",""))

	# função para procurar uma série de valores de dic em alvo e retornar chave para campo
	def buscaralvo(self,campo,dic,alvo):
		assert type(dic) == dict

		self.dic[campo] = ''
		for key, lista in dic.items():
			for termo in lista:
				if termo in alvo:
					self.dic[campo] = key
					break
			if self.dic[campo]:
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
						self.dic['Parte 1'] = limpar_lista(self.resumo[self.resumo.index(termo):].replace(":","").replace(";","").replace("(A)","").replace("(RÉ)","").replace("(ES)","").replace("(S)","").split(termo)[1].split("\n"))[0].strip()
						self.parte1 = self.dic['Parte 1'] + ' '
						break
			except AssertionError:
				break


		if self.dic['Tipo partes']:
			for termo in ("\nREQUERIDO","\nREQUERIDA","\nREQUERIDOS","\nREQUERIDAS","\nEMBARGADO","\nEMBARGADA","\nEMBARGADOS","\nEMBARGADAS","\nRÉU","\nRÉUS","\nRÉ"):
				if termo in self.resumo:
					self.dic['Parte 2'] = limpar_lista(self.resumo[self.resumo.index(termo):].replace(":","").replace(";","").replace("(A)","").replace("(RÉ)","").replace("(ES)","").replace("(S)","").split(termo)[1].split("\n"))[0].strip()
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
			for key, lista in dic.items():
				for termo in lista:
					if termo in self.resumo:
						sentencas += [key]
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

	# faz consulta avançada do processo
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

# função para raspar conforme pesquisa
def raspar(pesquisa):
	divisor('linhadupla')
	print('INICIANDO RASPAGEM DOS DADOS...')
	print('')
	assert type(pesquisa).__name__ == 'pesquisa'

	# definição da distribuição de processos
	print('\nEm seguida devem ser especificados os parâmetros para execução simultânea da raspagem.\nPara mais informações, leia o arquivo INSTRUCOES.txt, que acompanha o programa.')
	while True:
		try:
			n_estagiarios = int(input('\nQuantidade de threads/robôs: '))
			break
		except:
			print('O valor inserido não é um número! Tente novamente.')
			continue
	while True:
		try:
			tamanho_fila = int(input('\nTamanho do ciclo: '))//10
			break
		except:
			print('O valor inserido não é um número! Tente novamente.')
			continue

	timeout = n_estagiarios * 90	
	requests.packages.urllib3.disable_warnings()
	contagem = ignorados = 0
	i_pag = (pesquisa.indice_raspagem//10)+1
	pag1 = i_pag
	i_inicio = pesquisa.indice_raspagem%10
	inicio = True
	tarefas = queue.Queue()

	dic_financeiros = {
	'Banco Itaú':['ITAU','ITAÚ','UNIBANCO'],
	'Banco Bradesco':['BRADESCO'],
	'Banco do Brasil':['BANCO DO BRASIL'],
	'Finasa':['FINASA'],
	'Banco Safra':['SAFRA'],
	'Banco Santander':['SANTANDER'],
	'SOFISA':['SOFISA'],
	'BMG':['BMG'],
	'Banco Panamericano':['PANAMERICANO'],
	'Banco Rodobens':['RODOBENS'],
	'Tricury':['TRICURY'],
	'Banco Volkswagen':['VOLKSWAGEN'],
	'HSBC':['HSBC'],
	'BFB Leasing':['BFB']
	}

	dic_autarquias = {
	'Cohab':['COHAB'],
	'CDHU':['CDHU'],
	'Metrô':['METRÔ'],
	'CPTM':['CPTM'],
	'Sabesp':['SABESP'],
	'SPObras':['SPOBRAS'],
	'Dersa':['DERSA'],
	'DER-SP':["ESTRADAS DE RODAGEM","ESTRADAS E RODAGEM"],
	'EMTU':["EMTU","EMPRESA METROPOLITANA DE TRANSPORTES URBANOS"],
	'Petrobrás':["PETROBRÁS","PETROBRAS"]
	}

	dic_estado = {
	'Estado de São Paulo':["ESTADO DE SÃO PAULO","ESTADO DE SAO PAULO","FAZENDA DO ESTADO"],
	'Município':["PREFEITURA","MUNICIPALIDADE","MUNICÍPIO","MUNICIPIO"]
	}

	dic_sentencas = {
	'Procedente':["JULGO PROCEDENTE","JULGA-SE PROCEDENTE","JULGAR PROCEDENTE"],
	'Improcedente':["JULGO IMPROCEDENTE","JULGA-SE IMPROCEDENTE","JULGAR IMPROCEDENTE"],
	'Homologação':["HOMOLOGO"]
	}

	dic_usos = {
	'Industrial':["GALPÃO INDUSTRIAL","USO INDUSTRIAL","ATIVIDADE INDUSTRIAL","SALÃO INDUSTRIAL","VILA INDUSTRIAL"],
	'Comercial':["IMÓVEL COMERCIAL","LOCAÇÃO COMERCIAL","USO COMERCIAL","NATUREZA COMERCIAL"],
	'Não residencial':["NÃO RESIDENCIAL"],
	'Residencial':["IMÓVEL RESIDENCIAL","USO RESIDENCIAL","LOCAÇÃO RESIDENCIAL","FIM RESIDENCIAL","CONTRATO RESIDENCIAL","LOCATÍCIO RESIDENCIAL","NATUREZA RESIDENCIAL","MORADIA"]
	}


	# executa a pesqisa
	try:
		while True:
			if pesquisa.limite and contagem >= pesquisa.limite:
				print('Pesquisa chegou ao limite!\n')
				divisor('linhadupla')
				break

			matriz = []
			parciais = []
			cadeado = threading.Lock()
			cadeado2 = threading.Lock()

			divisor()
			print('Iniciando raspagem do próximo ciclo de páginas')

			for pag in range(i_pag,i_pag+tamanho_fila):
				tarefas.put(pag)

			# distribui trabalho para os estagiários
			divisor()
			print('Distribuindo tarefas...\n')
			if __name__ == '__main__':
				for a in range(n_estagiarios):
					trabalho = threading.Thread(target=estagiario,args=(tarefas,matriz,parciais,cadeado,cadeado2))
					trabalho.daemon = True
					trabalho.start()
			else:
				print('Divisão de threads não autorizada!')
				raise Exception

			tarefas.join()
			divisor('tracejado')
			print('Juntando tarefas...\n')

			if 'terminar' in parciais:
				divisor('linhadupla')
				print('Um erro inesperado ocorreu. Fechando a pesquisa...')
				divisor('linhadupla')
				break

			if parciais.count('erroavancado') > 0.9*parciais.count('contagem'):
				divisor('linhadupla')
				print('A busca avançada não retornou os resultados esperados!')
				print('Finalizando pesquisa...')
				divisor('linhadupla')
				break

			matriz = [x for x in matriz if type(x) is dict]

			if inicio:
				chaves = matriz[0].keys()
				if pesquisa.pesquisanova:
					with open(pesquisa.despacho, 'w', encoding = "utf-8",newline='') as saida:
						dict_writer = csv.DictWriter(saida,chaves,delimiter='|')
						dict_writer.writeheader()
						dict_writer.writerows(matriz)
					ctypes.windll.kernel32.SetFileAttributesW(pesquisa.despacho, 2)
				else:
					inicio = False

			# Salva os dados em arq_final
			if not inicio:
				with open(pesquisa.despacho, 'a', encoding = "utf-8",newline='') as saida:
					dict_writer = csv.DictWriter(saida,chaves,delimiter='|')
					dict_writer.writerows(matriz)

			print(len(matriz),"processos raspados e salvos!\n")
			inicio = False
			pesquisa.ignorados += parciais.count('ignorado')
			ignorados += parciais.count('ignorado')
			contagem += parciais.count('contagem')
			i_pag += parciais.count('pagina')

			if 'bandeira' in parciais:
				print('TODOS OS DADOS DISPONÍVEIS FORAM RASPADOS!')
				divisor('linhadupla')
				break

			continue

	finally:
		if inicio:
			print('Nenhum item foi raspado!')
		# salva o arquivo de metadados
		relato = 'Nome da pesquisa: '+pesquisa.nomepesquisa.upper()+'\n\nItens pesquisados: '+str(contagem+pesquisa.indice_raspagem)+'\nItens ignorados: '+str(pesquisa.ignorados)+'\nItens registrados: '+str(contagem+pesquisa.indice_raspagem-pesquisa.ignorados)+'\n\nurl: '+str(pesquisa.url)

		with open(pesquisa.relatorio,'w') as relatorio:
			relatorio.write(relato)
			print('O relatório da pesquisa foi salvo\n')

		# desoculta arquivos
		ctypes.windll.kernel32.SetFileAttributesW(pesquisa.despacho, 128)

		# maneja os arquivos finais
		if not pesquisa.pesquisanova:
			os.remove(pesquisa.arq_final)

		zip_final = zipfile.ZipFile(pesquisa.arq_final,'w')
		zip_final.close()

		zip_final = zipfile.ZipFile(pesquisa.arq_final,'a')
		zip_final.write(pesquisa.relatorio, os.path.basename(pesquisa.relatorio))
		zip_final.write(pesquisa.despacho, os.path.basename(pesquisa.despacho))
		zip_final.close()

		os.remove(pesquisa.relatorio)
		try:
			os.remove(pesquisa.pasta_final+'/TJSP_Resultados_'+pesquisa.nomepesquisa+'.csv')
		except OSError:
			pass

		os.rename(pesquisa.despacho, pesquisa.pasta_final+'/TJSP_Resultados_'+pesquisa.nomepesquisa+'.csv')
		os.rename(pesquisa.arq_final, pesquisa.robnada_final)

		# Dá o aviso de finalização da raspagem
		divisor('linhadupla')
		print("Raspagem finalizada!")
		print("Itens raspados:", contagem - ignorados)
		print("Itens ignorados:", ignorados)
		print("Itens já raspados na pesquisa:",pesquisa.indice_raspagem+contagem)
		divisor()
			
		# mantém o prompt aberto
		input('Aperte enter para fechar!')


# EXECUÇÃO DA RASPAGEM

p=pesquisa()
p.configurar()
raspar(p)