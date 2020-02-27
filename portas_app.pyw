#!/usr/bin/env python3.7
### LabCidados.py ###

# importa módulos
import sys
import os
import csv
import requests
import time
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
templates = os.listdir(_parent+'/templates')
templates = [x for x in templates if \
	os.path.isdir(_parent+'/templates/'+x)]

# cria variáveis do programa
_parent = os.path.dirname(os.path.realpath(__file__))
esaj = 'https://esaj.tjsp.jus.br/cjpg/'
qtCreatorFile = 'gui/portas.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

# thread de raspagem, separado da interface
class progressThread(QtCore.QThread):
	progress_update = QtCore.pyqtSignal(int)

	def __init__(self):
		QtCore.QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		m = 0
		while m <= 100:
			print(m)
			m += 1
			'''
			if self.raspar.isChecked():
				self.raspar.setEnabled(False)
				self.progresso.setText('Interrompendo pesquisa...')
				break
			'''
			tot = 1
			self.progress_update.emit(tot)
			time.sleep(1)

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

		renome = QtCore.QRegExp('[^/:?|<>*"]{1,}')
		validanome = QtGui.QRegExpValidator(renome)
		self.pesquisa_nome.setValidator(validanome)

		# conexão de widgets a funções
		self.novap.clicked.connect(self.novapesquisa)
		self.atualizarp.clicked.connect(self.atualizarpesquisa)
		self.retomarp.clicked.connect(self.retomarpesquisa)
		self.browse_arq.clicked.connect(self.set_saida)
		self.browse_url.clicked.connect(self.abrir_navegador)
		self.captura_url.clicked.connect(self.set_url)
		self.pesquisa_nome.editingFinished.connect(self.checar)
		self.pesquisa_arq.editingFinished.connect(self.checar)
		self.pesquisa_url.editingFinished.connect(self.checar)
		self.novo_template.clicked.connect(self.criar_template)
		self.isDics.stateChanged.connect(self.ativar_templates)

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
				continue

		self.driver.find_element_by_xpath("//*[@value='Consultar']").click()
		url = self.driver.current_url
		self.driver.quit()

		if url:
			url = url.replace("ordenacao=DESC","ordenacao=ASC")
			self.pesquisa_url.clear()
			self.pesquisa_url.insert(url)
			self.captura_url.hide()
			self.checar()

	def criar_template(self):
		return

	def ativar_templates(self):
		if self.isDics.isChecked():
			self.labelDics.setEnabled(True)
			self.raspar_dics.setEnabled(True)
			self.raspar_dics.addItems(templates)
			self.novo_template.setEnabled(True)
		else:
			self.labelDics.setEnabled(False)
			self.raspar_dics.setEnabled(False)
			self.raspar_dics.clear()
			self.novo_template.setEnabled(False)

	def novapesquisa(self):
		self.reset()
		self.novap.setChecked(True)
		self.retomarp.setChecked(False)
		self.atualizarp.setChecked(False)
		self.box_pesquisa.setEnabled(True)
		self.labelNome.setEnabled(True)
		self.labelSaida.setEnabled(True)
		self.labelURL.setEnabled(True)
		self.pesquisa_nome.setEnabled(True)
		self.pesquisa_arq.setEnabled(True)
		self.browse_arq.setEnabled(True)
		self.pesquisa_url.setEnabled(True)
		self.browse_url.setEnabled(True)
		self.isCompleta.setEnabled(True)
		self.isDics.setEnabled(True)
		self.raspar_dics.setEnabled(False)
		self.labelDics.setEnabled(False)

	def atualizarpesquisa (self):
		self.reset()
		self.novap.setChecked(False)
		self.retomarp.setChecked(False)
		self.atualizarp.setChecked(True)

	def retomarpesquisa (self):
		self.reset()
		self.novap.setChecked(False)
		self.retomarp.setChecked(True)
		self.atualizarp.setChecked(False)

	def reset(self):
		self.sucesso.hide()
		self.erroUrl.hide()
		self.progresso.hide()
		self.barraProgresso.setValue(0)
		self.novap.setEnabled(True)
		self.retomarp.setEnabled(True)
		self.atualizarp.setEnabled(True)
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

	def atualizar_progresso(self, tot):
		self.barraProgresso.setValue(self.barraProgresso.value() + tot)
		if tot == 0:
			self.barraProgresso.setValue(100)

	def executar (self):
		self.raspar.setEnabled(False)
		self.novap.setEnabled(False)
		self.retomarp.setEnabled(False)
		self.atualizarp.setEnabled(False)
		self.progresso.show()
		self.progresso.setText('Checando URL...')
		time.sleep(1)
		
		try:
			s = requests.Session()
			r = s.get(self.pesquisa_url.text())
			h = BeautifulSoup(r.content,'html.parser')
			r2 = h.find_all('div',{'id':'resultados'})
			assert len(r2) > 0
		except AssertionError:
			self.progresso.hide()
			self.reset()
			self.erroUrl.show()	
			return

		# trava elementos
		self.box_pesquisa.setEnabled(False)
		self.box_config.setEnabled(False)
		time.sleep(1)

		# configura objeto de pesquisa
		self.progresso.setText('Iniciando pesquisa...')
		self.p = portas.pesquisa()
		self.p.nome = self.pesquisa_nome.text()
		self.p.arq = self.pesquisa_arq.text() + '/' + self.p.nome
		self.p.url = self.pesquisa_url.text()
		print(self.p.url)
		self.p.dics = _parent + '/templates/' + self.raspar_dics.currentText()
		if self.isCompleta.isChecked():
			self.p.completa = True
		#p.ciclo = 

		self.tot = 0
		self.raspar.clicked.disconnect(self.executar)
		self.raspar.setEnabled(True)
		self.raspar.setText('Interromper')
		self.raspar.setCheckable(True)
		self.raspar.setChecked(False)

		self.thread_progresso = progressThread()
		self.thread_progresso.start()
		self.thread_progresso.progress_update.connect(self.atualizar_progresso)

		self.reset()
		self.sucesso.show()

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = PortasApp()
	window.show()
	sys.exit(app.exec_())


#https://esaj.tjsp.jus.br/cjpg/pesquisar.do;jsessionid=ED4BC75A2998842CF3AE506708C49111.cjpg3?conversationId=&dadosConsulta.pesquisaLivre=&tipoNumero=UNIFICADO&numeroDigitoAnoUnificado=&foroNumeroUnificado=&dadosConsulta.nuProcesso=&dadosConsulta.nuProcessoAntigo=&classeTreeSelection.values=8554&classeTreeSelection.text=Despejo&assuntoTreeSelection.values=&assuntoTreeSelection.text=&agenteSelectedEntitiesList=&contadoragente=0&contadorMaioragente=0&cdAgente=&nmAgente=&dadosConsulta.dtInicio=&dadosConsulta.dtFim=&varasTreeSelection.values=&varasTreeSelection.text=&dadosConsulta.ordenacao=ASC