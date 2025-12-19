# ==============================================================================
# Makefile Corrigido e Otimizado para o projeto helloworld
# Baseado na lógica de um Makefile funcional de referência.
# ==============================================================================

# ------------------------------------------------------------------------------
# Toolchain - Verifique se 'RISCV_PREFIX' está correto para o seu ambiente.
# 'riscv-none-elf-' é o padrão para bare-metal.
# ------------------------------------------------------------------------------
RISCV_XLEN    ?= 32
RISCV_MARCH   ?= rv$(RISCV_XLEN)imc_zicsr
RISCV_MABI    ?= ilp32
RISCV_PREFIX  ?= riscv32-unknown-elf-
RISCV_CC      ?= $(RISCV_PREFIX)gcc
RISCV_LD      ?= $(RISCV_PREFIX)ld
RISCV_OBJCOPY ?= $(RISCV_PREFIX)objcopy

# Flags de Compilação e Linkagem
# CORREÇÃO 1: Flags unificadas e seguras. Inclui os diretórios 'lib/inc' e o
# diretório atual ('.') sem causar problemas com espaços no caminho.
RISCV_CCFLAGS  ?= -march=$(RISCV_MARCH) -mabi=$(RISCV_MABI) -static -std=gnu99 -O2 -nostdlib -nostartfiles -ffreestanding -I. -Ilib/inc
RISCV_LDFLAGS  ?= -Tlink.ld -mno-relax -Wl,--no-warn-rwx-segments -lgcc

# ------------------------------------------------------------------------------
# Arquivos Fonte
# ------------------------------------------------------------------------------
BINDIR 	  ?= bin
CRT0 	  ?= crt0.S
MAIN_SRC  ?= helloworld.c

# CORREÇÃO 2: Lista explícita de TODOS os arquivos da biblioteca necessários.
# Isso garante que todas as funções (uart, print, gpio, etc.) sejam compiladas.
LIB_SOURCES := lib/src/gpio.c \
               lib/src/print.c \
               lib/src/timer.c \
               lib/src/uart.c 

# Gera automaticamente os nomes dos arquivos objeto (.o) a partir dos fontes.
CRT0_OBJ    := $(CRT0:.S=.o)
MAIN_OBJ    := $(MAIN_SRC:.c=.o)
LIB_OBJS    := $(LIB_SOURCES:.c=.o)
ALL_OBJS    := $(MAIN_OBJ) $(CRT0_OBJ) $(LIB_OBJS)

# ------------------------------------------------------------------------------
# Regras Principais de Compilação
# ------------------------------------------------------------------------------

# O alvo padrão 'all' compila o executável principal.
all: $(BINDIR)/$(MAIN_SRC:.c=.elf)

# Cria o diretório 'bin' se ele não existir.
$(BINDIR):
	mkdir -p $(BINDIR)

# CORREÇÃO 3: Regra de linkagem única e robusta.
# Junta o objeto principal, o crt0 e TODOS os objetos da biblioteca para criar o .elf.
$(BINDIR)/$(MAIN_SRC:.c=.elf): $(ALL_OBJS) | $(BINDIR)
	$(RISCV_CC) $(RISCV_CCFLAGS) -o $@ $^ $(RISCV_LDFLAGS)

# Regra genérica para compilar qualquer arquivo .c em um .o.
%.o: %.c
	$(RISCV_CC) $(RISCV_CCFLAGS) -c $< -o $@

# Regra genérica para compilar qualquer arquivo .S em um .o.
%.o: %.S
	$(RISCV_CC) $(RISCV_CCFLAGS) -c $< -o $@

# ------------------------------------------------------------------------------
# Regra para Gerar o Arquivo de Memória (`make mem`)
# ------------------------------------------------------------------------------
.PHONY: mem

# O alvo `make mem` agora depende do arquivo .elf, que aciona toda a compilação.
mem: $(BINDIR)/helloworld.mem

# Converte o .elf para .bin.
$(BINDIR)/%.bin: $(BINDIR)/%.elf
	$(RISCV_OBJCOPY) -O binary $< $@

# Converte o .bin para .mem no formato correto para o Vivado ($readmemh).
$(BINDIR)/%.mem: $(BINDIR)/%.bin
	echo "@00000000" > $@ && hexdump -v -e '1/4 "%08x\n"' $< >> $@

# ------------------------------------------------------------------------------
# Limpeza
# ------------------------------------------------------------------------------
.PHONY: clean

# CORREÇÃO 4: A regra 'clean' agora apaga TODOS os objetos, onde quer que estejam.
clean:
	rm -rf $(BINDIR)
	rm -f $(ALL_OBJS)
