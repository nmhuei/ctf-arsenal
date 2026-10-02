# Rejected rotor hypothesis

At 2026-10-01, an agent wrote `solver/solve.py` from a partial 77-state rotor
model.  That implementation filled unknown keystream entries with zero and
called the remote endpoint by default.  Its output varied across captures and
the agent subsequently retracted the apparent flag.

The file was removed from `solver/` because it was neither reproducible nor a
valid final solver.  The recorded evidence remains in the GPT session and BQA
journal.  A new solver may be placed in `solver/solve.py` only after it
reproduces one stable flag from independently collected captures.
