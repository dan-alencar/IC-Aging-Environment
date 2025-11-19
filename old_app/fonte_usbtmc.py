import pyvisa as visa
import time

# --- Modificação principal para USB-TMC (VISA) ---
try:
    # Cria o Resource Manager (gerenciador de recursos). 
    # 'pyvisa-py' é um backend comum se você não tem o NI-VISA/Keysight instalado.
    rm = visa.ResourceManager('@py') 

    # Encontre o endereço (resource string) do seu instrumento.
    # Você deve substituir o 'USB0::...' pelo endereço real do seu instrumento.
    # Você pode usar rm.list_resources() para encontrá-lo (veja o próximo passo).
    # O endereço USB-TMC geralmente se parece com: 'USB0::VendorID::ProductID::SerialNumber::INSTR'
    
    # Exemplo de endereço USB-TMC (A ITECH IT6500 Series é um modelo de fonte de alimentação programável)
    # Tente encontrar o seu endereço real primeiro!
    
    # É altamente recomendável consultar rm.list_resources() para o endereço exato:
    # print(rm.list_resources())
    
    # No seu caso, o dispositivo está sendo listado como /dev/usbtmc1. 
    # O PyVISA deve conseguir resolver isso (se o backend estiver correto).
    # Se 'USB::...' não funcionar, tente o formato Raw: 'ASRL/dev/usbtmc1::INSTR' ou use o endereço USB.

    # O PyVISA geralmente prefere o formato padronizado USB::...
    # Vamos usar um placeholder, mas você deve verificar o seu
    resource_address = 'USB0::65535::25856::800630011777420110::0::INSTR' # <--- SUBSTITUA ESTE ENDEREÇO

    # Abrindo a conexão com o instrumento
    inst = rm.open_resource(resource_address)
    
    # Configurações de tempo limite (timeout) em milissegundos
    inst.timeout = 5000 
    
    # Recomenda-se um comando de identificação no início
    idn = inst.query('*IDN?')
    print(f"Conectado a: {idn}")
    
    # A fonte de alimentação deve ser controlada remotamente
    inst.write('SYSTem:REMote')
    print("Sistema agora em Modo Remoto")

    # Exemplo: Medir a tensão de saída (MEASure[:SCALar]:VOLTage[:DC]?)
    voltage = inst.query('MEAS:VOLT?')
    print(f"Tensão Medida: {voltage.strip()} V")

    # Exemplo: Consultar o estado da saída (OUTPut[:STATe]?)
    output_state = inst.query('OUTP?')
    print(f"Estado da Saída (0=OFF, 1=ON): {output_state.strip()}")

    # Exemplo: Definir tensão para 5.0 V e ligar a saída
    inst.write('VOLT 1.0')
    inst.write('OUTP ON')
    
    voltage = inst.query('MEAS:VOLT?')
    print(f"Tensão Medida: {voltage.strip()} V")
    # print("Saída ligada a 5.0 V.")

    # Exemplo: Desligar a saída
    # inst.write('OUTP OFF')
    # print("Saída desligada.")

except visa.errors.VisaIOError as e:
    print(f"Erro de comunicação VISA. Verifique o endereço e se o instrumento está conectado/ligado: {e}")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
finally:
    # O PyVISA fecha o recurso automaticamente na maioria dos casos, mas é uma boa prática tentar fechar
    if 'inst' in locals() and inst:
        inst.close()
    if 'rm' in locals() and rm:
        rm.close()
