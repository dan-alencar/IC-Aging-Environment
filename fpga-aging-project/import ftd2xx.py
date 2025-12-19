import usb.core
import usb.util
import time

print("=== ACESSO USB DIRETO - FTDI ===\n")

# IDs FTDI
FTDI_VID = 0x0403
FTDI_PID = 0x6014

def find_ftdi_device():
    """Encontra o dispositivo FTDI"""
    print("1. 🔍 Procurando dispositivo FTDI...")
    
    # Tentar diferentes abordagens
    devices = []
    
    # Método 1: Buscar por VID/PID
    dev = usb.core.find(idVendor=FTDI_VID, idProduct=FTDI_PID)
    if dev:
        devices.append(dev)
        print(f"   ✅ Encontrado por VID/PID: {dev}")
    
    # Método 2: Listar todos os dispositivos FTDI
    all_ftdi = usb.core.find(find_all=True, idVendor=FTDI_VID)
    for d in all_ftdi:
        if d not in devices:
            devices.append(d)
            print(f"   ✅ Encontrado: {d}")
    
    return devices

def setup_usb_communication(dev):
    """Configura comunicação USB"""
    print("\n2. 🔧 Configurando comunicação USB...")
    
    try:
        # Detach kernel driver se necessário
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)
            print("   ✅ Kernel driver detached")
        
        # Configurar dispositivo
        dev.set_configuration()
        print("   ✅ Configuração aplicada")
        
        # Obter endpoints
        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]
        
        print("   📋 Interfaces encontradas:")
        for interface in cfg:
            print(f"      Interface {interface.bInterfaceNumber}")
            for endpoint in interface:
                print(f"        Endpoint 0x{endpoint.bEndpointAddress:02x}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na configuração: {e}")
        return False

def try_bulk_transfer(dev):
    """Tenta transferência bulk (comum em FTDI)"""
    print("\n3. 📡 Tentando transferência bulk...")
    
    try:
        # Endpoints típicos do FTDI
        # EP 0x02 - Bulk OUT (host para dispositivo)
        # EP 0x81 - Bulk IN (dispositivo para host)
        
        # Tentar ler do endpoint 0x81
        print("   Lendo do endpoint 0x81...")
        data = dev.read(0x81, 64, timeout=1000)
        if data:
            text = bytes(data).decode('utf-8', errors='ignore')
            print(f"   📨 Dados recebidos: {text}")
            return True
        else:
            print("   ⏳ Nenhum dado recebido")
            
    except usb.core.USBError as e:
        print(f"   ❌ Erro USB: {e}")
    
    return False

def try_control_transfer(dev):
    """Tenta transferência de controle"""
    print("\n4. 🔄 Tentando transferência de controle...")
    
    try:
        # Comando FTDI: Get Modem Status
        # bRequest = 0x05 (FTDI SIO_GET_MODEM_STATUS)
        data = dev.ctrl_transfer(
            0xC0,  # bmRequestType: Device-to-host, Vendor, Interface
            0x05,  # bRequest: FTDI SIO_GET_MODEM_STATUS
            0x00,  # wValue: Zero
            0x00,  # wIndex: Interface
            1      # wLength: 1 byte
        )
        print(f"   📨 Status modem: 0x{data[0]:02x}")
        return True
        
    except usb.core.USBError as e:
        print(f"   ❌ Erro controle: {e}")
        return False

# Executar
try:
    devices = find_ftdi_device()
    
    if devices:
        for dev in devices:
            print(f"\n🎯 Trabalhando com dispositivo: {dev}")
            
            if setup_usb_communication(dev):
                # Tentar diferentes métodos de comunicação
                if try_control_transfer(dev) or try_bulk_transfer(dev):
                    print(f"\n✅ Comunicação estabelecida!")
                    break
            else:
                print(f"❌ Não foi possível configurar o dispositivo")
    else:
        print("❌ Nenhum dispositivo FTDI encontrado")
        
except Exception as e:
    print(f"❌ Erro geral: {e}")

print("\n" + "="*60)
print("CONCLUSÃO:")
print("="*60)
print("Se nenhum método funcionou, o FTDI está em modo especial")
print("que não permite comunicação direta via USB.")
print("")
print("💡 PRÓXIMOS PASSOS:")
print("1. Verificar documentação EXATA da placa CROC")
print("2. Contatar o fabricante da placa")
print("3. Procurar por software específico da placa")
print("="*60)