#!/usr/bin/env make

###############################################################################
HOME=.
UTIL=$(HOME)/util
SUBDIRS=daemon gpgpu
BANNER=python $(UTIL)/Banner.py -b -t "w0!"
MESSAGE=$(filter-out commit,$(message))
BUILDID=$(shell date +%Y%m%d-%H:%M:%S)

###############################################################################
all:	$(SUBDIRS)

###############################################################################
.PHONY: daemon
daemon:
	@$(BANNER) "make daemon"
	@cd $@ && $(MAKE)

###############################################################################
.PHONY: gpgpu
gpgpu:
	@$(BANNER) "make gpgpu RPN engine"
	@cd $@ && sudo $(MAKE)

###############################################################################
.PHONY: clean
clean:
	@$(BANNER) "clean daemon and gpgpu directories"
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
