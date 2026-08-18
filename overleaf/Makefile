LATEXMK ?= latexmk
INKSCAPE ?= inkscape
PAPER_SKILL := ../skills/build-evidence-grounded-overleaf-paper
FIGS := fig1_architecture fig2_quantum_value_region fig3_evidence_evolution
CLIP_NAMES := staffing-mix classical-counterfactual evidence-gate quantum-pilot independent-certificate classical-fallback outcome-ledger
CLIP_SVGS := $(addprefix assets/clip-art-set/assets/,$(addsuffix .svg,$(CLIP_NAMES)))
CLIP_PNGS := $(addprefix assets/clip-art-set/assets/,$(addsuffix .png,$(CLIP_NAMES)))

.PHONY: all figures clip-art tables visual-audit clean distclean

all: main.pdf

figures: $(addprefix figs/,$(addsuffix .pdf,$(FIGS))) clip-art

tables: tabs/table1_decision_environment.tex tabs/table2_results.tex

clip-art: $(CLIP_PNGS) assets/clip-art-set/contact-sheet.png assets/clip-art-set/clip-art-manifest.json

visual-audit: figures
	python3 $(PAPER_SKILL)/scripts/audit_svg_text_containment.py --self-test
	python3 $(PAPER_SKILL)/scripts/audit_svg_text_containment.py figs/fig1_architecture.svg --require-annotations --require-classification
	python3 $(PAPER_SKILL)/scripts/audit_svg_text_containment.py figs/fig2_quantum_value_region.svg --require-classification
	python3 $(PAPER_SKILL)/scripts/audit_svg_text_containment.py figs/fig3_evidence_evolution.svg --require-annotations --require-classification

figs/%.pdf: figs/%.svg
	$(INKSCAPE) $< --export-type=pdf --export-filename=$@

$(addprefix figs/,$(addsuffix .svg,$(FIGS))) $(CLIP_SVGS) assets/clip-art-set/contact-sheet.svg tabs/table1_decision_environment.tex tabs/table2_results.tex: scripts/generate_release_assets.py data/locked_c12_records.csv data/locked_c12_summary.json data/locked_rerun_summary.json
	python3 scripts/generate_release_assets.py

assets/clip-art-set/assets/%.png: assets/clip-art-set/assets/%.svg
	$(INKSCAPE) $< --export-type=png --export-width=1024 --export-height=1024 --export-filename=$@

assets/clip-art-set/contact-sheet.png: assets/clip-art-set/contact-sheet.svg $(CLIP_SVGS)
	$(INKSCAPE) $< --export-type=png --export-width=2400 --export-filename=$@

assets/clip-art-set/clip-art-manifest.json: $(CLIP_PNGS) assets/clip-art-set/contact-sheet.png scripts/finalize_asset_manifest.py
	python3 scripts/finalize_asset_manifest.py

main.pdf: main.tex references.bib figures tables
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error main.tex

clean:
	$(LATEXMK) -c main.tex

distclean: clean
	rm -f main.pdf figs/*.pdf assets/clip-art-set/assets/*.png assets/clip-art-set/contact-sheet.png
