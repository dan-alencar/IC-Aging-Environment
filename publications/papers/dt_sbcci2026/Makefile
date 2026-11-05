# One command regenerates everything from the raw CSVs in data/campaigns/:
#   make            analysis -> values.tex -> figures -> PDF -> checks
#   make analysis   only the Python pipeline
#   make pdf        only LaTeX
#   make check      word/reference budget and number audit
#   make clean      remove generated outputs and LaTeX build files
PY      := .venv/bin/python
GEN     := generated
MS      := manuscript

.PHONY: all venv analysis pdf check clean package

all: analysis pdf check

venv: .venv/bin/python
.venv/bin/python:
	python3 -m venv .venv
	$(PY) -m pip install -q numpy scipy pandas matplotlib

analysis: venv
	$(PY) analysis/inventory.py > /dev/null
	$(PY) analysis/run_analysis.py
	$(PY) analysis/pid_bench.py > /dev/null
	$(PY) analysis/derive.py            # first pass: results_derived.json (figures need it)
	$(PY) analysis/make_figures.py
	$(PY) analysis/derive.py            # second pass: figure-derived macros

pdf:
	cd $(MS) && latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex > /dev/null
	cp $(MS)/build/main.pdf main.pdf
	@! grep -n "Overfull" $(MS)/build/main.log || (echo "overfull boxes above"; true)

check: venv
	$(PY) analysis/wordcount.py
	$(PY) analysis/audit_numbers.py

# Submission bundle: PDF, standalone LaTeX source, figures (PDF/EPS/600-dpi TIFF),
# generating scripts and data checksums, plus a zip of the whole folder.
PKG_DATE ?= $(shell date +%Y-%m-%d)
PKG      := submission/$(PKG_DATE)
package: all
	rm -rf $(PKG) && mkdir -p $(PKG)/latex/figures $(PKG)/figures $(PKG)/sources/analysis
	cp main.pdf $(PKG)/Alencar_DT_SBCCI2026.pdf
	sed 's|\\input{../generated/values.tex}|\\input{values.tex}|' $(MS)/main.tex > $(PKG)/latex/main.tex
	cp $(GEN)/values.tex $(PKG)/latex/
	cp $(MS)/figures/*.pdf $(PKG)/latex/figures/
	cp $(MS)/figures/*.pdf $(MS)/figures/*.eps $(MS)/figures/*.tif $(PKG)/figures/
	cp analysis/*.py analysis/number_whitelist.txt $(PKG)/sources/analysis/
	cp Makefile README.md $(PKG)/sources/
	cp ../../../data/campaigns/SHA256SUMS $(PKG)/sources/
	cp ../../../data/campaigns/README.md $(PKG)/sources/DATA_README.md
	cp analysis/PACKAGE_README.md $(PKG)/README.md
	# shipped copies: drop references to the internal reconciliation note
	sed -i -e 's/(not reproduced; see RECONCILIATION 14)/(quoted)/' -e 's/(not reproduced)/(quoted)/' $(PKG)/sources/analysis/number_whitelist.txt
	sed -i -e '/RECONCILIATION/d' -e 's/, and renders `RECONCILIATION.md`//' $(PKG)/sources/README.md
	cd $(PKG)/latex && latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=_check main.tex > /dev/null && rm -rf _check && echo "standalone LaTeX source compiles"
	cd submission && rm -f dt_sbcci2026_$(PKG_DATE).zip && zip -qr dt_sbcci2026_$(PKG_DATE).zip $(PKG_DATE) && echo "wrote submission/dt_sbcci2026_$(PKG_DATE).zip"

clean:
	rm -rf $(MS)/build $(GEN)/*.json $(GEN)/values.tex $(GEN)/inventory.csv main.pdf
