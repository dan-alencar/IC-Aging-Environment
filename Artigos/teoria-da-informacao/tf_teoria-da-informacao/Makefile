# Reprodução completa do TF: dados (CSV) -> análise -> figuras/valores -> PDFs.
#
#   make            # venv + análise + todos os PDFs
#   make analysis   # só o pipeline Python (regrava latex/generated e latex/figures)
#   make pdf        # só o LaTeX (main_pt, seminar, main)
#   make clean      # remove auxiliares do LaTeX e caches Python
#   make distclean  # clean + remove .venv e os PDFs compilados
#
# Requisitos: python3 (>=3.10) e uma distribuição TeX com latexmk
# (TeX Live: texlive-latex-extra, texlive-lang-portuguese, texlive-science, latexmk).

PYTHON  ?= python3
VENV    := .venv
PY      := $(VENV)/bin/python
LATEXMK ?= latexmk -pdf -interaction=nonstopmode -halt-on-error

DOCS := main_pt seminar main

.PHONY: all venv analysis pdf clean distclean

all: analysis pdf

venv: $(VENV)/.installed

$(VENV)/.installed: analysis/requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r analysis/requirements.txt
	touch $@

# A ordem importa: cada script preenche só as suas macros em values.tex,
# e make_figures.py importa dos demais.
analysis: venv
	cd analysis && ../$(PY) tier1_pipeline.py
	cd analysis && ../$(PY) kl_benches.py
	cd analysis && ../$(PY) ica_separation.py
	cd analysis && ../$(PY) kalman_rul.py
	cd analysis && ../$(PY) make_figures.py

pdf:
	cd latex && for d in $(DOCS); do $(LATEXMK) $$d.tex || exit 1; done

clean:
	-cd latex && latexmk -c $(addsuffix .tex,$(DOCS))
	cd latex && rm -f *.aux *.bbl *.blg *.fdb_latexmk *.fls *.log *.nav *.out *.snm *.toc *.vrb *.synctex.gz
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

distclean: clean
	rm -rf $(VENV)
	cd latex && rm -f $(addsuffix .pdf,$(DOCS))
