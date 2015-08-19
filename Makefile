SUBDIRS = daemon gpgpu
all:	$(SUBDIRS)

.PHONY: daemon
daemon:
	@cd $@ && $(MAKE)

.PHONY: gpgpu
gpgpu:
	@cd $@ && sudo $(MAKE)

.PHONY: clean
clean:
	@cd daemon && $(MAKE) clean
	@cd gpgpu  && $(MAKE) clean
