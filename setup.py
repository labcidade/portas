### setup.py ###

import setuptools

with open('README.md', 'r') as fh:
	long_description = fh.read()

setuptools.setup(
	name='robnada-labcidade',
	version='0.0.1',
	author='LabCidade FAUUSP',
	author_email='labcidadefau@gmail.com',
	description='Pacote de raspagem do Banco de Sentenças em 1º Grau do TJSP',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='www.labcidade.com.br',
	packages=setuptools.find_packages(),
	classifiers=[
		'Development Status :: 3 - Alpha'
		'Programming Language :: Python :: 3',
		'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
		'Operating System :: OS Independent',
		'Intended Audience :: Science/Research',
		'Natural Language :: Portuguese (Brazilian)',
		'Topic :: Scientific/Engineering :: Information Analysis',

	],
	python_requires='>=3.6',
)