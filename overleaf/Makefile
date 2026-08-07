LATEXMK ?= latexmk
INKSCAPE ?= inkscape
FIGS := fig1_teaser fig2_benchmark_taxonomy fig3_uwcq_pipeline fig4_literature_map fig5_results_dashboard fig6_open_questions_map

.PHONY: all figures visual-audit clean distclean

all: main.pdf

figures: $(addprefix figs/,$(addsuffix .pdf,$(FIGS)))

visual-audit: figures
	python3 scripts/audit_svg_text_containment.py figs/fig2_benchmark_taxonomy.svg --require-annotations
	python3 scripts/audit_svg_text_containment.py figs/fig6_open_questions_map.svg --require-annotations

figs/%.pdf: figs/%.svg
	$(INKSCAPE) $< --export-type=pdf --export-filename=$@

figs/fig1_teaser.svg figs/fig2_benchmark_taxonomy.svg figs/fig3_uwcq_pipeline.svg figs/fig4_literature_map.svg figs/fig5_results_dashboard.svg figs/fig6_open_questions_map.svg: scripts/make_figures.py data/locked_c12_records.csv
	python3 scripts/make_figures.py

main.pdf: main.tex references.bib figures
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error main.tex

clean:
	$(LATEXMK) -c main.tex

distclean: clean
	rm -f main.pdf figs/*.pdf
