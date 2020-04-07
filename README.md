
# LabCidade PORTAS
*Aplicação em Python para web scraping de pesquisas no Banco de Sentenças do Tribunal de Justiça do Estado de São Paulo - TJSP - desenvolvido no Laboratório Espaço Público e Direito à Cidade - LabCidade - da Faculdade de Arquitetura e Urbanismo da Universidade de São Paulo.*

## Introdução
Uma das frentes de atuação do Observatório de Remoções do Laboratório Espaço Público e Direito à Cidade da Faculdade de Arquitetura e Urbanismo da Universidade de São Paulo é o mapeamento e o acompanhamento dos processos de remoção em curso na Região Metropolitana de São Paulo, os quais que têm sido realizados continuamente por meio da inclusão, pelos(as) pesquisadores(as), de conflitos fundiários coletivos em uma plataforma de mapeamento, e da sua ampla divulgação. No âmbito do convênio do LabCidade - FAU/USP com a Escola Superior do Ministério Público do Estado de São Paulo, a proposta de obtenção de dados do Tribunal de Justiça de São Paulo visa a ampliação desse mapeamento, com a inclusão de resultados de processos judiciais que resultam em remoções forçadas como índice de processos de remoção ou ameaça.

Esses dados podem ser obtidos através do Banco de Sentenças do Tribunal de Justiça, disponível no endereço [https://esaj.tjsp.jus.br/cjpg/](https://esaj.tjsp.jus.br/cjpg/), base de dados pública que reúne os julgados de 1º grau onde se pode consultar conjuntos de processos judiciais separados por tema, e não apenas pelo número do processo. Como os processos judiciais, mesmo quando ainda em primeira instância, resultam em remoções forçadas e, portanto, também configuram situações de ameaça a partir do momento em que são autuados, a base de dados de sentenças de primeira instância tem total relevância para o trabalho.

Em levantamento prévio, foram identificadas mais de 300 mil sentenças de assuntos associados a despejos, desapropriação e conflitos de posse até 2018. No entanto, esses dados estão disponíveis na página apenas em texto html, e em quantidade que inviabiliza a tabulação manual ou leitura qualitativa individualizada do teor das sentenças.

Com essas limitações, optou-se pelo desenvolvimento de um programa de raspagem de dados (web scraping) para obtenção das informações. O programa requisita dados de sentenças página a página, simulando uma consulta manual à base de dados do Tribunal de Justiça a partir de assuntos escolhidos pelo usuário. Para cada resposta do servidor, o programa faz uma análise sintática do texto em html, extraindo três conjuntos de dados:

- (1) Dados da ficha cadastral do processo padronizada pelo próprio banco de dados, contendo dados como a data de publicação da sentença, o número do processo julgado, o magistrado responsável e a vara responsável pelo processo;
- (2) Dados sobre as partes, comuns a todos os processos, mas só disponíveis "em prosa", no texto das sentenças; e
- (3) Dados secundários, majoritariamente qualitativos, obtidos a partir de busca de expressões regulares e outras operações sintáticas nos dois conjuntos de dados anteriores.

A princípio, havia também um quarto conjunto, obtido a partir de consulta processual, com dados de duração da tramitação e decisões intermediárias. Contudo, com a introdução de reCaptcha na página, esse conjunto foi inviabilizado por ora.

Para identificação das expressões regulares a serem utilizadas na criação do terceiro conjunto de dados, foram realizadas várias pequenas pesquisas amostrais, com indicação manual dos termos de interesse. A partir delas, foram identificados os tipos de dados que poderiam ser extraídos em massa, graças ao uso repetitivo de  pelos redatores das sentenças. Dentre as variáveis criadas nesse processo estão a classificação das partes em pessoa física ou jurídica, a discriminação de processo imobiliário, a concessão ou não de justiça gratuita, o teor final da sentença e, em especial a procedência ou não do pedido inicial ou a homologação de acordos, o endereço dos imóveis alvo dos processos, dentre outros.

## Entendendo a arquitetura

O PORTAS está organizada com a seguinte estrutura:
```
portas
├ PORTAS.pyw
├ portas.py
├ dics
│   └ […]
├ templates
│   └ labcidade
│       └ […]
├ gui
│   └ […]
├ install.py
├ requirements.txt
├ .gitignore
├ LICENSE
└ README.md
```
Para executar o programa, basta clicar no arquivo "PORTAS.pyw". As principais funções, contudo, são executadas pelo arquivo "portas.py". Com intenção de facilitar a compreensão, faremos uma analogia.
O arquivo "portas.py" funciona como um centro de controle da raspagem. Ele é capaz de executar um objeto-pesquisa configurado conforme suas exigências (que consiste de uma consulta ao Banco de Sentenças com algumas outras variáveis), e retorna os resultados tabulados. 

*Diagrama simplificado do processo de mineração dos dados*
![Diagrama simplificado do processo de mineração dos dados](https://lh3.googleusercontent.com/hAL9P0uy5z4t43Yt343SOz0ib7r-tksX3nDPW6Nk6N7Ae1wg4GfW1cnPdNiAwPjAXdvGEISn2AXWTNGJoP_wUl-x5DVHRoakQLZRFJOy_AYEtcvvJkzH-Tm-fkKqgw0NhUkmTfMZEw=w600)

O script opera em três etapas: configuração, pesquisa e registro. Na etapa de configuração, o script cria objetos necessários para executar o objeto-pesquisa a partir dos arquivos nas pastas "dics" e "templates" e de outras configurações. Esses dados dizem ao script quais são as informações que precisam ser buscadas nos textos das sentenças. Em seguida, na etapa de pesquisa, o script utilizará as configurações especificadas para executar threads. É como se o centro de controle enviasse robôs ao banco de sentenças, com instruções para encontrar informações que correspondam às configurações. O centro de controle enviará um número específico de robôs (definido pelo "número de buscas simultâneas", na interface) e aguardará que todos retornem para prosseguir. O tamanho do ciclo, especificado na interface do PORTAS, determina quantos processos os robôs devem encontrar antes de registrar os resultados. Assim, se os robôs retornarem e o ciclo ainda não estiver completo, eles serão enviados novamente ao Banco de Sentenças. Quando o ciclo é terminado, as informações obtidas pelos robôs é registrada em um aquivo .csv intermediário e em um arquivo de metadados em formato .txt. A execução de uma pesquisa pode precisar de vários ciclos, e o arquivo intermediário será atualizado ao final de cada um deles. Quando todos os ciclos forem terminados, o programa executa a etapa 3. Ela consiste na tradução dos dados do arquivo intermediário e dos metadados em um arquivo .portas de saída. Esse aquivo tem estrutura de arquivo .zip, e contém todas as informações necessárias para retomar a pesquisa: os templates utilizados, as configurações de busca e os resultados tabulados. Também será salvo um arquivo .csv contendo apenas os resultados tabulados, que pode ser aberto em programas como o LibreOffice Calc ou o Microsoft Office Excel.

A função do script "PORTAS.pyw" é simplesmente conectar o script "portas.py" aos arquivos de configuração da primeira etapa, usando para isso uma interface gráfica de usuário.

O PORTAS foi desenvolvido em linguagem Python 3, e é compatível com o sistema operacional Windows.

## Como usar
Para executar o PORTAS no seu computador, é necessário ter uma instalação de [Python 3.7](https://www.python.org/downloads/release/python-377/). Lembre-se de selecionar a opção adicionar ao PATH ("Add Python 3.7 to PATH") na caixa de diálogo da instalação. Caso já tenha instalado e/ou se esqueceu desse passo, [aqui](https://www.ownard.com.br/back-end/iniciante-adicionando-python-ao-path-no-windows-10/) você encontra instruções de como fazê-lo manualmente.
Além disso, é necessário ter uma conexão estável à Internet durante a execução, ou as pesquisas podem ser interrompidas.

Feito isso, basta baixar os arquivos do PORTAS no seu computador, extraí-los da pasta zipada e clicar no arquivo "PORTAS.pyw" para iniciar a execução. Este arquivo abrirá a interface do usuário, que possui instruções de como realizar a pesquisa. Pode ser que o programa demore para ser inicializado, pois serão instalados e verificados alguns requisitos para sua execução. Uma janela preta deve aparecer neste momento. Não a feche, ela indica que o programa está funcionando como esperado. Quando a interface aparecer, basta clicar em "Criar pesquisa" para configurar e executar uma nova raspagem.

Quando o programa terminar a execução, serão criados um arquivo .portas e um arquivo tabular (.csv ou .xlsx). O arquivo .portas contém todas as informações da sua pesquisa, e pode ser usado para atualizá-la no futuro usando a função "Retomar pesquisa" na interface do PORTAS. Guarde este arquivo, ele é o produto mais importante da raspagem! O arquivo tabular é apenas um fragmento do arquivo .portas, que pode ser usado para visualizar os resultados. É possível extrair um arquivo tabular de um arquivo .portas usando a função "Extrair resultados" na interface do PORTAS. Quando o arquivo tabular é criado em formato .csv, a codificação do arquivo é UTF-8 e o separador é o caractere | (pipe).

## Especificação das variáveis
Os arquivos de saída 

|Variável|Fonte|Descrição|
|---|---|---|
|`Hora registro`|Máquina|Horário de início da raspagem|
|`Processo`|Cabeçalho da sentença|Código do processo|
|`Classe`|Cabeçalho da sentença|Classe do processo|
|`Assunto`|Cabeçalho da sentença|Assunto do processo|
|`Magistrado`|Cabeçalho da sentença|Magistrado responsável pela sentença|
|`Comarca`|Cabeçalho da sentença|Comarca Judicial do processo|
|`Foro`|Cabeçalho da sentença|Foro do processo|
|`Vara`|Cabeçalho da sentença|Vara do processo|
|`Data de Disponibilização`|Cabeçalho da sentença|Data de publicação da sentença|
|`Caracteres sentença`|Mineração de texto|Número de caracteres no resumo|
|`Palavras sentença`|Mineração de texto|Número de palavras no resumo|
|`Frases sentença`|Mineração de texto|Número de frases no resumo|
|`Tipo partes`|Mineração de texto|Relação entre as partes do processo|
|`Parte 1`|Mineração de texto|Nome da parte que move o processo|
|`Parte 2`|Mineração de texto|Nome da parte contra quem o processo é movido|
|`Razão parte 1`|Mineração de texto|Razão social da parte 1|
|`Razão parte 2`|Mineração de texto|Razão social da parte 2|
|`Parte 2 múltipla`|Mineração de texto|Indica se parte 2 é composta por mais de 2 pessoas|
|`Grupo parte 1`|Mineração de texto|Agrupamento da parte 1|
|`Grupo parte 2`|Mineração de texto|Agrupamento da parte 2|
|`Descrição parte 1`|Mineração de texto|Identificador da parte 1 em seu agrupamento|
|`RAJ`|Mineração de texto|Região Administrativa Judicial do processo|
|`UTA`|Mineração de texto|Unidade territorial de análise do processo|
|`Justiça gratuita`|Mineração de texto|Indica se parte 1 usa benefício de gratuidade|
|`Aluguel (R$)`|Mineração de texto|Indica valor do aluguel pago|
|`Aluguel atualizado (R$)`|Mineração de texto|Indica valor atualizado do aluguel, se houver|
|`Dívida do requerido (R$)`|Mineração de texto|Indica a dívida da parte 2|
|`Aluguel NA`|Mineração de texto|Aluguel (Se não autenticado)|
|`Aluguel atualizado NA`|Mineração de texto|Aluguel atualizado (Se não autenticado)|
|`Dívida do requerido NA`|Mineração de texto|Dívida da parte 1 (Se não autenticada) |
|`Endereço`|Mineração de texto|Endereço do imóvel sub judice|
|`Sentença`|Mineração de texto|Teor da(s) sentença(s) proferida(s)|
|`Contagem sentenças`|Mineração de texto|Número de sintagmas de sentença|


## Sobre os templates
Os templates são conjuntos de variáveis que podem ser incluídas e excluídas sem mudanças no código do PORTAS. O template "labcidade", por exemplo, permite incluir as seguintes variáveis nos resultados:

|Template|Variável|Descrição|
|---|---|---|
|labcidade|`Ambiental`|Indica se há sintagma de infração ambiental|
|labcidade|`Imobiliário`|Indica se há sintagma imobiliária|
|labcidade|`Invasão`|Indica se há sintagma sobre invasão|
|labcidade|`Sublocação`|Indica se há sintagma sobre sublocação|
|labcidade|`Uso imóvel`|Indica grupo de uso do imóvel sub judice|

Os templates consistem de uma pasta contendo exclusivamente arquivos de texto com o formato padrão do PORTAS. Para criar um template, primeiro crie uma nova pasta no seu computador. O nome dessa pasta será o nome do novo template. Em seguida, alimenta-se essa pasta com os arquivos de texto padronizados.

O arquivo de texto padrão segue as seguintes regras:

- O nome do arquivo será o nome da variável na tabela de resultados
- O formato do arquivo de texto deve ser .txt
- O arquivo deve ser codificado em UTF-8
- O arquivo será estruturado em linhas, cada linha com uma correspondência *sintagma*:*classificação*
- O *sintagma* corresponde ao termo que deve ser buscado na sentença. Caso seja encontrado, a variável assumirá o valor da *classificação*.
- O texto dos *sintagmas* deve ser escrito em letra maiúscula. Termos com letras minúsculas não retornarão resultados.
- O sintagma e a classificação em cada linha devem ser separados por uma tabulação (\t).
- A ordem das linhas no arquivo estabelece uma hierarquia. A variável assumirá a primeira correspondência encontrada - ou seja, a correspondência da linha inferior só será procurada caso a correspondência da linha superior não retorne resultados.
- Caso nenhum dos pares de correspondência seja identificado, a variável assumirá valor vazio.

A título de ilustração, observe o exemplo de conteúdo do arquivo de texto "Uso imóvel.txt", no template labcidade:

    GALPÃO INDUSTRIAL	Industrial
    USO INDUSTRIAL	Industrial
    ATIVIDADE INDUSTRIAL	Industrial
    SALÃO INDUSTRIAL	Industrial
    VILA INDUSTRIAL	Industrial
    IMÓVEL COMERCIAL	Comercial
    LOCAÇÃO COMERCIAL	Comercial
    USO COMERCIAL	Comercial
    NATUREZA COMERCIAL	Comercial
    NÃO RESIDENCIAL	Não residencial
    IMÓVEL RESIDENCIAL	Residencial
    USO RESIDENCIAL	Residencial
    LOCAÇÃO RESIDENCIAL	Residencial
    FIM RESIDENCIAL	Residencial
    CONTRATO RESIDENCIAL	Residencial
    LOCATÍCIO RESIDENCIAL	Residencial
    NATUREZA RESIDENCIAL	Residencial
    MORADIA	Residencial

Uma pasta de template pode conter quantos arquivos de texto padrão forem necessários. Assim que terminar de escrever suas variáveis, execute o PORTAS e siga as instruções da interface para ativar e incluir novos templates de pesquisa. Ao adicionar um template, selecione a pasta com os arquivos de texto padrão que você criou.
As variáveis fixas do PORTAS também usam arquivos de texto padrão, salvos na pasta "dics". Esses arquivos podem ter conteúdo alterado, mas não podem ser apagados ou renomeados, sob risco de danificar o programa. Para saber mais sobre as correspondências usadas no software, basta ler os arquivos de texto correspondentes a cada variável.

## Mapeando resultados
O LabCidade elaborou um procedimento para criar leituras cartográficas dos resultados de pesquisa. Utilizamos perímetros de comarcas e foros para desenhar Unidades Territoriais de Análise (UTAs), que foram georreferenciadas e disponibilizadas no shapefile de UTAs, dentro da pasta "recursos". Cada unidade possui um código, que é escrito na variável "UTA" de cada sentença pesquisada. Para criar uma leitura cartográfica dos resultados, agregue a base de dados por UTAs e utilize um programa SIG (como o [QGIS](https://qgis.org/en/site/)) para [unir os resultados](https://aredeurbana.com/2020/02/03/qgis-uniao-entre-planilhas-excel-e-shapefiles/) agregados ao shapefile das UTAs.
___
