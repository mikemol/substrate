------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop
--
-- DECOMPOSED 2026-05-21 per [[file-size-one-pass-rewrite]]: the
-- former 406-line module is now a thin re-export shim over eight
-- submodules in PhaseLockedLoop/. Callers may continue using
-- `Substrate.Category.PhaseLockedLoop` directly.
--
-- Submodule decomposition:
--   PhaseLockedLoop.LockState          — lock state machine
--   PhaseLockedLoop.PLL                — the PLL primitive record
--   PhaseLockedLoop.AcquisitionStrategies
--                                       — 3-cycle / cost-gate / warmup-buffer
--   PhaseLockedLoop.LockTimeBound      — lock-time bounds proportional to prime
--   PhaseLockedLoop.Bank               — PLLBank + BankIndependence
--   PhaseLockedLoop.AcquisitionTimeline
--                                       — substrate-3cycle-timeline
--   PhaseLockedLoop.LoopParameters     — loop bandwidth + damping
--   PhaseLockedLoop.SubstratePLLBank   — substrate-4prime-bank
--
-- Per the user 2026-05-21 PLL framing: the substrate's adaptive
-- multi-Sylow predictor IS a polyphonic phase-locked loop bank.
-- Per [[multi-route-equivariance-recovery]]: a polyphonic bank of
-- single-Sylow PLLs IS the atlas-of-charts realization at the
-- temporal/dynamical level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop where

open import Substrate.Category.PhaseLockedLoop.LockState
open import Substrate.Category.PhaseLockedLoop.PLL
open import Substrate.Category.PhaseLockedLoop.AcquisitionStrategies
open import Substrate.Category.PhaseLockedLoop.LockTimeBound
open import Substrate.Category.PhaseLockedLoop.Bank
open import Substrate.Category.PhaseLockedLoop.AcquisitionTimeline
open import Substrate.Category.PhaseLockedLoop.LoopParameters
open import Substrate.Category.PhaseLockedLoop.SubstratePLLBank