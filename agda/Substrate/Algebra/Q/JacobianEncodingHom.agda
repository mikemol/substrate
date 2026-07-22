{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncodingHom — the free-algebra HOM engine.
--
-- The heavy generic half of ◆jac-gamma: the `*P`/`+P` HOMOMORPHISM laws (§3) and
-- the free-`Expr` UNIVERSAL-PROPERTY lift `homAgree` (§4), plus the point-free ℚ
-- rearrangements (§0) and `powℚ`/negation bridge lemmas (§1) they consume.
-- Imports the MINIMAL generators (`JacobianEncodingGen.Point`, opened per point).
--
-- Kept SEPARATE from the tiny generator layer so a cheap consumer (e.g. the det
-- literal, which needs only `gen-kP`) imports `JacobianEncodingGen` and does NOT
-- deserialize these larger `homAgree`/`*P` proofs at ~40× (the def/proof-separation
-- memory mechanism). The C-specific degree-9 γᵢ live one module further out
-- (`JacobianEncodingLiteral`), which opens `Point2` from here.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncodingHom where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 1ℤ; -ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (neg-*-left)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Neg using (-ℚ_)
open import Substrate.Algebra.Q.Sub using (_-ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.Embeddings using (ℤ→ℚ)
open import Substrate.Algebra.Q.Properties.Field
  using ( +ℚ-assoc; +ℚ-identityˡ; +ℚ-identityʳ
        ; *ℚ-comm; *ℚ-assoc; *ℚ-identityˡ; *ℚ-identityʳ
        ; zero-absorbˡ; zero-absorbʳ; distribˡ; distribʳ )
open import Substrate.Algebra.Q.Properties.Congruence using (+ℚ-cong; *ℚ-cong)

import Substrate.Algebra.Z.JacobianResidue as R
open R using (Mono; Term; MPoly; mono; term; addM; mulT; scaleT; _*P_; _+P_)

open import Substrate.Algebra.Q.JacobianEvalNormalize using (powℚ)

open import Substrate.Algebra.Q.JacobianExpr
  using (Expr; eX; eY; eZ; eK; _⊕E_; _⊗E_; _⊖E_; encode)

-- The minimal generator layer (E / _≋_ / gen-*), opened per point below.
open import Substrate.Algebra.Q.JacobianEncodingGen

----------------------------------------------------------------------
-- 0. Generic ℚ rearrangements (point-free; pinned; no reasoning combinator).
----------------------------------------------------------------------

-- ((a*ℚb)*ℚc)*ℚd ≈ a*ℚ(b*ℚ(c*ℚd))
assoc-lll : (a b c d : ℚ) → ((a *ℚ b) *ℚ c) *ℚ d ≋ a *ℚ (b *ℚ (c *ℚ d))
assoc-lll a b c d =
  ≈ℚ-trans {((a *ℚ b) *ℚ c) *ℚ d} {(a *ℚ b) *ℚ (c *ℚ d)} {a *ℚ (b *ℚ (c *ℚ d))}
    (*ℚ-assoc (a *ℚ b) c d)
    (*ℚ-assoc a b (c *ℚ d))

-- (a*ℚb)*ℚ(c*ℚd) ≈ (a*ℚc)*ℚ(b*ℚd)
swap4 : (a b c d : ℚ) → (a *ℚ b) *ℚ (c *ℚ d) ≋ (a *ℚ c) *ℚ (b *ℚ d)
swap4 a b c d =
  ≈ℚ-trans {(a *ℚ b) *ℚ (c *ℚ d)} {a *ℚ (b *ℚ (c *ℚ d))} {(a *ℚ c) *ℚ (b *ℚ d)}
    (*ℚ-assoc a b (c *ℚ d))
  (≈ℚ-trans {a *ℚ (b *ℚ (c *ℚ d))} {a *ℚ ((b *ℚ c) *ℚ d)} {(a *ℚ c) *ℚ (b *ℚ d)}
    (*ℚ-cong {a} {a} {b *ℚ (c *ℚ d)} {(b *ℚ c) *ℚ d}
             (≈ℚ-refl a) (≈ℚ-sym {(b *ℚ c) *ℚ d} {b *ℚ (c *ℚ d)} (*ℚ-assoc b c d)))
  (≈ℚ-trans {a *ℚ ((b *ℚ c) *ℚ d)} {a *ℚ ((c *ℚ b) *ℚ d)} {(a *ℚ c) *ℚ (b *ℚ d)}
    (*ℚ-cong {a} {a} {(b *ℚ c) *ℚ d} {(c *ℚ b) *ℚ d}
             (≈ℚ-refl a)
             (*ℚ-cong {b *ℚ c} {c *ℚ b} {d} {d} (*ℚ-comm b c) (≈ℚ-refl d)))
  (≈ℚ-trans {a *ℚ ((c *ℚ b) *ℚ d)} {a *ℚ (c *ℚ (b *ℚ d))} {(a *ℚ c) *ℚ (b *ℚ d)}
    (*ℚ-cong {a} {a} {(c *ℚ b) *ℚ d} {c *ℚ (b *ℚ d)}
             (≈ℚ-refl a) (*ℚ-assoc c b d))
    (≈ℚ-sym {(a *ℚ c) *ℚ (b *ℚ d)} {a *ℚ (c *ℚ (b *ℚ d))} (*ℚ-assoc a c (b *ℚ d))))))

-- (p*ℚp')*ℚ((q*ℚq')*ℚ(r*ℚr')) ≈ (p*ℚ(q*ℚr))*ℚ(p'*ℚ(q'*ℚr'))
swap6 : (p p′ q q′ r r′ : ℚ)
      → (p *ℚ p′) *ℚ ((q *ℚ q′) *ℚ (r *ℚ r′))
      ≋ (p *ℚ (q *ℚ r)) *ℚ (p′ *ℚ (q′ *ℚ r′))
swap6 p p′ q q′ r r′ =
  ≈ℚ-trans {(p *ℚ p′) *ℚ ((q *ℚ q′) *ℚ (r *ℚ r′))}
           {(p *ℚ p′) *ℚ ((q *ℚ r) *ℚ (q′ *ℚ r′))}
           {(p *ℚ (q *ℚ r)) *ℚ (p′ *ℚ (q′ *ℚ r′))}
    (*ℚ-cong {p *ℚ p′} {p *ℚ p′} {(q *ℚ q′) *ℚ (r *ℚ r′)} {(q *ℚ r) *ℚ (q′ *ℚ r′)}
             (≈ℚ-refl (p *ℚ p′)) (swap4 q q′ r r′))
    (swap4 p p′ (q *ℚ r) (q′ *ℚ r′))

----------------------------------------------------------------------
-- 1. `powℚ` and ℤ→ℚ / negation bridge lemmas (point-free; pinned).
----------------------------------------------------------------------

powℚ-+ : (w : ℚ) (a b : ℕ) → powℚ w (a + b) ≋ (powℚ w a) *ℚ (powℚ w b)
powℚ-+ w zero    b = ≈ℚ-sym {1ℚ *ℚ (powℚ w b)} {powℚ w b} (*ℚ-identityˡ (powℚ w b))
powℚ-+ w (suc a) b =
  ≈ℚ-trans {w *ℚ powℚ w (a + b)}
           {w *ℚ ((powℚ w a) *ℚ (powℚ w b))}
           {(w *ℚ powℚ w a) *ℚ (powℚ w b)}
    (*ℚ-cong {w} {w} {powℚ w (a + b)} {(powℚ w a) *ℚ (powℚ w b)}
             (≈ℚ-refl w) (powℚ-+ w a b))
    (≈ℚ-sym {(w *ℚ powℚ w a) *ℚ (powℚ w b)} {w *ℚ ((powℚ w a) *ℚ (powℚ w b))}
      (*ℚ-assoc w (powℚ w a) (powℚ w b)))

ℤ→ℚ-*ℚ-hom : (k l : ℤ) → ℤ→ℚ (k *ℤ l) ≋ (ℤ→ℚ k) *ℚ (ℤ→ℚ l)
ℤ→ℚ-*ℚ-hom k l = ≈ℚ-refl (ℤ→ℚ (k *ℤ l))

-- (-ℚ a) *ℚ b ≈ -ℚ (a *ℚ b): same denominator, numerators by neg-*-left.
neg-*ℚ-l : (a b : ℚ) → (-ℚ a) *ℚ b ≋ (-ℚ (a *ℚ b))
neg-*ℚ-l a b =
  cong (_*ℤ (+ suc (den-1 ((-ℚ a) *ℚ b)))) (neg-*-left (num a) (num b))

-- -ℚ is a congruence for ≋ (same denominators; numerators via neg-*-left).
neg-cong : {a b : ℚ} → a ≋ b → (-ℚ a) ≋ (-ℚ b)
neg-cong {a} {b} H =
  trans (neg-*-left (num a) (+ suc (den-1 b)))
  (trans (cong -ℤ_ H)
         (sym (neg-*-left (num b) (+ suc (den-1 a)))))

module Point2 (x y z : ℚ) where

  open Point x y z    -- E / eT / mv / gen-X/Y/Z/kP / monoval-*

  ----------------------------------------------------------------------
  -- 3. THE *P / +P HOMOMORPHISM LAWS (pinned; the shallow generator laws).
  ----------------------------------------------------------------------

  monoval-hom : (m n : Mono) → mv (addM m n) ≋ (mv m) *ℚ (mv n)
  monoval-hom (mono a b c) (mono a′ b′ c′) =
    ≈ℚ-trans {powℚ x (a + a′) *ℚ (powℚ y (b + b′) *ℚ powℚ z (c + c′))}
             {((powℚ x a) *ℚ (powℚ x a′)) *ℚ (((powℚ y b) *ℚ (powℚ y b′)) *ℚ ((powℚ z c) *ℚ (powℚ z c′)))}
             {((powℚ x a) *ℚ ((powℚ y b) *ℚ (powℚ z c))) *ℚ ((powℚ x a′) *ℚ ((powℚ y b′) *ℚ (powℚ z c′)))}
      (*ℚ-cong {powℚ x (a + a′)} {(powℚ x a) *ℚ (powℚ x a′)}
               {powℚ y (b + b′) *ℚ powℚ z (c + c′)} {((powℚ y b) *ℚ (powℚ y b′)) *ℚ ((powℚ z c) *ℚ (powℚ z c′))}
               (powℚ-+ x a a′)
               (*ℚ-cong {powℚ y (b + b′)} {(powℚ y b) *ℚ (powℚ y b′)}
                        {powℚ z (c + c′)} {(powℚ z c) *ℚ (powℚ z c′)}
                        (powℚ-+ y b b′) (powℚ-+ z c c′)))
      (swap6 (powℚ x a) (powℚ x a′) (powℚ y b) (powℚ y b′) (powℚ z c) (powℚ z c′))

  evalT-mulT : (t u : Term) → eT (mulT t u) ≋ (eT t) *ℚ (eT u)
  evalT-mulT (term m k) (term n l) =
    ≈ℚ-trans {(ℤ→ℚ (k *ℤ l)) *ℚ mv (addM m n)}
             {((ℤ→ℚ k) *ℚ (ℤ→ℚ l)) *ℚ ((mv m) *ℚ (mv n))}
             {((ℤ→ℚ k) *ℚ (mv m)) *ℚ ((ℤ→ℚ l) *ℚ (mv n))}
      (*ℚ-cong {ℤ→ℚ (k *ℤ l)} {(ℤ→ℚ k) *ℚ (ℤ→ℚ l)} {mv (addM m n)} {(mv m) *ℚ (mv n)}
               (ℤ→ℚ-*ℚ-hom k l) (monoval-hom m n))
      (swap4 (ℤ→ℚ k) (ℤ→ℚ l) (mv m) (mv n))

  evalℚ-++ : (p q : MPoly) → E (p ++ q) ≋ (E p) +ℚ (E q)
  evalℚ-++ []      q = ≈ℚ-sym {0ℚ +ℚ E q} {E q} (+ℚ-identityˡ (E q))
  evalℚ-++ (t ∷ p) q =
    ≈ℚ-trans {eT t +ℚ E (p ++ q)}
             {eT t +ℚ (E p +ℚ E q)}
             {(eT t +ℚ E p) +ℚ E q}
      (+ℚ-cong {eT t} {eT t} {E (p ++ q)} {E p +ℚ E q}
               (≈ℚ-refl (eT t)) (evalℚ-++ p q))
      (≈ℚ-sym {(eT t +ℚ E p) +ℚ E q} {eT t +ℚ (E p +ℚ E q)}
        (+ℚ-assoc (eT t) (E p) (E q)))

  evalℚ-scaleT : (t : Term) (p : MPoly) → E (scaleT t p) ≋ (eT t) *ℚ (E p)
  evalℚ-scaleT t []       = ≈ℚ-sym {eT t *ℚ 0ℚ} {0ℚ} (zero-absorbʳ (eT t))
  evalℚ-scaleT t (u ∷ us) =
    ≈ℚ-trans {eT (mulT t u) +ℚ E (scaleT t us)}
             {((eT t) *ℚ (eT u)) +ℚ ((eT t) *ℚ (E us))}
             {(eT t) *ℚ (eT u +ℚ E us)}
      (+ℚ-cong {eT (mulT t u)} {(eT t) *ℚ (eT u)} {E (scaleT t us)} {(eT t) *ℚ (E us)}
               (evalT-mulT t u) (evalℚ-scaleT t us))
      (≈ℚ-sym {(eT t) *ℚ (eT u +ℚ E us)} {((eT t) *ℚ (eT u)) +ℚ ((eT t) *ℚ (E us))}
        (distribˡ (eT t) (eT u) (E us)))

  evalℚ-*P : (p q : MPoly) → E (p *P q) ≋ (E p) *ℚ (E q)
  evalℚ-*P []      q = ≈ℚ-sym {0ℚ *ℚ E q} {0ℚ} (zero-absorbˡ (E q))
  evalℚ-*P (t ∷ p) q =
    ≈ℚ-trans {E (scaleT t q ++ (p *P q))}
             {(E (scaleT t q)) +ℚ (E (p *P q))}
             {(eT t +ℚ E p) *ℚ (E q)}
      (evalℚ-++ (scaleT t q) (p *P q))
      (≈ℚ-trans {(E (scaleT t q)) +ℚ (E (p *P q))}
                {((eT t) *ℚ (E q)) +ℚ ((E p) *ℚ (E q))}
                {(eT t +ℚ E p) *ℚ (E q)}
        (+ℚ-cong {E (scaleT t q)} {(eT t) *ℚ (E q)} {E (p *P q)} {(E p) *ℚ (E q)}
                 (evalℚ-scaleT t q) (evalℚ-*P p q))
        (≈ℚ-sym {(eT t +ℚ E p) *ℚ (E q)} {((eT t) *ℚ (E q)) +ℚ ((E p) *ℚ (E q))}
          (distribʳ (eT t) (E p) (E q))))

  ----------------------------------------------------------------------
  -- 4. THE UNIVERSAL-PROPERTY LIFT: evalℚ∘encode and the direct ℚ eval are
  --    two homs out of `Expr`, equal by ONE structural induction. The deep
  --    degree-9 composition never enters an ≋ endpoint.
  ----------------------------------------------------------------------

  evalDirect : Expr → ℚ
  evalDirect eX        = x
  evalDirect eY        = y
  evalDirect eZ        = z
  evalDirect (eK k)    = ℤ→ℚ k
  evalDirect (a ⊕E b)  = evalDirect a +ℚ evalDirect b
  evalDirect (a ⊗E b)  = evalDirect a *ℚ evalDirect b
  evalDirect (a ⊖E b)  = evalDirect a -ℚ evalDirect b

  homAgree : (e : Expr) → E (encode e) ≋ evalDirect e
  homAgree eX       = gen-X
  homAgree eY       = gen-Y
  homAgree eZ       = gen-Z
  homAgree (eK k)   = gen-kP k
  homAgree (a ⊕E b) =
    ≈ℚ-trans {E (encode a +P encode b)}
             {E (encode a) +ℚ E (encode b)}
             {evalDirect a +ℚ evalDirect b}
      (evalℚ-++ (encode a) (encode b))
      (+ℚ-cong {E (encode a)} {evalDirect a} {E (encode b)} {evalDirect b}
               (homAgree a) (homAgree b))
  homAgree (a ⊗E b) =
    ≈ℚ-trans {E (encode a *P encode b)}
             {E (encode a) *ℚ E (encode b)}
             {evalDirect a *ℚ evalDirect b}
      (evalℚ-*P (encode a) (encode b))
      (*ℚ-cong {E (encode a)} {evalDirect a} {E (encode b)} {evalDirect b}
               (homAgree a) (homAgree b))
  homAgree (a ⊖E b) =
    ≈ℚ-trans {E (encode a +P (R.kP (-suc 0) *P encode b))}
             {E (encode a) +ℚ E (R.kP (-suc 0) *P encode b)}
             {evalDirect a -ℚ evalDirect b}
      (evalℚ-++ (encode a) (R.kP (-suc 0) *P encode b))
      (+ℚ-cong {E (encode a)} {evalDirect a}
               {E (R.kP (-suc 0) *P encode b)} { -ℚ evalDirect b}
               (homAgree a) neg-part)
    where
      -- (−1)*ℚw ≈ −w, proved with endpoints matching neg-*ℚ-l exactly (`-ℚ 1ℚ`);
      -- neg1 then holds by ℤ→ℚ(-suc 0) ≡ -ℚ 1ℚ (both mkℚ (-suc 0) 0), a whole-term defeq.
      neg1w : (-ℚ 1ℚ) *ℚ evalDirect b ≋ (-ℚ evalDirect b)
      neg1w = ≈ℚ-trans {(-ℚ 1ℚ) *ℚ evalDirect b}
                       { -ℚ (1ℚ *ℚ evalDirect b)}
                       { -ℚ evalDirect b}
        (neg-*ℚ-l 1ℚ (evalDirect b))
        (neg-cong {1ℚ *ℚ evalDirect b} {evalDirect b} (*ℚ-identityˡ (evalDirect b)))
      neg1 : (ℤ→ℚ (-suc 0)) *ℚ evalDirect b ≋ (-ℚ evalDirect b)
      neg1 = neg1w
      neg-part : E (R.kP (-suc 0) *P encode b) ≋ (-ℚ evalDirect b)
      neg-part =
        ≈ℚ-trans {E (R.kP (-suc 0) *P encode b)}
                 {E (R.kP (-suc 0)) *ℚ E (encode b)}
                 { -ℚ evalDirect b}
          (evalℚ-*P (R.kP (-suc 0)) (encode b))
          (≈ℚ-trans {E (R.kP (-suc 0)) *ℚ E (encode b)}
                    {(ℤ→ℚ (-suc 0)) *ℚ evalDirect b}
                    { -ℚ evalDirect b}
            (*ℚ-cong {E (R.kP (-suc 0))} {ℤ→ℚ (-suc 0)} {E (encode b)} {evalDirect b}
                     (gen-kP (-suc 0)) (homAgree b))
            neg1)
