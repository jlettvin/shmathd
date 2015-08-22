SUBDIRS = daemon gpgpu
BANNER=python ./Banner.py -b -c "w0!"

all:	$(SUBDIRS)

.PHONY: daemon
daemon:
	@$(BANNER) "make daemon"
	@cd $@ && $(MAKE)

.PHONY: gpgpu
gpgpu:
	@$(BANNER) "make gpgpu RPN engine"
	@cd $@ && sudo $(MAKE)

.PHONY: clean
clean:
	@$(BANNER) "clean daemon and gpgpu directories"
	@cd daemon && $(MAKE) clean
	@cd gpgpu  && $(MAKE) clean
