# Importando as Bibliotecas necessárias

from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import textwrap

import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from matplotlib.ticker import ScalarFormatter
from babel.numbers import format_currency


# Configurando a visualização para os numeros apresentar duas casas decimáis apenas
pd.options.display.float_format = '{:.2f}'.format

# Definindo as Configirações básicas para a busca dos dados
periodo = '1d' # This variable is not used with start and end, but kept for clarity if needed later.
start = '2025-01-01' # Data de Início dos dados
final = '2026-12-31' # Data Final para busca dos Dados
ibov = 'Dados_Colab/IBOVDia_23-11-26.csv' # Nome do arquivo do IBOV
filtro = 5 # Quantidade de empresas para filtro de Ranking

# Abrindo o arquivo CSV com as empresas que compõe o IBOV
dados = pd.read_csv(ibov, sep=';', header=1, encoding='latin-1', index_col=False)
dados.drop([dados.shape[0] -2, dados.shape[0]-1], inplace=True)

# Criando uma lista com os Tickers para a busca dos dados no yfinance
tikers = [f'{codigo}.SA' for codigo in dados['Código']]

'''tikers = []
for codigo in dados['Código']:
    tikers.append(f'{codigo}.SA')'''

# Buscando os dados diários para o periodo informado de cada empresa do IBOV
dados_acoes = yf.download(tikers,
    start=start,
    end=final,
    auto_adjust=False)

# Criando DataFrame somente com o fechamento
if 'Adj Close' in dados_acoes.columns.get_level_values(0):
    precos = dados_acoes['Adj Close']
else:
    precos = dados_acoes['Close']

    # Função para gerar os Gráficos
def grafico(x,y,nome_grafico):
  ax = plt.figure(figsize=(12,5))
  ax = plt.xlabel('Data')
  ax = plt.ylabel('Preço')
  ax = plt.title(nome_grafico)
  ax=plt.plot(x, y, linewidth=0.8)


  # Plotando o Gráfico com todas as ações
grafico(dados_acoes.index, precos, 'Todas as Ações do IBOV')

# Normalizando os dados das Ações
dados_normalizados = precos / precos.iloc[0]

# Plotando o Gráfico com os dados Normalizados
grafico(dados_acoes.index, dados_normalizados, 'Todas as Ações do IBOV - Dados Normalizados')

# Criando uma lista com as 10 empresas com maior ganho no periodo
lista = []
for i in dados_normalizados.columns:
    lista.append([i,dados_normalizados[i].iloc[-1]])
lista = pd.DataFrame(lista).sort_values(by=1,ascending=False)
lista.columns = ['Ticker', 'V_final']
tickers_destaque = lista['Ticker'].iloc[0:filtro]

# Buscando os dados para as empresas destaque no yfinance
dados_acoes_destaque = yf.download(list(tickers_destaque), start=start, end=final, auto_adjust=False)

if 'Adj Close' in dados_acoes_destaque.columns.get_level_values(0):
    precos_destaque = dados_acoes_destaque['Adj Close']
else:
    precos_destaque = dados_acoes_destaque['Close']

# Normalizando os dados das empresas destaque
dados_normalizados_destaque = precos_destaque / precos_destaque.iloc[0]

# Plotando um Gráfico com os dados normalizados das empresas destaque
grafico(dados_acoes_destaque.index, dados_normalizados_destaque, f'Ranking das {filtro} Ações do IBOV com Melhor Desempenho')
plt.legend(list(tickers_destaque), fontsize=8)  

# Criando uma lista com as 10 empresas com maior ganho no periodo
lista = []
for i in dados_normalizados.columns:
    lista.append([i,dados_normalizados[i].iloc[-1]])
lista = pd.DataFrame(lista).sort_values(by=1,ascending=True)
lista.columns = ['Ticker', 'V_final']
tickers_destaque_neg = lista['Ticker'].iloc[0:filtro]

# Buscando os dados para as empresas destaque no yfinance
dados_acoes_destaque_neg = yf.download(list(tickers_destaque_neg), start=start, end=final, auto_adjust=False)

if 'Adj Close' in dados_acoes_destaque_neg.columns.get_level_values(0):
    precos_destaque_neg = dados_acoes_destaque_neg['Adj Close']
else:
    precos_destaque_neg = dados_acoes_destaque_neg['Close']

# Normalizando os dados das empresas destaque
dados_normalizados_destaque_neg = precos_destaque_neg / precos_destaque_neg.iloc[0]

# Plotando um Gráfico com os dados normalizados das empresas menos destacadas
grafico(dados_acoes_destaque_neg.index, dados_normalizados_destaque_neg, f'Ranking das {filtro} Ações do IBOV com Pior Desempenho')
plt.legend(list(tickers_destaque_neg), fontsize=8)

# Inserindo uma coluna com o Ticker no formato de pesquisa do yfinance (.SA)
_ = []
for n, i in enumerate(dados.Código):
  _.append(f'{dados.Código.iloc[n]}.SA')
dados['Ticker'] = _

# Inserindo a Coluna de Dados de Fechamento Anterior
dados_ultimo_pregao = pd.merge(dados, dados_acoes.tail(2).Close.T.reset_index(), on='Ticker', how='left')
dados_ultimo_pregao = dados_ultimo_pregao.drop(columns = [dados_ultimo_pregao.columns[-1]])
dados_ultimo_pregao.columns = ['Código', 'Ação', 'Tipo', 'Qtde. Teórica', 'Part. (%)', 'Ticker', f'Fech. Anterior {str(dados_acoes.tail(2).Close.T.reset_index().columns[-2])[:10]}']

# Inserindo a Coluna de Dados de Abertura do Dia
dados_ultimo_pregao = pd.merge(dados_ultimo_pregao, dados_acoes.tail(1).Open.T.reset_index(), on='Ticker', how='left')
dados_ultimo_pregao.columns = ['Código', 'Ação', 'Tipo', 'Qtde. Teórica', 'Part. (%)', 'Ticker', f'Fech. Anterior {str(dados_acoes.tail(2).Close.T.reset_index().columns[-2])[:10]}', f'Abert. {str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[:10]}']

# Inserindo a Coluna de Dados de Fechamento do Dia
dados_ultimo_pregao = pd.merge(dados_ultimo_pregao, dados_acoes.tail(1).Close.T.reset_index(), on='Ticker', how='left')
dados_ultimo_pregao.columns = ['Código', 'Ação', 'Tipo', 'Qtde. Teórica', 'Part. (%)', 'Ticker', f'Fech. Anterior {str(dados_acoes.tail(2).Close.T.reset_index().columns[-2])[:10]}', f'Abert. {str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[:10]}', f'Fech. {str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[:10]}']

# Removendo os Pontos da coluna de Quantidade Teórica
dados_ultimo_pregao['Qtde. Teórica'] = dados_ultimo_pregao['Qtde. Teórica'].str.replace('.', '').astype(float)
dados_ultimo_pregao.head()

# Inserindo a Coluna de Variação do Dia por Ação em Reais (com base no fechamento do dia Anterior)
dados_ultimo_pregao['Var_dia_Rs'] = dados.apply(lambda row: dados_acoes['Close'].iloc[-1][row['Ticker']] - dados_acoes['Close'].iloc[-2][row['Ticker']], axis=1)

# Inserindo a Coluna de Variação do Dia por Ação e Porcentagem (com base no fechamento do dia Anterior)
dados_ultimo_pregao['Var_dia_pct'] = ((dados.apply(lambda row: dados_acoes['Close'].iloc[-1][row['Ticker']] / dados_acoes['Close'].iloc[-2][row['Ticker']], axis=1)) - 1) * 100
dados_ultimo_pregao.head()

# Inserindo a Coluna de Resultado, Se Subiu ou Desceu
dados_ultimo_pregao['resultado'] = dados_ultimo_pregao['Var_dia_pct'].apply(lambda x: "Subiu" if x > 0 else ("Desceu" if x < 0 else "Estável"))
dados_ultimo_pregao.head()

# Inserindo a Coluna de Valor de Mercado (Quantidade teórica de Ações * Valor de Fechamento do Dia)
dados_ultimo_pregao['valor_merc'] = dados_ultimo_pregao[f'Fech. {str(dados_acoes.tail(1).Open.T.reset_index().columns[-1])[:10]}'] * dados_ultimo_pregao['Qtde. Teórica']
dados_ultimo_pregao.head()

# Lendo o arquivo csv com os Dados dos Setores
dados_setorial = pd.read_excel('Dados_Colab/Setorial B3 07-03-2024.xlsx')
dados_setorial.head()

# Fazendo um "Merge" para juntar os Dados Setoriais da B3 ao DataFrame dados_ultimo_pregao
dados_ultimo_pregao['Ação'] = dados_ultimo_pregao['Ação'].str.strip()
dados_setorial['Ação'] = dados_setorial['Ação'].str.strip()
dados_ultimo_pregao = pd.merge(dados_ultimo_pregao, dados_setorial, on='Ação', how='left')
dados_ultimo_pregao = dados_ultimo_pregao.drop(columns= ['Codigo', 'seg'])
dados_ultimo_pregao['Part. (%)'] = pd.to_numeric(dados_ultimo_pregao['Part. (%)'].str.replace(',', '.'))
dados_ultimo_pregao.head(1)

# Inserindo a Coluna de Variação do Valor de Mercado no Dia em Reais
dados_ultimo_pregao['Variacao_rs'] = dados_ultimo_pregao['Qtde. Teórica'] * dados_ultimo_pregao['Var_dia_Rs']
dados_ultimo_pregao.head()

# Salvando o DataFrame em um arquivo csv
dados_ultimo_pregao.to_csv(f'Financas/analise_{str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[:10]}.csv')

Maior = dados_ultimo_pregao.Variacao_rs.max()
Menor = dados_ultimo_pregao.Variacao_rs.min()
Media = dados_ultimo_pregao.Variacao_rs.mean()
Media_subiu = dados_ultimo_pregao[dados_ultimo_pregao['resultado'] == 'Subiu']['Variacao_rs'].mean()
Media_desceu = dados_ultimo_pregao[dados_ultimo_pregao['resultado'] == 'Desceu']['Variacao_rs'].mean()


print(f'Maior Alta\t   {format_currency(Maior, "BRL", locale="pt_BR")}')
print(f'Maior Baixa\t{format_currency(Menor, "BRL", locale="pt_BR")}\n')
print(f'Média\t          {format_currency(Media, "BRL", locale="pt_BR")}\n')
print(f'Média Subiu\t   {format_currency(Media_subiu, "BRL", locale="pt_BR")}')
print(f'Média Desceu\t  {format_currency(Media_desceu, "BRL", locale="pt_BR")}')


# Análise por segmento
ax = plt.figure(figsize=(16,6))
ax = plt.xlabel('Segmento', fontsize=20)
ax = plt.ylabel('Valor em Bilhões', fontsize=20)
ax = plt.title('Variação do dia por Segmento (R$)', fontsize=20)
ax = plt.xticks(rotation=90)
ax = plt.grid(True, color='gray', linewidth=0.4, axis='y')
# ax = plt.grid(zorder=1)
fig = plt.bar(dados_ultimo_pregao.groupby(by='Segmento')['Variacao_rs'].sum().reset_index()['Segmento'], dados_ultimo_pregao.groupby(by='Segmento')['Variacao_rs'].sum().reset_index()['Variacao_rs'])
for bar in fig:
  height = bar.get_height()
  if height > 0:
    bar.set_zorder(0)
    bar.set_color('green')
  elif height < 0:
    bar.set_zorder(0)
    bar.set_color('red')


ax = plt.gca()
ax.tick_params(labelsize=25)

plt.savefig('grafico_1.png', dpi=600, bbox_inches='tight')

ax = plt.figure(figsize=(12,5))
ax = plt.xlabel('Segmento')
ax = plt.ylabel('Valor em Bilhões (R$)')
ax = plt.title('Segmentos com Alta no Dia (R$)')
ax = plt.xticks(rotation=85)
# plt.grid(True)
ax = plt.gca()
# ax.set_ylim(0, 1000000000)
ax.ticklabel_format(axis='y', style='sci')

plt.bar(dados_ultimo_pregao.groupby(by='Segmento')['Variacao_rs'].sum().reset_index().query("Variacao_rs > 0")['Segmento'], dados_ultimo_pregao.groupby(by='Segmento')['Variacao_rs'].sum().reset_index().query("Variacao_rs > 0")['Variacao_rs'], color='green')
plt.savefig('grafico_2.png', dpi=300, bbox_inches='tight')

dados_ultimo_pregao.query("resultado == 'Desceu'").groupby(by='Segmento')['Variacao_rs'].sum().reset_index()

ax = plt.figure(figsize=(12,5))
ax = plt.xlabel('Segmento')
ax = plt.ylabel('Valor em Bilhões')
ax = plt.title('Segmentos com Baixa no Dia (R$)')
ax = plt.xticks(rotation=85)
# ax = plt.grid(True, color='gray', linewidth=0.4, axis='y')
# ax = plt.grid(True, color='gray', linewidth=0.4, axis='x')

ax = plt.gca()
# ax.ticklabel_format(axis='y', style='plain')
# ax.set_yticks(list(range(0, -9000000000 + 1, -100000000)))


fig = plt.bar(dados_ultimo_pregao.groupby(by='Segmento')['Variacao_rs'].sum().reset_index().query("Variacao_rs < 0")['Segmento'], dados_ultimo_pregao.groupby(by='Segmento')['Variacao_rs'].sum().reset_index().query("Variacao_rs < 0")['Variacao_rs'], color='red')
plt.savefig('grafico_3.png', dpi=300, bbox_inches='tight')

# Análise das 3 Ações com Maiores Altas e Maiores Baixas
# 3 Ações com Maiores Altas no dia (%)
dados_ultimo_pregao.iloc[dados_ultimo_pregao['Var_dia_pct'].nlargest(3).index]

variacao_pos = dados_ultimo_pregao.iloc[dados_ultimo_pregao['Var_dia_pct'].nlargest(3).index][['Código', 'Ação', f'Fech. {str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[:10]}', 'Var_dia_pct', 'Segmento']].reset_index(drop=True)
variacao_pos

# 3 Ações com Maiores Baixas no dia (%)
variacao_neg = dados_ultimo_pregao.iloc[dados_ultimo_pregao['Var_dia_pct'].nsmallest(3).index][['Código', 'Ação', f'Fech. {str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[:10]}', 'Var_dia_pct', 'Segmento']].reset_index(drop=True)
variacao_neg

# Carregando a imagem de fundo
imagem_fundo = Image.open("Dados_Colab/fundo.png")

# Pegando a Largura e Altura da Imagem de fundo
imagem_largura, imagem_altura = imagem_fundo.size

# Criando um contexto de desenho
desenho = ImageDraw.Draw(imagem_fundo)

# Carregando uma fonte
caminho_fonte = "Dados_Colab/frutiger-bold.ttf"
tamanho_fonte = 40
fonte = ImageFont.truetype(caminho_fonte, tamanho_fonte)

# Desenhando os valores de Alta
Y = 0
for i in range(3):
  # Definindo o texto a ser colocado
  nome_pos = f"{variacao_pos['Ação'][i]} ({variacao_pos['Código'][i]})"
  fech_pos = f"| R$ {variacao_pos[variacao_pos.columns[-3]][i]:.2f}"
  var_pos = f"|  {variacao_pos[variacao_pos.columns[-2]][i]:.2f} %"

  # Obtendo a caixa delimitadora do texto
  caixa_delimitadora = desenho.textbbox((0, 0), nome_pos, font=fonte)
  # Calculando a posição do texto
  x1_pos = 164
  x2_pos = 650
  x3_pos = 880
  y = ((1000 - caixa_delimitadora[3]) // 2) + Y
  Y += caixa_delimitadora[3] + 25
  # Desenhando o texto na imagem
  desenho.text((x1_pos, y), nome_pos, font=fonte, fill="white")
  desenho.text((x2_pos, y), fech_pos, font=fonte, fill="white")
  desenho.text((x3_pos, y), var_pos, font=fonte, fill="white")

  # Desenhando os valores de Baixa
Y = 0
for i in range(3):
  # Definindo o texto a ser colocado
  nome_neg = f"{variacao_neg['Ação'][i]} ({variacao_neg['Código'][i]})"
  fech_neg = f"| R$ {variacao_neg[variacao_neg.columns[-3]][i]:.2f}"
  var_neg = f"|  {variacao_neg[variacao_neg.columns[-2]][i]:.2f} %"

  # Obtendo a caixa delimitadora do texto
  caixa_delimitadora = desenho.textbbox((0, 0), nome_neg, font=fonte)
  # Calculando a posição do texto
  x1_neg = 50
  x2_neg = 500
  x3_neg = 730
  y = ((1600 - caixa_delimitadora[3]) // 2) + Y
  Y += caixa_delimitadora[3] + 25
  # Desenhando o texto na imagem
  desenho.text((x1_neg, y), nome_neg, font=fonte, fill="white")
  desenho.text((x2_neg, y), fech_neg, font=fonte, fill="white")
  desenho.text((x3_neg, y), var_neg, font=fonte, fill="white")

# Definindo aposição do gráfico 1
grafico = Image.open('grafico_1.png')
grafico = grafico.resize((int(7937-(7937*0.90)),int(9108-(9108*0.90))))
grafico_largura, grafico_altura = grafico.size
centro_grafico = (imagem_largura - grafico_largura) // 2

imagem_fundo.paste(grafico, (int(centro_grafico),1000))

# Inserindo a Data no rodapé da Imagem
data = f'{str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[8:10]}/{str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[5:7]}/{str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[:4]}'
x_data = 170
y_data = (imagem_largura - caixa_delimitadora[3]) // 2
desenho.text((y_data, x_data), data, font=fonte, fill="white")



# Salvando a imagem modificada
imagem_fundo.save(f"Financas/image_{str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[:10]}.png", dpi=(1200, 1200))
imagem_fundo.save(f"Financas/grafico.png", dpi=(1200, 1200))


# Exibindo uma mensagem de sucesso
print("Texto adicionado à imagem e salvo como output.jpg")
imagem_fundo

# GPT

# Definindo as Configirações básicas para a busca dos dados
periodo = '1d' # This variable is not used with start and end, but kept for clarity if needed later.
start = '2025-01-01' # Data de Início dos dados
final = '2026-11-25' # Data Final para busca dos Dados
ibov = 'Dados_Colab/IBOVDia_24-06-26.csv' # Nome do arquivo do IBOV
filtro = 5 # Quantidade de empresas para filtro de Ranking

# Abrindo o arquivo CSV com as empresas que compõe o IBOV
dados = pd.read_csv(ibov, sep=';', header=1, encoding='latin-1', index_col=False)
dados.drop([dados.shape[0] -2, dados.shape[0]-1], inplace=True)

# Criando uma lista com os Tickers para a busca dos dados no yfinance
tikers = [f'{codigo}.SA' for codigo in dados['Código']]

'''tikers = []
for codigo in dados['Código']:
    tikers.append(f'{codigo}.SA')'''

# Buscando os dados diários para o periodo informado de cada empresa do IBOV
dados_acoes = yf.download(tikers,
    start=start,
    end=final,
    auto_adjust=False)

# Criando DataFrame somente com o fechamento
if 'Adj Close' in dados_acoes.columns.get_level_values(0):
    precos = dados_acoes['Adj Close']
else:
    precos = dados_acoes['Close']

    retorno_12m = (precos.iloc[-1] / precos.iloc[-252] - 1) * 100
retorno_3m = (precos.iloc[-1] / precos.iloc[-63] - 1) * 100
mm50 = precos.rolling(50).mean()
mm200 = precos.rolling(200).mean()

max_52 = precos.rolling(252).max()

dist_max = (
    (precos.iloc[-1] / max_52.iloc[-1]) - 1
) * 100

retornos = precos.pct_change()

volatilidade = retornos.std() * (252**0.5)

# forca_relativa = retorno_12m_acao - retorno_12m_ibov

# Retornos
ret_12m = (precos.iloc[-1] / precos.iloc[-252] - 1) * 100
ret_6m  = (precos.iloc[-1] / precos.iloc[-126] - 1) * 100
ret_3m  = (precos.iloc[-1] / precos.iloc[-63] - 1) * 100

# Médias
mm50 = precos.rolling(50).mean()
mm200 = precos.rolling(200).mean()

# Tendência
trend = (mm50.iloc[-1] > mm200.iloc[-1]).astype(int)

# Volatilidade
vol = precos.pct_change().std() * np.sqrt(252)

# Distância da máxima
max52 = precos.rolling(252).max()
dist_max = ((precos.iloc[-1] / max52.iloc[-1]) - 1) * 100

ranking = pd.DataFrame({
    'Ret_12M': ret_12m,
    'Ret_6M': ret_6m,
    'Ret_3M': ret_3m,
    'Trend': trend,
    'Vol': vol,
    'DistMax': dist_max
})

ranking['Score'] = (
    ranking['Ret_12M'].rank(pct=True)*0.35 +
    ranking['Ret_6M'].rank(pct=True)*0.25 +
    ranking['Ret_3M'].rank(pct=True)*0.15 +
    ranking['Trend']*0.15 +
    ranking['Vol'].rank(pct=True, ascending=False)*0.10
)

ranking = ranking.sort_values(
    'Score',
    ascending=False
)

carteira_modelo = ranking.head(10).copy()

carteira_modelo['Peso'] = (
    carteira_modelo['Score'] /
    carteira_modelo['Score'].sum()
)

aporte = 5000

carteira_modelo['Valor_Investir'] = (
    carteira_modelo['Peso'] * aporte
)

preco_atual = precos.iloc[-1]

carteira_modelo['Preco'] = (
    preco_atual.loc[carteira_modelo.index]
)

carteira_modelo['Qtde'] = (
    carteira_modelo['Valor_Investir'] /
    carteira_modelo['Preco']
).astype(int)

carteira_modelo['Valor_Real'] = (
    carteira_modelo['Qtde'] *
    carteira_modelo['Preco']
)

carteira_modelo[
    ['Score',
     'Peso',
     'Preco',
     'Qtde',
     'Valor_Real']
]

# Salvando o DataFrame em um arquivo csv
carteira_modelo.to_csv(f'Financas/carteira_{str(dados_acoes.tail(1).Close.T.reset_index().columns[-1])[:10]}.csv')
