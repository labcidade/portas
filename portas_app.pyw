#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

### portas_app.py ###

# define a pasta local
import os
_parent = os.path.dirname(os.path.realpath(__file__))
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# importa módulos
import install
import sys
import time
import shutil
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWebEngineWidgets import QWebEngineView
from portas import portas

ico = _parent+'\\gui\\icone_martelo.ico'

# lista templates
_templates_dir = _parent+'/templates'
templates = os.listdir(_templates_dir)
templates = [x for x in templates if \
	os.path.isdir(_templates_dir+'/'+x)]

# cria variáveis do programa
esaj = 'https://esaj.tjsp.jus.br/cjpg/'
qtCreatorFile = 'gui/portas.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

# thread de execução, separado da interface
class progressThread(QtCore.QThread):
	progress_update = QtCore.pyqtSignal(int)

	def __init__(self,gen):
		QtCore.QThread.__init__(self)
		self.gen = gen

	def run(self):
		while True:
			try:
				tot = next(self.gen)
				self.progress_update.emit(tot)
				time.sleep(0.25)
				continue
			except StopIteration:
				break

		self.gen.close()
		self.finished.emit()


class Browser(QWebEngineView):
	fechamento = QtCore.pyqtSignal()

	def __init__(self):
		QtCore.QThread.__init__(self)

	def closeEvent(self,event):
		self.fechamento.emit()
		event.accept()

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
		self.retomada = False

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
		self.min_dics.currentTextChanged.connect(self.resumir_template)

	def checar(self):
		try:
			assert os.path.isdir(self.pesquisa_arq.text())
			assert len(self.pesquisa_nome.text()) > 0
			assert len(self.pesquisa_url.text()) > 0
			assert self.pesquisa_url.text().startswith(esaj)
			assert len(self.pesquisa_url.text()) > len(esaj)
			self.fazer.setEnabled(True)

		except AssertionError:
			self.fazer.setEnabled(False)
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
		self.browser = Browser()
		self.browser.setWindowTitle('Realize uma consulta e capture a pesquisa na janela principal')
		self.browser.setWindowIcon(QtGui.QIcon(ico))
		self.browser.load(QtCore.QUrl(esaj))
		self.browser.fechamento.connect(self.set_url)
		self.browser.show()
		self.captura_url.show()
		self.captura_url.setEnabled(True)

	def set_url(self):
		try:
			url = self.browser.url()
			url = url.toString()
			assert url != esaj
			url = url.replace("ordenacao=DESC","ordenacao=ASC")
			self.pesquisa_url.clear()
			self.pesquisa_url.insert(url)
			self.browser.close()
			self.checar()
		except:
			self.pesquisa_url.clear()
			pass
		finally:
			try:
				self.browser.fechamento.disconnect()
			except:
				pass
			self.browser.close()
			self.captura_url.hide()

	def resumir_template(self):
		self.dic_desc.clear()
		if self.isDics.isChecked() and\
			len(self.min_dics.currentText())>0:
			self.dic_desc.show()
			ltexto = []
			tpath = _templates_dir + '/' + self.min_dics.currentText()
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
			destino = _templates_dir+'/'+nome
			if os.path.isdir(destino):
				odics = os.listdir(pasta)
				odics.sort()
				ddics = os.listdir(destino)
				ddics.sort()
				if ddics == odics:
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
			self.min_dics.setCurrentText(nome)
		except:
			return
		
	def ativar_templates(self):
		if self.isDics.isChecked():
			self.labelDics.setEnabled(True)
			self.min_dics.setEnabled(True)
			self.min_dics.clear()
			self.min_dics.addItems(templates)
			self.resumir_template()
			if self.retomada == True:
				self.novo_template.setEnabled(False)
			else:
				self.novo_template.setEnabled(True)
		else:
			self.labelDics.setEnabled(False)
			self.min_dics.setEnabled(False)
			self.min_dics.clear()
			self.resumir_template()
			self.novo_template.setEnabled(False)

	def ativar_configs(self):
		self.box_config.setEnabled(True)
		self.isLimite.setEnabled(True)
		self.isCustom.setEnabled(True)
		self.isXlsx.setEnabled(True)

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
		self.min_dics.setEnabled(False)
		self.labelDics.setEnabled(False)
		self.ativar_configs()

	def retomarpesquisa(self):
		self.reset()
		t = None
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
			if t not in templates:
				templates.append(t)
			self.ativar_templates()
			self.min_dics.setCurrentText(t)

		self.pesquisa_arq.clear()
		locatual = os.path.dirname(self.anterior)
		self.pesquisa_arq.insert(locatual)
		self.pesquisa_nome.clear()
		self.pesquisa_nome.insert(self.d['nome'])
		self.pesquisa_url.clear()
		self.pesquisa_url.insert(self.d['url'])
		self.checar()

		self.labelNome.setEnabled(False)
		self.labelURL.setEnabled(False)
		self.pesquisa_nome.setEnabled(False)
		self.pesquisa_url.setEnabled(False)
		self.browse_url.setEnabled(False)
		self.isDics.setEnabled(False)
		self.min_dics.setEnabled(False)
		self.labelDics.setEnabled(False)

	def extrairpesquisa(self):
		self.reset()
		self.novap.setChecked(False)
		self.retomarp.setChecked(False)
		self.box_pesquisa.setEnabled(True)
		self.labelSaida.setEnabled(True)
		self.pesquisa_arq.setEnabled(True)
		self.browse_arq.setEnabled(True)
		self.novo_template.setEnabled(False)
		self.box_config.setEnabled(True)
		self.isXlsx.setEnabled(True)
		self.isCustom.setEnabled(False)
		self.isLimite.setEnabled(False)
		self.fazer.clicked.disconnect(self.executar)
		self.fazer.clicked.connect(self.extrairpesquisa2)

		try:
			self.anterior, self.d = portas._achar_portas()
			assert self.anterior
		except:
			self.reset()
			return

		self.pesquisa_arq.clear()
		locatual = os.path.dirname(self.anterior)
		self.pesquisa_arq.insert(locatual)
		self.pesquisa_nome.clear()
		self.pesquisa_nome.insert(self.d['nome'])
		self.pesquisa_url.clear()
		self.pesquisa_url.insert(self.d['url'])
		if self.d['template'] != '*':
			self.min_dics.clear()
			self.min_dics.addItem(self.d['template'])
			self.min_dics.setCurrentText(self.d['template'])
		self.fazer.setText('Extrair')
		self.fazer.setEnabled(True)

	def extrairpesquisa2(self):
		self.fazer.setEnabled(False)
		dir_out = self.pesquisa_arq.text()
		basename = self.pesquisa_nome.text() + '_resultados'

		rivais = os.listdir(dir_out)
		csv_rivais = [x.replace('.csv','') \
			for x in rivais if x.endswith('.csv')]
		csv_rivais = [x for x in csv_rivais\
			if x.startswith(basename) and (len(basename)==(len(x)-4)\
			or len(basename)==(len(x)-5))]
		lc = len(csv_rivais)
		if basename + '.csv' in os.listdir(dir_out):
			lc += 1
		
		if lc == 0:
			sufixo = '.csv'
		else:
			sufixo = ' ({}).csv'.format(str(lc))
		nome_out = dir_out + '\\' + basename + sufixo
		portas._extrair_csv(self.anterior,nome_out)
		if self.isXlsx.isChecked():
			portas._trocar_csv(nome_out)
		self.finalizar()

	def reset(self):
		self.sucesso.hide()
		self.erroUrl.hide()
		self.progresso.hide()
		self.barraProgresso.setValue(0)
		self.novap.setEnabled(True)
		self.retomarp.setEnabled(True)
		self.extrairp.setEnabled(True)
		self.novap.setChecked(False)
		self.retomarp.setChecked(False)
		self.pesquisa_nome.clear()
		self.pesquisa_arq.clear()
		self.pesquisa_url.clear()
		self.isCompleta.setChecked(False)
		self.isDics.setChecked(False)
		self.min_dics.clear()
		self.isLimite.setChecked(False)
		self.isCustom.setChecked(False)
		self.isXlsx.setChecked(False)
		self.box_pesquisa.setEnabled(False)
		self.box_config.setEnabled(False)
		try:
			self.fazer.clicked.disconnect()
		except:
			pass
		self.fazer.clicked.connect(self.executar)
		self.fazer.setText('Iniciar')
		self.fazer.setCheckable(False)
		self.fazer.setChecked(False)
		self.fazer.setEnabled(False)
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
		try:
			self.thread_progresso.wait()
			self.thread_progresso.terminate()
		except:
			pass
		self.reset()
		self.novap.setChecked(False)
		self.retomarp.setChecked(False)
		self.sucesso.show()

	def executar(self):
		print('Começando a execução')
		self.fazer.clicked.disconnect(self.executar)
		time.sleep(1)
		self.fazer.setChecked(False)
		self.fazer.setEnabled(False)
		self.novap.setEnabled(False)
		self.retomarp.setEnabled(False)
		self.extrairp.setEnabled(False)
		self.progresso.show()
		self.progresso.setText('Checando URL...')
		p = portas.pesquisa()
		
		self.meta = portas._contar_resultados(self.pesquisa_url.text())

		if not self.meta:
			self.progresso.hide()
			self.reset()
			self.erroUrl.show()	
			return

		# trava elementos
		self.box_pesquisa.setEnabled(False)
		self.box_config.setEnabled(False)
		time.sleep(1)

		# configura objeto de pesquisa
		self.progresso.setText('Configurando pesquisa')
		p.nome = self.pesquisa_nome.text()

		p.arq = self.pesquisa_arq.text() + '/' + p.nome
		p.url = self.pesquisa_url.text()
		if self.isDics.isChecked() and self.min_dics.currentText():
			p.dics = _parent + '/templates/' + self.min_dics.currentText()
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
			self.meta = p.limite
		else:
			p.limite = None

		if self.isXlsx.isChecked():
			p.salvar_xlsx = True
		else:
			p.salvar_xlsx = False

		print('Iniciando Thread')
		self.progresso.setText('Executando primeiro ciclo...')
		gen = portas.executar(p)
		self.thread_progresso = progressThread(gen)
		self.thread_progresso.progress_update.connect(self.atualizar_progresso)
		self.thread_progresso.finished.connect(self.finalizar)
		self.thread_progresso.start()

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = PortasApp()
	window.show()
	sys.exit(app.exec_())
