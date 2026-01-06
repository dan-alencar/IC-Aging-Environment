import pyvisa as visa

rm = visa.ResourceManager('@py') # Use '@py' para o pyvisa-py backend
resources = rm.list_resources()
print("Recursos Encontrados:")
for res in resources:
    print(res)
rm.close()
