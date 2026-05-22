------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.OrbitName
--
-- OrbitName: an 8-element data tag for the named orbits.
-- orbit-of : OrbitName → ReferenceOrbit dispatches each name to its
-- corresponding orbit value.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.OrbitName where

open import Substrate.Category.ReferenceOrbit.Record using (ReferenceOrbit)
open import Substrate.Category.ReferenceOrbit.QUOT using (QUOT)
open import Substrate.Category.ReferenceOrbit.ChainBackRef using (ChainBackRef)
open import Substrate.Category.ReferenceOrbit.ByteBackRef using (ByteBackRef)
open import Substrate.Category.ReferenceOrbit.QUOTRecent using (QUOTRecent)
open import Substrate.Category.ReferenceOrbit.OneShotSlice using (OneShotSlice)
open import Substrate.Category.ReferenceOrbit.ChamberFreeQUOT using (ChamberFreeQUOT)
open import Substrate.Category.ReferenceOrbit.ChamberFreeQUOTRecent using (ChamberFreeQUOTRecent)
open import Substrate.Category.ReferenceOrbit.ChamberFreeOneShotSlice using (ChamberFreeOneShotSlice)

data OrbitName : Set where
  QUOT-orbit                    : OrbitName
  ChainBackRef-orbit            : OrbitName
  ByteBackRef-orbit             : OrbitName
  QUOTRecent-orbit              : OrbitName
  OneShotSlice-orbit            : OrbitName
  ChamberFreeQUOT-orbit         : OrbitName
  ChamberFreeQUOTRecent-orbit   : OrbitName
  ChamberFreeOneShotSlice-orbit : OrbitName

orbit-of : OrbitName → ReferenceOrbit
orbit-of QUOT-orbit                    = QUOT
orbit-of ChainBackRef-orbit            = ChainBackRef
orbit-of ByteBackRef-orbit             = ByteBackRef
orbit-of QUOTRecent-orbit              = QUOTRecent
orbit-of OneShotSlice-orbit            = OneShotSlice
orbit-of ChamberFreeQUOT-orbit         = ChamberFreeQUOT
orbit-of ChamberFreeQUOTRecent-orbit   = ChamberFreeQUOTRecent
orbit-of ChamberFreeOneShotSlice-orbit = ChamberFreeOneShotSlice
