# Controle do Sistema

Para controlar a temperatura do forno, mantendo uma pequena faixa de variação, podendo apenas desligar e ligar o sistema de aquecimento.

---
Controle ON/OFF com Histerese (Simples):

O sistema liga o aquecimento quando a temperatura fica abaixo de um limite inferior e desliga quando atinge um limite superior, variando dentro de uma faixa aceitável.

Gráficos úteis para modelagem do sistema
  
 - Resposta ao degrau de potência (Step Response)

    Obter: Ligar o aquecedor de repente e registrar a temperatura ao longo do tempo.

    Utilidade: A inércia térmica do sistema, constante de tempo, temperatura máxima atingida, etc. 

 - Curva de resfriamento
    
    Obter: Desligar o aquecedor e registrar a curva de queda da temperatura.

    Utilidade: Demonstra a perda de calor do sistema para o ambiente (coeficiente de dissipação térmica).

 - Ciclo de controle ON/OFF
  
    Obter: Registrar a temperatura enquanto o sistema opera com controle ON/OFF

    Utilidade: A faixa de variação da temperatura (overshoot, undershoot), frequência de comutação do aquecedor.

---

Controle PID com PWM:

O sistema calcula um ciclo de trabalho PWM utilizando PID sobre o erro de temperatura, com o PWM definindo quanto tempo o aquecedor fica ligado a cada ciclo.

Gráficos úteis para modelagem do sistema

 - Resposta ao degrau de potência
 - Curva de resfriamento
 - Sinal de controle PWM

    Obter: Registrar o valor de u(t) ao longo do tempo.

    Utilidade: Validar a reação do PID a mudanças na temperatura e referência.

---
---

## Taxa de Amostragem

Para obter uma boa taxa de amostragem, é necessario ter ideia de qual seria o valor da constante de tempo τ do forno. Possuindo esse dado, poderia ser utilizada cerca de 10 amostragens por constante de tempo, ou seja:
$$
f= \frac{10}{τ}
$$

Para encontrar a constante de tempo do forno é necessario aplicar um degrau de potência fixa e medir a temperatura ate atingir o regime permanente identificando:
  - $T_0$: Temperatura inicial
  - $T_f$: Temperatura final (regime)
  - $\Delta_T$: $T_f - T_0$

Aproximando a resposta térmica do forno como um modelo de primeira ordem.

$$
T(t)=Tf​−ΔT⋅e^{−t/τ}
$$

com a constante de tempo sendo o tempo necessario para o sistema chegar em 63.2% da variação de temperatura total.

Não sinto que este método seja muito prático, por conta de termos que estimar uma temperatura final e inicial para conseguir fazer a modelagem. Considerando que o forno que utilizamos a temperatura se altera bem lentamente, cerca de 5-10 segundos já seria um bom tempo entre as amostras, sendo possivel aumentar ainda mais caso haja muitos ruídos.