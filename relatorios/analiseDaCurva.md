# Método de Análise da Curva

### Limpeza dos dados
 
 - Remoção de leituras impossíveis 
 
    Valores que provavelmente são erros do sensor: -999 ou valores que saltem bruscamente, por exemplo um salto de 5 graus com uma taxa de amostragem de 0,2Hz

 - Suavização da curva
    
    Para evitar ruídos do sensor podemos utlizar um filtro de média móvel pequeno, com 3 ou 4 amostras, ou outros tipos de filtros.

### Processamento Estatístico
 - Plot de gráfico temperatura x tempo
   
   Estimativa da constante de tempo τ a partir do gráfico.

   Análise do atraso ao ligar o aquecimento (Dead time).

   Estimar a velocidade inicial do aquecimento aplicando regressão linear ao inicio do aquecimento (inclinação inicial do aquecimento).