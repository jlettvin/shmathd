#!/usr/bin/env make

# -Wall 					check for all warnings and errors
# -Wno-format-security		ignore protections for instruction buffers
# -Wno-self-assign			ignore argc=argc and argv=argv used to pass syntax
CFLAGS=-Wall -Wno-format-security -Wno-self-assign
BANNER=python ../Banner.py -b -c "wg"

.PHONY: all
all:	shmathd shm_server shm_client
	@$(BANNER) "TODO: Run shared memory tests."
	@$(BANNER) "TODO: integrate shm_server.c into shmathd."

.PHONY: clean
clean:
	@$(BANNER) "clean daemon directory"
	@rm -f shmathd shm_server shm_client

shm_client:	shm_client.c Makefile
	@$(BANNER) "make shared memory test client"
	@gcc -o $@ $<

shm_server:	shm_server.c Makefile
	@$(BANNER) "make shared memory test server"
	@gcc -o $@ $<

shmathd:	shmathd.cpp Makefile
	@$(BANNER) "make daemon"
	@g++ $(CFLAGS) -o $@ $<
