# Residue — Substrate.Groups.Coxeter.Core.IdemInequality

Lines the split of `agda/Substrate/Groups/Coxeter/Core/IdemInequality.agda` could not place in any leaf.
They are recorded, not discarded: each carries the line number it
held in the original file. Re-home them deliberately, or delete
them deliberately — but do it as a decision, not as a side effect.

   21    (Word : Set)
   22    (Canonical : Word → Set)
   23    (normalize : Word → Word)
   24    (normalize-canonical : (w : Word) → Canonical (normalize w))
   25    (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
   26    where
