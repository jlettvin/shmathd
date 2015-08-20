#!/usr/bin/env make
MODULE=gpu11
BANNER=python ../Banner.py -c "yb"

CHECKERIMG=img/checkers_0060_01.png
NOISYIMG=img/gray_0.03_0.30.png
IMGS=$(CHECKERIMG)

MAKES=$(CHECKERIMG) $(NOISYIMG)

# Makefile
# __date__       = "20130101"
# __author__     = "jlettvin"
# __maintainer__ = "jlettvin"
# __email__      = "jlettvin@gmail.com"
# __copyright__  = "Copyright(c) 2013-2015 Jonathan D. Lettvin, All Rights Reserved"
# __license__    = "Trade Secret"
# __status__     = "Production"
# __version__    = "0.0.1"

.PHONY: all
all:	$(MODULE).py $(MAKES) Makefile
	@$(BANNER) "run $(MODULE)"
	@./$(MODULE).py

.PHONY: clean
clean:
	@$(BANNER) "clean gpgpu directory"
	@rm -f img/checkers*.png img/gray*.png
	@rm -f RPN_CUDA_*.txt RPN_sourceCode.c
	@rm -f img/target.png

$(CHECKERIMG):	make_checkers.py Makefile
	@$(BANNER) "make checkers figures"
	@mkdir -p -m 777 img
	@for i in 1 2 3 4 5 6 10 12 15 20 30; do ./$< 60 $$i; done

$(NOISYIMG):	make_noisyboundary.py Makefile
	@$(BANNER) "make noisy figures"
	@mkdir -p -m 777 img
	@for i in 3e-2 5e-2; \
		do for j in 3e-1 5e-1; \
		do ./$< $$i $$j; \
		done; \
	done

include include/tgz.mk
