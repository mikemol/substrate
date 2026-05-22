------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.LockState
--
-- Lock state machine for the PLL bank.
-- A PLL transitions through four lock states; transitions form a
-- relation; ForwardOnly captures the (3+1) acquisition arrow plus
-- lost-lock chirality.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.LockState where

data LockState : Set where
  unlocked  : LockState
  acquiring : LockState
  locked    : LockState
  lost-lock : LockState

------------------------------------------------------------------------
-- Discrete transitions on the lock state machine.

data LockTransition : LockState → LockState → Set where
  begin-acquire  : LockTransition unlocked acquiring
  acquire-lock   : LockTransition acquiring locked
  drop-lock      : LockTransition locked lost-lock
  reacquire      : LockTransition lost-lock acquiring
  stay-unlocked  : LockTransition unlocked unlocked
  stay-acquiring : LockTransition acquiring acquiring
  stay-locked    : LockTransition locked locked
  stay-lost-lock : LockTransition lost-lock lost-lock

------------------------------------------------------------------------
-- Forward-only transitions (3+1 lock-acquisition arrow).

data ForwardOnly : LockState → LockState → Set where
  fwd-acquire : ForwardOnly unlocked acquiring
  fwd-lock    : ForwardOnly acquiring locked
