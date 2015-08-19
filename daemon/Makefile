#!/usr/bin/env make

# -Wall 					check for all warnings and errors
# -Wno-format-security		ignore protections for instruction buffers
# -Wno-self-assign			ignore argc=argc and argv=argv used to pass syntax
CFLAGS=-Wall -Wno-format-security -Wno-self-assign

all:	shmathd

shmathd:	shmathd.cpp Makefile
	@g++ $(CFLAGS) -o $@ $<
