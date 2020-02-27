# Robnada 0.0.1
*Pacote em Python para web scraping de pesquisas no Banco de Sentenças do Tribunal de Justiça do Estado de São Paulo -- TJSP -- desenvolvido pela equipe do Laboratório Espaço Público e Direito à Cidade -- LabCidade -- da Faculdade de Arquitetura e Urbanismo da Universidade de São Paulo.*

Usando Python 3.6 ou superior, é possível instalá-lo em seu computador com o comando abaixo, desde que python esteja definido como variável ambiente:
`>>> python -m pip install robnada`

## Estrutura
A aplicação em python está organizada com a seguinte estrutura:

## Introdução
Uma das frentes de atuação do Observatório de Remoções do Laboratório Espaço Público e Direito à Cidade da Faculdade de Arquitetura e Urbanismo da Universidade de São Paulo é o mapeamento e o acompanhamento dos processos de remoção em curso na Região Metropolitana de São Paulo, os quais que têm sido realizados continuamente por meio da inclusão, pelos(as) pesquisadores(as), de conflitos fundiários coletivos em uma plataforma de mapeamento, e da sua ampla divulgação. No âmbito do convênio do LabCidade - FAU/USP com a Escola Superior do Ministério Público do Estado de São Paulo, a proposta de obtenção de dados do Tribunal de Justiça de São Paulo visa a ampliação desse mapeamento, com a inclusão de resultados de processos judiciais que resultam em remoções forçadas como índice de processos de remoção ou ameaça.

Esses dados podem ser obtidos através do Banco de Sentenças do Tribunal de Justiça, disponível no endereço [https://esaj.tjsp.jus.br/cjpg/](https://esaj.tjsp.jus.br/cjpg/), base de dados pública que reúne os julgados de 1º grau onde se pode consultar conjuntos de processos judiciais separados por tema, e não apenas pelo número do processo. Como os processos judiciais, mesmo quando ainda em primeira instância, resultam em remoções forçadas e, portanto, também configuram situações de ameaça a partir do momento em que são autuados, a base de dados de sentenças de primeira instância tem total relevância para o trabalho.

Em levantamento prévio, foram identificadas mais de 300 mil sentenças de assuntos associados a despejos, desapropriação e conflitos de posse até 2018. No entanto, esses dados estão disponíveis na página apenas em texto html, e em quantidade que inviabiliza a tabulação manual ou leitura qualitativa individualizada do teor das sentenças.

Com essas limitações, optou-se pelo desenvolvimento de um programa de raspagem de dados (web scraping) para obtenção das informações. O programa requisita dados de sentenças página a página, simulando uma consulta manual à base de dados do Tribunal de Justiça a partir de assuntos escolhidos pelo usuário. Para cada resposta do servidor, o programa faz uma análise sintática do texto em html, extraindo três conjuntos de dados.

O primeiro diz respeito à ficha cadastral do processo padronizada pelo próprio banco de dados, contendo dados como a data de publicação da sentença, o número do processo julgado, o magistrado responsável e a vara responsável pelo processo. O segundo reúne informações sobre as partes, comuns a todos os processos, mas só disponíveis "em prosa", no resumo das sentenças. O terceiro abrange uma série de dados secundários, majoritariamente qualitativos, obtidos a partir de busca de expressões regulares e outras operações sintáticas nos dois conjuntos de dados anteriores.

Para identificação das expressões regulares a serem utilizadas na criação do terceiro conjunto de dados, foram realizadas várias pequenas pesquisas amostrais. A partir delas, foram identificados os tipos de dados que poderiam ser extraídos em massa, graças ao uso de frases recorrentes pelos escrivães das sentenças. Dentre as variáveis criadas nesse processo estão a classificação das partes em pessoa física ou jurídica, a discriminação de processo imobiliário, a concessão ou não de justiça gratuita, o teor final da sentença e, em especial a procedência ou não do pedido inicial ou a homologação de acordos, o endereço dos imóveis alvo dos processos, dentre outros.

Ainda, durante o desenvolvimento do programa, identificou-se a possibilidade de raspagem dos dados de outra fonte do Tribunal de Justiça para qualificar ainda mais as informações. A partir dos números dos processos obtidos na raspagem do primeiro conjunto de dados, o programa realiza uma consulta avançada de cada processo raspado, onde se pode obter informações específicas dos processos que tramitam ou tramitaram em primeira instância, tais como as movimentações e os atos processuais realizados. Com isso, obtém-se dados sobre a data de abertura do processo, o valor da ação judicial e a situação do processo.

Como as informações dos processos judiciais passaram a compor a base informatizada de maneira completa e sistemática somente a partir de 2013, todos os dados de processos abertos antes de 2013 não corresponderão ao universo e, portanto, deverão ser separados durante a análise. [ esses dados serão utilizados para contornar uma limitação metodológica imposta pela base de dados. ]

O programa foi desenvolvido em linguagem Python 3, e é compatível com o sistema operacional Windows. Sua execução exige a instalação do navegador Google Chrome para configuração da pesquisa. As solicitações são realizadas utilizando a biblioteca "requests", em solicitações ao servidor do Tribunal de Justiça organizadas com as bibliotecas "queue" e "threading". O número de threads simultâneos é definido pelo usuário. O resultado é um arquivo csv contendo os dados tabulados e um arquivo com estrutura zip que permite uma atualização da pesquisa realizada sem necessidade de realizá-la desde o começo. Isso foi implementado para viabilizar um acompanhamento periódico da base de dados, que possa corresponder ao fluxo de pesquisa e produção do Observatório de Remoções. Também foi desenvolvido um pequeno script para união dos dados de múltiplas pesquisas em uma única planilha.

Após a raspagem, os dados são utilizados na produção de gráficos e mapas temáticos. Os mapas serão elaborados pelo cruzamento dos perímetros de abrangência territorial dos fóruns com os dados agregados dos processos, ponderados pelo número de domicílios de cada fórum conforme o último Censo Demográfico do IBGE. Além disso, parte dos processos para a qual foi possível obter um endereço será geocodificada com serviços gratuitos do Google API.

## Especificação das variáveis

|Variável|Método|Fonte|
|---|---|---|
|`Início Raspagem`|Operação interna|Máquina local|
|`Processo`|Raspagem|Banco de Sentenças, TJSP|
|`Classe`|Raspagem|Banco de Sentenças, TJSP|
|`Assunto`|Raspagem|Banco de Sentenças, TJSP|
|`Magistrado`|Raspagem|Banco de Sentenças, TJSP|
|`Comarca`|Raspagem|Banco de Sentenças, TJSP|
|`Foro`|Raspagem|Banco de Sentenças, TJSP|
|`Vara`|Raspagem|Banco de Sentenças, TJSP|
|`Data de Disponibilização`|Raspagem|Banco de Sentenças, TJSP|
|`Comprimento resumo`|Mineração de texto|Programa|
|`Tipo partes`|Mineração de texto|Programa|
|`Parte 1`|Mineração de texto|Programa|
|`Parte 2`|Mineração de texto|Programa|
|`Razão parte 1`|Mineração de texto|Programa|
|`Razão parte 2`|Mineração de texto|Programa|
|`Parte 2 múltipla`|Mineração de texto|Programa|
|`Grupo parte 1`|Mineração de texto|Programa|
|`Descrição parte 1`|Mineração de texto|Programa|
|`RAJ`|Mineração de texto|Programa|
|`Justiça gratuita`|Mineração de texto|Programa|
|`Imobiliário`|Mineração de texto|Programa|
|`Invasor`|Mineração de texto|Programa|
|`Sublocação`|Mineração de texto|Programa|
|`Ambiental`|Mineração de texto|Programa|
|`Uso imóvel`|Mineração de texto|Programa|
|`Contagem R$`|Mineração de texto|Programa|
|`Aluguel (R$)`|Mineração de texto|Programa|
|`Aluguel atualizado (R$)`|Mineração de texto|Programa|
|`Dívida do requerido (R$)`|Mineração de texto|Programa|
|`Aluguel NA`|Mineração de texto|Programa|
|`Aluguel atualizado NA`|Mineração de texto|Programa|
|`Dívida do requerido NA`|Mineração de texto|Programa|
|`Endereço`|Mineração de texto|Programa|
|`Ref Endereço`|Mineração de texto|Programa|
|`Sentença`|Mineração de texto|Programa|
|`Contagem sentenças`|Mineração de texto|Programa|
|`Situação`|Raspagem|Consulta processual, TJSP|
|`Valor da ação (R$)`|Raspagem|Consulta processual, TJSP|
|`Data distribuição`|Raspagem|Consulta processual, TJSP|
|`Dias em tramitação`|Operação interna|Programa|