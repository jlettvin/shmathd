#!/usr/bin/env make
###############################################################################
# Makefile
# __date__       = "20150815"
# __author__     = "jlettvin"
# __maintainer__ = "jlettvin"
# __email__      = "jlettvin@gmail.com"
# __copyright__  = "Copyright(c) 2015 Jonathan D. Lettvin, All Rights Reserved"
# __license__    = "Trade Secret"
# __status__     = "Production"
# __version__    = "0.0.1"
###############################################################################
# git submodule add https://github.com/jlettvin/Banner
###############################################################################

###############################################################################
HOME=..
BANNER=python $(HOME)/Banner/Banner.py -b -t "wb!"
MODULE=gpu11
CHECKERIMG=img/checkers_0060_01.png
NOISYIMG=img/gray_0.03_0.30.png
IMGS=$(CHECKERIMG)
MAKES=$(CHECKERIMG) $(NOISYIMG)
PYPATH=$(HOME)/Banner

###############################################################################
.PHONY: all
all:	$(MODULE).py $(MAKES) Makefile
	@$(BANNER) "$(MODULE): all"
	@PYTHONPATH=$(PYPATH) python $(MODULE).py

###############################################################################
.PHONY: clean
clean:
	@$(BANNER) "$(MODULE): clean gpgpu directory"
	@rm -f img/checkers*.png img/gray*.png
	@rm -f RPN_CUDA_*.txt RPN_sourceCode.c
	@rm -f img/target.png
	@rm -f *.pep8 *.pylint *.pyflakes

###############################################################################
$(CHECKERIMG):	make_checkers.py Makefile
	@$(BANNER) "$(MODULE): make checkers figures"
	@mkdir -p -m 777 img
	@for i in 1 2 3 4 5 6 10 12 15 20 30; do ./$< 60 $$i; done

###############################################################################
$(NOISYIMG):	make_noisyboundary.py Makefile
	@$(BANNER) "$(MODULE): make noisy figures"
	@mkdir -p -m 777 img
	@for i in 3e-2 5e-2; \
		do for j in 3e-1 5e-1; \
		do ./$< $$i $$j; \
		done; \
	done

###############################################################################
lint: $(MODULE).py
	@$(BANNER) "$(MODULE): lint"
	@-pep8 $< > $<.pep8 2>&1
	@-pylint $< > $<.pylint 2>&1
	@-pyflakes $< > $<.pyflakes 2>&1

###############################################################################
include include/tgz.mk
###############################################################################
