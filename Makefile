#!/usr/bin/env make
###############################################################################
# __date__       = "20150815"
# __author__     = "jlettvin"
# __maintainer__ = "jlettvin"
# __email__      = "jlettvin@gmail.com"
# __copyright__  = "Copyright(c) 2015 Jonathan D. Lettvin, All Rights Reserved"
# __license__    = "Trade Secret"
# __status__     = "Production"
# __version__    = "0.0.1"
###############################################################################

###############################################################################
HOME=.
SUBDIRS=daemon gpgpu
BANNER=python $(HOME)/Banner/Banner.py -b -t "w0!"
MESSAGE=$(filter-out commit,$(message))
BUILDID=$(shell date +%Y%m%d-%H:%M:%S)
PYPATH=$(PYTHONPATH):$(HOME)/Banner

###############################################################################
all:	$(SUBDIRS)

###############################################################################
.PHONY: daemon
daemon:
	@$(BANNER) "make daemon"
	@cd $@ && $(MAKE) lint
	@cd $@ && $(MAKE)

###############################################################################
.PHONY: gpgpu
gpgpu:
	@$(BANNER) "make gpgpu RPN engine"
	@cd $@ && $(MAKE) lint
	@cd $@ && sudo $(MAKE)

###############################################################################
.PHONY: clean
clean:
	@$(BANNER) "clean project"
	@cd daemon && $(MAKE) clean
	@cd gpgpu  && $(MAKE) clean

###############################################################################
.PHONY: commit
commit:
	@$(BANNER) "commit and push project and submodules"
ifeq ("$(MESSAGE)", "")
	@echo "Usage: make commit message='{commit-message}'".
else
	@echo "Causes problems."
	#git add .
	#git commit \
		#--author="Jonathan D. Lettvin <jlettvin@gmail.com>" \
		#-a \
		#-m '$(BUILDID) $(MESSAGE)'
	#git push --recurse-submodules=on-demand;
endif
