#!/usr/bin/env make
DATETIME=`date +%Y%m%d%H%M%S`
MAIN=${MODULE}.py

.PHONY: tgz
tgz:
	@echo ${DATETIME} incremental backup
	@mkdir -p tgz
	@tar cvzf tgz/${MODULE}.src.${DATETIME}.tgz \
		*.py \
		Makefile \
		*.tex \
		*.bib \
		*.png \
		*.pdf

.IGNORE:
	@tar cvzf tgz/${MODULE}.src.${DATETIME}.tgz . \
	  --exclude=".git" \
	  --exclude=".ropeproject" \
	  --exclude="latex/tgz" \
	  --exclude="old.*" \
	  --exclude="*.old" \
	  --exclude="latex.old" \
	  --exclude="*.perf" \
	  --exclude="*.prof" \
	  --exclude="*.pyc" \
	  --exclude="*/*.swp" \
	  --exclude="*.swp" \
	  --exclude="*.tgz" \
	  --exclude="log" \
	  --exclude="tgz" \
	  --exclude="old" \
	  --exclude="tmp" \
	  --exclude="img" \
	  --exclude=".git/*" \
	  --exclude="img/*" \
	  --exclude="log/*" \
	  --exclude="old/*" \
	  --exclude="latex.old/*" \
	  --exclude="latex/tgz/*" \
	  --exclude="old/*" \
	  --exclude="tgz/*" \
	  --exclude="tmp/*" \
	  --exclude="graph/*" \
	  --exclude="spine/*" \
	  --exclude="kernels/*" \
	  --exclude="unsorted/*" \
	  --exclude="download/*"
