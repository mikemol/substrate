# jea/metalanguage — build the .agdai shim (Agda Interface → JSON core nodes).
#
# The shim links Agda's OWN version-matched serialiser (EmbPrj): the linked Agda MUST be the SAME build
# that produced the .agdai you decode (interface hashes must match exactly), else the shim errors
# "decode Nothing (stale/wrong-version)". This repo is used under BOTH Agda 2.6.3 and 2.8.0 — the shim
# must be (re)built against whichever produced the current _build/*/.agdai. Pick the version explicitly:
#
#   make -C jea/metalanguage shim                       # default: -package Agda (the db's current)
#   make -C jea/metalanguage shim AGDA_PKG=Agda-2.6.3   # pin 2.6.3
#   make -C jea/metalanguage shim AGDA_PKG=Agda-2.8.0   # pin 2.8.0
#   make -C jea/metalanguage clean-shim
# (a fresh full agda build regenerates the .agdai to match the current Agda, if they have drifted.)

GHC ?= ghc
AGDA_PKG ?= Agda
GHCFLAGS ?= -package $(AGDA_PKG) -O0
SHIM := agdai_shim

.PHONY: shim clean-shim
shim: $(SHIM)

$(SHIM): $(SHIM).hs
	$(GHC) $(GHCFLAGS) -o $@ $<

clean-shim:
	rm -f $(SHIM) $(SHIM).hi $(SHIM).o
