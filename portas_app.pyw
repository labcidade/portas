#!/usr/bin/env python3.7
### portas_app.py ###

# importa módulos
import sys
import os
import csv
import requests
import time
import shutil
from selenium import webdriver
from dbfread import DBF
from string import Template
from io import StringIO
from zipfile import ZipFile, ZIP_DEFLATED
from tkinter import Tk
from tkinter.filedialog import askopenfilenames, askdirectory
from bs4 import BeautifulSoup
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# define a pasta local
_parent = os.path.dirname(os.path.realpath(__file__))
os.chdir(os.path.dirname(os.path.realpath(__file__)))
from portas import portas

# lista templates
_templates_dir = _parent+'/templates'
templates = os.listdir(_templates_dir)
templates = [x for x in templates if \
	os.path.isdir(_templates_dir+'/'+x)]

# cria variáveis do programa
esaj = 'https://esaj.tjsp.jus.br/cjpg/'
qtCreatorFile = 'gui/portas.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

# thread de raspagem, separado da interface
class progressThread(QtCore.QThread):
	progress_update = QtCore.pyqtSignal(int)

	def __init__(self,gen):
		QtCore.QThread.__init__(self)
		self.gen = gen

	def run(self):
		while True:
			try:
				tot = next(self.gen)
				print(tot)
				self.progress_update.emit(tot)
				time.sleep(0.25)
				continue
			except StopIteration:
				break

		self.gen.close()
		self.finished.emit()
		#self.quit()


# classe de interface
class PortasApp(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.sucesso.hide()
		self.erroUrl.hide()
		self.captura_url.hide()
		self.progresso.hide()
		self.isCompleta.hide()
		self.dic_desc.hide()
		self.d = {}
		self.anterior = None

		renome = QtCore.QRegExp('[^/:?|<>*"]{1,}')
		validanome = QtGui.QRegExpValidator(renome)
		self.pesquisa_nome.setValidator(validanome)

		# conexão de widgets a funções
		self.novap.clicked.connect(self.novapesquisa)
		self.retomarp.clicked.connect(self.retomarpesquisa)
		self.extrairp.clicked.connect(self.extrairpesquisa)
		self.browse_arq.clicked.connect(self.set_saida)
		self.browse_url.clicked.connect(self.abrir_navegador)
		self.captura_url.clicked.connect(self.set_url)
		self.pesquisa_nome.editingFinished.connect(self.checar)
		self.pesquisa_arq.editingFinished.connect(self.checar)
		self.pesquisa_url.editingFinished.connect(self.checar)
		self.novo_template.clicked.connect(self.criar_template)
		self.isDics.stateChanged.connect(self.ativar_templates)
		self.isLimite.stateChanged.connect(self.ativar_limite)
		self.isCustom.stateChanged.connect(self.ativar_custom)
		self.raspar_dics.currentTextChanged.connect(self.resumir_template)

	def checar(self):
		try:
			assert os.path.isdir(self.pesquisa_arq.text())
			assert len(self.pesquisa_nome.text()) > 0
			assert len(self.pesquisa_url.text()) > 0
			assert self.pesquisa_url.text().startswith(esaj)
			assert len(self.pesquisa_url.text()) > len(esaj)
			self.raspar.setEnabled(True)

		except AssertionError:
			self.raspar.setEnabled(False)
			self.sucesso.hide()
			self.erroUrl.hide()
			pass

	def set_saida(self):
		d = portas._achar_pasta()
		if d:
			self.pesquisa_arq.clear()
			self.pesquisa_arq.insert(d)
			self.rol_destino = os.listdir(d)
			self.checar()

	def abrir_navegador(self):
		fbin = webdriver.firefox.firefox_binary.FirefoxBinary(\
			r'recursos/FirefoxPortable/App/Firefox/firefox.exe')
		self.driver = webdriver.Firefox(\
			executable_path=r"recursos/geckodriver_win32.exe",\
			firefox_binary=fbin)
		self.driver.get(esaj)
		self.captura_url.show()
		self.captura_url.setEnabled(True)

	def set_url(self):
		while True:
			try:
				self.driver.find_element_by_xpath("//*[@value='Consultar']")
				break
			except:
				self.captura_url.hide()
				return

		self.driver.find_element_by_xpath("//*[@value='Consultar']").click()
		url = self.driver.current_url
		self.driver.quit()

		if url:
			url = url.replace("ordenacao=DESC","ordenacao=ASC")
			self.pesquisa_url.clear()
			self.pesquisa_url.insert(url)
			self.captura_url.hide()
			self.checar()

	def resumir_template(self):
		self.dic_desc.clear()
		if self.isDics.isChecked() and\
			len(self.raspar_dics.currentText())>0:
			self.dic_desc.show()
			ltexto = []
			tpath = _templates_dir + '/' + self.raspar_dics.currentText()
			for file in os.listdir(tpath):
				limpo = file.replace('.txt','')
				ltexto.append(limpo)
			var = ', '.join(ltexto)
			texto = 'Variáveis: {}'.format(var)
			self.dic_desc.setText(texto)
		else:
			self.dic_desc.hide()

	def criar_template(self):
		pasta = portas._achar_pasta()
		try:
			assert pasta
			nome = os.path.basename(pasta)
			sinal = portas._template_ok(pasta)
			assert sinal
			print('Criando template...')
			destino = _templates_dir+'/'+nome
			if os.path.isdir(destino):
				odics = os.listdir(pasta)
				odics.sort()
				ddics = os.listdir(destino)
				ddics.sort()
				if ddics == odics:
					print('Template já existe')
					return
				else:
					rivais = [x for x in templates if x.startswith(nome)]
					r1 = ['_'.join(x.split('_')[:-1]) for x in rivais if '_' in x and x.split('_')[-1].isdigit()]
					r2 = [x for x in rivais if '_' not in x]
					rivais = r1+r2
					nrivais = rivais.count(nome)
					destino = destino + '_' + str(nrivais)
					nome = nome + '_' + str(nrivais)

			shutil.copytree(pasta,destino)
			templates.append(nome)
			self.ativar_templates()
			self.raspar_dics.setCurrentText(nome)
			print('Template criado!')
		except:
			print("Impossível criar template")
			return
		
	def ativar_templates(self):
		if self.isDics.isChecked():
			self.labelDics.setEnabled(True)
			self.raspar_dics.setEnabled(True)
			self.raspar_dics.clear()
			self.raspar_dics.addItems(templates)
			self.resumir_template()
			self.novo_template.setEnabled(True)
		else:
			self.labelDics.setEnabled(False)
			self.raspar_dics.setEnabled(False)
			self.raspar_dics.clear()
			self.resumir_template()
			self.novo_template.setEnabled(False)

	def ativar_configs(self):
		self.box_config.setEnabled(True)
		self.isLimite.setEnabled(True)
		self.isCustom.setEnabled(True)

	def ativar_limite(self):
		if self.isLimite.isChecked():
			self.pesquisa_limite.setEnabled(True)
			self.labelLimite.setEnabled(True)
		else:
			self.pesquisa_limite.setEnabled(False)
			self.labelLimite.setEnabled(False)
			self.pesquisa_limite.setValue(0)

	def ativar_custom(self):
		if self.isCustom.isChecked():
			self.labelRobos.setEnabled(True)
			self.labelCiclo.setEnabled(True)
			self.nrobos.setEnabled(True)
			self.nciclo.setEnabled(True)
		else:
			self.labelRobos.setEnabled(False)
			self.labelCiclo.setEnabled(False)
			self.nrobos.setEnabled(False)
			self.nciclo.setEnabled(False)
			self.nrobos.setValue(10)
			self.nciclo.setValue(500)

	def novapesquisa(self):
		self.reset()
		self.retomada = False
		self.novap.setChecked(True)
		self.retomarp.setChecked(False)
		self.box_pesquisa.setEnabled(True)
		self.labelNome.setEnabled(True)
		self.labelSaida.setEnabled(True)
		self.labelURL.setEnabled(True)
		self.pesquisa_nome.setEnabled(True)
		self.pesquisa_arq.setEnabled(True)
		self.browse_arq.setEnabled(True)
		self.pesquisa_url.setEnabled(True)
		self.browse_url.setEnabled(True)
		self.isDics.setEnabled(True)
		self.raspar_dics.setEnabled(False)
		self.labelDics.setEnabled(False)
		self.ativar_configs()

	def retomarpesquisa(self):
		self.reset()
		self.retomada = True
		self.novap.setChecked(False)
		self.retomarp.setChecked(True)
		self.box_pesquisa.setEnabled(True)
		self.labelSaida.setEnabled(True)
		self.pesquisa_arq.setEnabled(True)
		self.browse_arq.setEnabled(True)
		self.novo_template.setEnabled(False)
		self.ativar_configs()
		try:
			self.anterior, self.d = portas._achar_portas()
			assert self.anterior
		except:
			self.reset()
			return
		if self.d['template'] != '*':
			self.isDics.setChecked(True)
			t = portas._preparar_template(self.anterior,_templates_dir)
			self.ativar_templates()
			self.raspar_dics.setCurrentText(t)

		self.pesquisa_nome.clear()
		self.pesquisa_nome.insert(self.d['nome'])
		self.pesquisa_url.clear()
		self.pesquisa_url.insert(self.d['url'])

		self.labelNome.setEnabled(False)
		self.labelURL.setEnabled(False)
		self.pesquisa_nome.setEnabled(False)
		self.pesquisa_url.setEnabled(False)
		self.browse_url.setEnabled(False)
		self.isDics.setEnabled(False)
		self.raspar_dics.setEnabled(False)
		self.labelDics.setEnabled(False)

	def extrairpesquisa(self):
		self.reset()

	def reset(self):
		self.sucesso.hide()
		self.erroUrl.hide()
		self.progresso.hide()
		self.barraProgresso.setValue(0)
		self.novap.setEnabled(True)
		self.retomarp.setEnabled(True)
		self.novap.setChecked(False)
		self.retomarp.setChecked(False)
		self.pesquisa_nome.clear()
		self.pesquisa_arq.clear()
		self.pesquisa_url.clear()
		self.isCompleta.setChecked(False)
		self.isDics.setChecked(False)
		self.isLimite.setChecked(False)
		self.isCustom.setChecked(False)
		self.box_pesquisa.setEnabled(False)
		self.box_config.setEnabled(False)
		self.raspar.clicked.connect(self.executar)
		self.raspar.setText('Iniciar')
		self.raspar.setCheckable(False)
		self.raspar.setEnabled(False)
		self.pesquisa_limite.setValue(0)
		self.nrobos.setValue(10)
		self.nciclo.setValue(500)
		self.meta = 0
		self.anterior = None
		self.d = {}

	def atualizar_progresso(self, tot):
		porc = int((tot*100)/self.meta)
		self.barraProgresso.setValue(porc)
		tp = '{} de {} processos registrados'.format(str(tot),str(self.meta))
		print(tp)
		self.progresso.setText(tp)

	def finalizar(self):
		self.reset()
		self.raspar.clicked.connect(self.executar)
		self.novap.setChecked(False)
		self.retomarp.setChecked(False)
		self.novap.setEnabled(False)
		self.retomarp.setEnabled(False)
		self.extrairp.setEnabled(False)
		self.sucesso.show()

	def executar (self):
		print('Começando a execução')
		self.raspar.setChecked(False)
		self.raspar.setEnabled(False)
		self.novap.setEnabled(False)
		self.retomarp.setEnabled(False)
		self.extrairp.setEnabled(False)
		self.progresso.show()
		self.progresso.setText('Checando URL...')
		p = portas.pesquisa()
		
		print('Checando URL')
		try:
			s = requests.Session()
			r = s.get(self.pesquisa_url.text())
			h = BeautifulSoup(r.content,'html.parser')
			r2 = h.find_all('div',{'id':'resultados'})
			assert len(r2) > 0

			x = h.findAll('td',{'bgcolor':'#EEEEEE'})[-2].getText()
			x = x.split()[-1]
			print('Resultados contém {} processos'.format(x))
			self.meta = int(x)

		except AssertionError:
			self.progresso.hide()
			self.reset()
			self.erroUrl.show()	
			return

		# trava elementos
		print('Travando UI')
		self.box_pesquisa.setEnabled(False)
		self.box_config.setEnabled(False)
		time.sleep(1)

		# configura objeto de pesquisa
		self.progresso.setText('Iniciando pesquisa...')
		p.nome = self.pesquisa_nome.text()

		p.arq = self.pesquisa_arq.text() + '/' + p.nome
		p.url = self.pesquisa_url.text()
		print(p.url)
		if self.isDics.isChecked() and self.raspar_dics.currentText():
			p.dics = _parent + '/templates/' + self.raspar_dics.currentText()
		else:
			p.dics = None
		p.ciclo = self.nciclo.value()
		p.robos = self.nrobos.value()

		if self.retomada:
			p.retomada = True
			p.original = self.anterior
			p.indice = int(self.d['indice'])

		if self.isLimite.isChecked():
			p.limite = self.pesquisa_limite.value()
			self.meta = p.limite + p.indice
		else:
			p.limite = None

		self.raspar.clicked.disconnect(self.executar)
		self.raspar.setEnabled(False)
		time.sleep(2)
		
		gen = portas.executar(p)
		thread_progresso = progressThread(gen)
		thread_progresso.progress_update.connect(self.atualizar_progresso)
		thread_progresso.finished.connect(self.finalizar)
		thread_progresso.start()

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = PortasApp()
	window.show()
	sys.exit(app.exec_())
