LATEXMK ?= latexmk
INKSCAPE ?= inkscape
export SOURCE_DATE_EPOCH := 1787011200
export XDG_CONFIG_HOME := /tmp/qops-xdg-config
export XDG_CACHE_HOME := /tmp/qops-xdg-cache
export XDG_DATA_HOME := /tmp/qops-xdg-data
FIGS := fig1_architecture fig2_quantum_value_region fig3_evidence_evolution
CLIP_NAMES := staffing-mix classical-counterfactual evidence-gate quantum-pilot independent-certificate classical-fallback outcome-ledger difficulty-vector-instrument
CLIP_SVGS := $(addprefix assets/clip-art-set/assets/,$(addsuffix .svg,$(CLIP_NAMES)))
CLIP_PNGS := $(addprefix assets/clip-art-set/assets/,$(addsuffix .png,$(CLIP_NAMES)))
FIG_SVGS := $(addprefix figs/,$(addsuffix .svg,$(FIGS)))
FIG_PDFS := $(addprefix figs/,$(addsuffix .pdf,$(FIGS)))
CLIP_SVG_STAMP := assets/clip-art-set/.svg-ready
CLIP_READY_STAMP := assets/clip-art-set/.validated-ready
MANUSCRIPT_ASSET_STAMP := figs/.manuscript-assets-ready

.PHONY: all figures clip-art tables visual-audit visual-style-audit reference-audit quantitative-audit page-audit pdf-audit static-audit checksums release-audit package clean distclean

all: main.pdf

figures: clip-art $(FIG_PDFS)

tables: tabs/table1_decision_environment.tex tabs/table2_results.tex

clip-art: $(CLIP_READY_STAMP)

visual-audit: figures
	python3 scripts/audit_svg_text_containment.py --self-test
	python3 scripts/audit_svg_text_containment.py figs/fig1_architecture.svg --require-annotations --require-classification
	python3 scripts/audit_svg_text_containment.py figs/fig2_quantum_value_region.svg --require-annotations --require-classification
	python3 scripts/audit_svg_text_containment.py figs/fig3_evidence_evolution.svg --require-annotations --require-classification

reference-audit:
	python3 scripts/audit_references.py

quantitative-audit: tables
	python3 scripts/audit_quantitative_claims.py

visual-style-audit: figures
	python3 scripts/audit_visual_style.py

page-audit: main.pdf
	python3 scripts/audit_page_budget.py

pdf-audit: main.pdf
	python3 scripts/audit_pdf_release.py

static-audit:
	python3 scripts/audit_release.py

checksums: figures tables
	python3 scripts/write_asset_checksums.py

release-audit: main.pdf visual-audit visual-style-audit reference-audit quantitative-audit page-audit pdf-audit static-audit checksums

package: release-audit
	python3 scripts/package_anonymous.py
	sha256sum packages/qops-anonymous-supplement.zip > audits/package_checksum.sha256

figs/%.pdf: figs/%.svg
	$(INKSCAPE) $< --export-type=pdf --export-filename=$@

$(CLIP_SVG_STAMP): scripts/generate_release_assets.py
	python3 scripts/generate_release_assets.py --stage clip-art
	touch $@

$(CLIP_SVGS) assets/clip-art-set/contact-sheet.svg: $(CLIP_SVG_STAMP)
	@:

assets/clip-art-set/assets/%.png: assets/clip-art-set/assets/%.svg
	$(INKSCAPE) $< --export-type=png --export-width=1024 --export-height=1024 --export-filename=$@

assets/clip-art-set/contact-sheet.png: assets/clip-art-set/contact-sheet.svg $(CLIP_SVGS)
	$(INKSCAPE) $< --export-type=png --export-width=2400 --export-filename=$@

assets/clip-art-set/clip-art-manifest.json: $(CLIP_PNGS) assets/clip-art-set/contact-sheet.png scripts/finalize_asset_manifest.py $(CLIP_SVG_STAMP)
	python3 scripts/finalize_asset_manifest.py

$(CLIP_READY_STAMP): assets/clip-art-set/clip-art-manifest.json
	python3 scripts/validate_clip_art_package.py
	touch $@

$(MANUSCRIPT_ASSET_STAMP): $(CLIP_READY_STAMP) scripts/generate_release_assets.py data/locked_c12_records.csv data/locked_c12_summary.json data/locked_rerun_records.csv data/locked_rerun_summary.json data/shared_field_reproduction.json
	python3 scripts/generate_release_assets.py --stage manuscript
	touch $@

$(FIG_SVGS) tabs/table1_decision_environment.tex tabs/table2_results.tex figs/fig1_architecture.tex figs/fig2_quantum_value_region.tex figs/fig3_evidence_evolution.tex: $(MANUSCRIPT_ASSET_STAMP)
	@:

main.pdf: main.tex references.bib figures tables reference-audit quantitative-audit
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error main.tex

clean:
	$(LATEXMK) -c main.tex

distclean: clean
	rm -f main.pdf figs/*.pdf assets/clip-art-set/assets/*.png assets/clip-art-set/contact-sheet.png $(CLIP_SVG_STAMP) $(CLIP_READY_STAMP) $(MANUSCRIPT_ASSET_STAMP)
