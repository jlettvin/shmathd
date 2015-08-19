# shmathd: shared memory math daemon

A cool computer is an idle computer.

TANSTATFC! "There ain't no such thing as the fastest code" (Michael Abrash).
But it is also true that most computers perform math inefficiently.
Standard libraries use SISD math instructions (8086).
Better ones use SIMD (Pentium).  Some even use MIMD (gpgpu).
All these have relative efficiencies making them "best" at something.
Many libraries vectorize or parallelize math in one way (monoculture).
Some libraries adapt for better performance on the host machine (CILK).

GOAL: This daemon is aimed at dynamic adaptation for significant gains.
Use all available math instructions.
Measure their performance in real-time during execution.
Schedule and assign execution to achieve higher performance.

Writing yet another library offering a first pass performance improvement
is not enough in an age of dynamic configuration, changing clock-rates,
and changing loads.

shmathd is intended to be a dynamically adapting core math service,
driven by atomic writes to a named pipe of a simple RPN language,
using shared memory to avoid copying,
employing all available math capabilities on the host machine,
even as those capabilities change.

As a daemon, it is a single entity responsible for all math functions.
There need be no library linkage, just atomic writes to the named pipe.
The current gpgpu portion of the code already implements most of cmath.
This implementation processes images quickly with little RPN code snippets.

The project will have phases:

* unimodal gpgpu execution path
* performance measuring code
* multimodal gpgpu and SSE/AVX execution paths
* data fragmenting and scheduling
* dynamic performance control of fragmenting and scheduling
* thorough comparison against existing static and adaptive libraries

My personal goal is to make computers hotter when there's work to do
which likely means making them cooler on average.
