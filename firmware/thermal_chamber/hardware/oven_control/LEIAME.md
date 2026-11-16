# Controle do forno: esquemático (KiCad 7)

`forno_controle.kicad_sch` é o circuito do breadboard que controla o forno: Arduino Nano 33
IoT, NTC, TIP31 e o relé de estado sólido LOTI 48D25A. Abra `forno_controle.kicad_pro` no
KiCad; o PDF, o SVG e o PNG são a mesma folha exportada.

Levantado em 29/10/2026 a partir do firmware, do TCC e das fotos do breadboard (não houve
medição com multímetro). O que não deu para ver nas fotos está em caixas tracejadas.

## O circuito

| Bloco | Ligação | De onde vem |
|---|---|---|
| Temperatura | 3,3 V → R1 10 kΩ 1 % → **A0** → NTC 10 kΩ β 3950 → GND | `PID_Controller.ino` (`NTC_PIN = A0`, divisor "VREF → R_DIVISOR → ADC → NTC → GND") e TCC |
| SSR | **A1** → R2 1 kΩ → base do **TIP31**; emissor no GND; coletor no **−4** do SSR; **+3** do SSR em V_SSR | `PID_Controller.ino` (`SSR_PIN = A1 // via TIP31`), `SSR_TEST.ino` ("A1 → resistor de 1k → base do TIP31") |
| Carga | rede 220 V (L) → SSR 1–2 → resistência do forno → N | TCC (SSR zero-crossing, carga AC de 220 V; resistência original do Odontobras EL 1.1) |

O componente preto TO-220 do breadboard é um **transistor NPN TIP31**, não um MOSFET. Com
A1 em nível alto (3,3 V), a corrente de base é ≈ (3,3 − 0,8)/1 kΩ ≈ 2,5 mA; o TIP31 satura e
fecha o circuito de entrada do SSR. Ele existe porque o SSR pede de 5 a 32 V na entrada e o
Nano 33 IoT só dá 3,3 V. Os dois resistores azuis (5 faixas, 1 %) batem com os 10 kΩ e 1 kΩ
do firmware.

No KiCad, o TIP31 usa o símbolo `BD911` da biblioteca (também NPN em TO-220, com a mesma
pinagem: 1 B, 2 C, 3 E), porque o KiCad 7 não tem o TIP31. O SSR é um símbolo próprio
(`Bancada:SSR_LOTI_48D25A`) embutido no arquivo, com os números dos terminais do relé
(1 e 2 AC, 3+ e 4− controle).

## A confirmar

1. **De onde vem o +3 do SSR (V_SSR).** Pode ser o VIN/+5V do Nano (5 V do USB) ou a fonte
   chaveada. Teste: com o app ligado e o SSR aceso, meça a tensão entre o +3 do SSR e o GND
   do Nano. Se der ~4,7–5 V, vem do Nano; se der ~12 V, da fonte. Nesse segundo caso, o GND
   da fonte tem de estar ligado ao GND do Nano, senão o TIP31 não fecha o circuito.
2. **O capacitor cerâmico (C1).** Leia a marcação (ex.: `104` = 100 nF) e veja em que
   fileiras do breadboard estão as pernas. No desenho ele aparece como desacoplamento de
   3,3 V, que é só o mais provável.
3. **A fonte chaveada (caixa metálica com chave 115/230 V).** Ela não aparece no firmware
   nem no TCC. Talvez seja a fonte de 12 V da placa AU15P (o STM32 mede Vin = 12,1 V), mas
   isso precisa ser conferido.

Depois de conferir, edite direto no KiCad.

## Recriar do zero

`gerador/gera_forno.py` monta o esquemático lendo os símbolos de `/usr/share/kicad/symbols`
(`python3 gerador/gera_forno.py <pasta>`). Ele sobrescreve o arquivo: só use se as edições
feitas no KiCad puderem ser perdidas.
