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
import shutil
from zipfile import ZipFile, ZIP_DEFLATED
from bs4 import BeautifulSoup
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory


def _worker(tarefas,matriz,parciais,cadeado,cadeado2,cadeado3,cod):
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
                    itens_na_pagina = []

                    # realiza pesquisa em pasta local
                    if pesquisa.espelho:
                        repfile = '{0}/{1}.html'.format(pesquisa.espelho, str(tarefa))
                        if os.path.isfile(repfile):
                            with open(repfile,'rb') as rephtml:
                                itens_na_pagina = [a for a in BeautifulSoup(rephtml,'html.parser').find_all("tr",{"class":"fundocinza1"})[:10]]
                            if len(itens_na_pagina) < 10:
                                itens_na_pagina = []

                    # realiza pesquisa na internet
                    if not itens_na_pagina:
                        while True:
                            sessao = requests.Session()
                            sessao.trust_env=False
                            resposta = sessao.get(pesquisa.url,verify=False)
                            pagina = sessao.get('https://esaj.tjsp.jus.br/cjpg/trocarDePagina.do?pagina='+str(tarefa)+'&conversationId=',verify=False)
                            pag_soup = BeautifulSoup(pagina.content,'html.parser')
                            assert pagina.text != '\nSessão Expirada\n' and pagina.ok
                            sessao.close()
                        
                            tottentativa = _achar_proctot(pag_soup)
                            if tottentativa < proctot:
                                agora = datetime.datetime.now()
                                if (agora-partida).total_seconds() > timeout:
                                    itens_na_pagina = 1
                                    break
                                continue
                            else:
                                itens_na_pagina = [a for a in pag_soup.find_all("tr",{"class":"fundocinza1"})[:10]]
                                break

                        # salva os dados da página
                        _t, _u, _f = shutil.disk_usage('/')
                        if pesquisa.espelho and _f//(2**30) > 1 and len(itens_na_pagina) > 0:
                            html_out = '{0}/{1}.html'.format(pesquisa.espelho, str(tarefa))
                            cadeado3.acquire()
                            with open(html_out,'wb') as htmlfile:
                                htmlfile.write(pagina.content)
                            cadeado3.release()
                    break
                except AssertionError:
                    agora = datetime.datetime.now()
                    if (agora-partida).total_seconds() > timeout:
                        itens_na_pagina = 2
                        break
                    else:
                        continue

            # checa se página tem conteúdo
            if itens_na_pagina == 2:
                ts = prefixo+'\nO servidor levou tempo demais para responder. A execução será terminada em breve.\n'
                print(ts)
                cadeado2.acquire()
                parciais.append('terminar')
                cadeado2.release()
                tarefas.task_done()
                continue
            elif itens_na_pagina == 1:
                tarefas.task_done()
                continue

            # checa se página tem conteúdo
            if len(itens_na_pagina) == 0:
                ts = prefixo+'Página '+str(tarefa)+' vazia!'
                print(ts)
                cadeado2.acquire()
                bandeira = True
                parciais.append('bandeira')
                cadeado2.release()
                tarefas.task_done()
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
                    u.buscaralvo('UTA',masterdic['utas'],u.dic["Foro"])
                    u.buscaralvo('Justiça gratuita',{"\nJUSTIÇA GRATUITA\n":'Sim'},u.resumo)
                    u.buscaralvo('Prioridade idoso',{"PRIORIDADE IDOSO":"Sim"},u.resumo)
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
                            cadeado2.acquire()
                            parciais.append('erroavancado')
                            cadeado2.release()

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

class pesquisa:
    '''
    Realiza o donwload dos dados de processos
    '''
    def __init__(self):
        pass

    def update(self):

    