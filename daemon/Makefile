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
# -Wall 					check for all warnings and errors
# -Wno-format-security		ignore protections for instruction buffers
# -Wno-self-assign			ignore argc=argc and argv=argv used to pass syntax
###############################################################################

###############################################################################
HOME=..
BANNER=python $(HOME)/Banner/Banner.py -b -t "wg!"
CFLAGS=-Wall -Wno-format-security -Wno-self-assign
PYPATH=$(PYTHONPATH):$(HOME)/Banner

###############################################################################
.PHONY: all
all:	shmathd shm_server shm_client
	@$(BANNER) "daemon TODO: Run shared memory tests."
	@$(BANNER) "daemon TODO: integrate shm_server.c into shmathd."

###############################################################################
.PHONY: clean
clean:
	@$(BANNER) "daemon: clean daemon directory"
	@rm -f shmathd shm_server shm_client

###############################################################################
shm_client:	shm_client.c Makefile
	@$(BANNER) "daemon: make shared memory test client"
	@gcc -o $@ $<

###############################################################################
shm_server:	shm_server.c Makefile
	@$(BANNER) "daemon: make shared memory test server"
	@gcc -o $@ $<

###############################################################################
shmathd:	shmathd.cpp Makefile
	@$(BANNER) "daemon: make daemon"
	@g++ $(CFLAGS) -o $@ $<
###############################################################################

###############################################################################
lint:	shmathd.cpp Makefile
	@$(BANNER) "daemon: no lint checking yet"

