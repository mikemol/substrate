{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NuAbstractLimitInstance — ⟡nu-abstract-limit-instance:
-- discharge ADD 165's ω-continuity hypothesis wrem-uniq (rem-uniqueness) for the
-- CERTIFIED wedge over ℕ-div, via recon-bounded-unique — witnessing that 165's
-- conditional theorem (abstract Limit = νΦ-step under wrem-uniq) is NON-VACUOUS.
--
-- HONEST (the ADD-165 sharpening): generic Wedge ℕ-div rem-uniqueness is FALSE
-- (a = q·(suc b) + r has many (q,r) without r < suc b). It holds for the CERTIFIED
-- wedge (Wedge.Certified.CertifiedWedge ℕ-div idℕ), which BUNDLES smallness
-- (rem < b). recon-bounded-unique (ℕ-div's recon is injective on bounded residues)
-- then gives rem-uniqueness. So the ω-continuity hypothesis is satisfied EXACTLY on
-- the certified/small wedges — the concrete witness naming the certified restriction.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.NuAbstractLimitInstance where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _*_; _+_)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Algebra.Wedge using (DivStr; z; quot; rem; wedge-eq; recon; ℕ-div)
open import Substrate.Algebra.Wedge.Certified using (CertifiedWedge; wedge; small; idℕ)
open import Substrate.Algebra.Wedge.BoundedIso using (recon-bounded-unique)

------------------------------------------------------------------------
-- ① rem-UNIQUENESS for certified wedges over ℕ-div at divisor (suc b). Two certified
-- wedges a→(suc b) both satisfy a ≡ recon (quot) (suc b) (rem) (wedge-eq), and both
-- residues are small (rem < suc b), so recon-bounded-unique forces rem equality.
------------------------------------------------------------------------
cwrem-uniq : {a : ℕ} {b : ℕ}
             (w w' : CertifiedWedge ℕ-div idℕ a (suc b)) →
             rem (wedge w) ≡ rem (wedge w')
cwrem-uniq {a} {b} w w' =
  proj₂ (recon-bounded-unique
           (quot (wedge w)) (quot (wedge w')) b
           (rem (wedge w))  (rem (wedge w'))
           (small w) (small w')
           -- recon (quot w)(suc b)(rem w) ≡ a ≡ recon (quot w')(suc b)(rem w')
           (trans (sym (wedge-eq (wedge w))) (wedge-eq (wedge w'))))

------------------------------------------------------------------------
-- ② THE HYPOTHESIS DISCHARGED: 165's wrem-uniq, packaged for the certified wedge —
-- witnessing 165's conditional theorem is inhabited (the ω-continuity condition CAN
-- be met). (Decidable ℕ equality — the other hypothesis, deq — is standard; the
-- rem-uniqueness was the smallness-dependent one, discharged here.)
------------------------------------------------------------------------
-- packaged as the ADD-165 shape ({a b} (w w') → rem w ≡ rem w') over certified wedges
-- at divisor (suc b) — the concrete witness that wrem-uniq is satisfiable.
wrem-uniq-certified : {a b : ℕ}
                      (w w' : CertifiedWedge ℕ-div idℕ a (suc b)) →
                      rem (wedge w) ≡ rem (wedge w')
wrem-uniq-certified = cwrem-uniq

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out): ADD 165's ω-continuity hypothesis wrem-uniq is
-- SATISFIABLE — discharged here for the CERTIFIED wedge over ℕ-div via recon-bounded-
-- unique. Two certified wedges a→(suc b) reconstruct the SAME a with SMALL residues,
-- so ℕ-div's recon (injective on bounded residues) forces equal rem. This names the
-- certified/small restriction EXACTLY: generic wedge rem-uniqueness is FALSE (many
-- (q,r) for a = q·(suc b)+r), the certified one TRUE (smallness bundled). So 165's
-- conditional theorem (abstract Limit = νΦ-step under wrem-uniq) is NON-VACUOUS on the
-- certified wedges — and the CONSTRUCTIVE ν (divide, ADD 164) needs no such hypothesis
-- because divide IS a canonical (implicitly certified) choice. The ω-continuity
-- either/or bottoms out: the abstract limit needs certified wedges, the constructive
-- ν builds them in — recon-bounded-unique is the shared smallness certificate.
------------------------------------------------------------------------
