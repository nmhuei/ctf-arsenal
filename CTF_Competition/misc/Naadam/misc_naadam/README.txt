Naadam-8
========

A first-person voxel handheld that exists nowhere else.

  naadam    - the console (a single self-contained binary; the remote runs exactly this)
  game.n8   - one cartridge

The console reads ONE cartridge on standard input and answers only in pictures
(binary PPM frames on standard output). The remote runs the same console on the
cartridge you send it and streams the frames back.

Everything else — how a cartridge is framed, what it may do, and how to read what
the machine draws — is yours to reverse. The flag is inside the machine.
