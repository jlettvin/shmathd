SUBDIRS = daemon gpgpu
all:	$(SUBDIRS)

.PHONY: daemon
daemon:
	@python Banner.py "make daemon"
	@cd $@ && $(MAKE)

.PHONY: gpgpu
gpgpu:
	@python Banner.py "make gpgpu RPN engine"
	@cd $@ && sudo $(MAKE)

.PHONY: clean
clean:
	@python Banner.py "clean daemon and gpgpu directories"
	@cd daemon && $(MAKE) clean
	@cd gpgpu  && $(MAKE) clean
