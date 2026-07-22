{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncodingLiteral — ◆jac-gamma, THE LITERAL CLOSE.
--
-- Closes the ⟡jac-encoding-bridge single-object identification at the LITERAL
-- ℚ-function level:
--
--     literalᵢ : (x y z : ℚ) → evalℚ x y z R.fᵢ ≋ C.fᵢ x y z
--
-- HALF A's curried-ℚ `C.fᵢ` (JacobianCollision) and HALF B's MPoly `R.fᵢ`
-- (JacobianResidue) are the SAME paper map F, WHEN EVALUATED at any point.
--
-- ⚑ THE METHOD — a FREE-ALGEBRA UNIVERSAL-PROPERTY LIFT, not hand-composed ≈ℚ.
-- The transparent eta-record `≈ℚ` defeats endpoint INFERENCE (the wall). Rather
-- than hand-pin a degree-9 ≋ chain, the deep composition is lifted by a single
-- UNIQUENESS induction: `Expr` is the free commutative-ring term on {x,y,z,+,*ℚ,−};
-- `evalℚ ∘ encode` and the direct ℚ evaluation are two homomorphisms out of it,
-- and `homAgree` proves them equal by structural induction — each constructor a
-- SHALLOW (one-operation, fully-PINNED, abstract-operand) ≋ fact that lands. The
-- deep tree never enters an ≋ endpoint. `eᵢ` mirrors C's grouping, so `encode eᵢ`
-- reduces to `Cᴹfᵢ` and the direct eval to `C.fᵢ x y z` (both refl); `γᵢ = homAgree eᵢ`.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncodingLiteral where

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

open import Substrate.Algebra.Q.JacobianEvalNormalize
  using (powℚ; evalBridge₁; evalBridge₂; evalBridge₃)
import Substrate.Algebra.Q.JacobianEvalNormalize as β
open import Substrate.Algebra.Q.JacobianEncodingNormalize using (Cᴹf₁; Cᴹf₂; Cᴹf₃)
import Substrate.Algebra.Q.JacobianCollision as C

-- The free-Expr syntax + encoding (the DEFINITION module; def/proof separation).
open import Substrate.Algebra.Q.JacobianExpr
  using (Expr; eX; eY; eZ; eK; _⊕E_; _⊗E_; _⊖E_; encode; e₁; e₂; e₃)

-- A loose-fixity synonym for the target equality, ONLY so `a *ℚ b ≋ c *ℚ d`
-- parses (both `_*ℚ_` and `_≈ℚ_` sit at level 20). This is a RELATION
-- (codomain Set), not a ℚ-carrier operator — it introduces no arithmetic op.
infix 0 _≋_
_≋_ : ℚ → ℚ → Set
_≋_ = _≈ℚ_

module _ (x y z : ℚ) where

  -- β's evaluator, threaded at this point (definitionally: E (t ∷ p) = eT t +ℚ E p).
  private
    E : MPoly → ℚ
    E  = β.evalℚ x y z
    eT : Term → ℚ
    eT = β.evalT x y z
    mv : Mono → ℚ
    mv = β.monoval x y z

  ----------------------------------------------------------------------
  -- 0. Generic ℚ rearrangements (pinned; no reasoning combinator).
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
  -- 1. `powℚ` and ℤ→ℚ bridge lemmas (pinned).
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

  ----------------------------------------------------------------------
  -- 2. monoval / generator VALUES (pinned).
  ----------------------------------------------------------------------

  monoval-100 : mv (mono 1 0 0) ≋ x
  monoval-100 =
    ≈ℚ-trans {(x *ℚ 1ℚ) *ℚ (1ℚ *ℚ 1ℚ)} {x *ℚ 1ℚ} {x}
      (*ℚ-cong {x *ℚ 1ℚ} {x} {1ℚ *ℚ 1ℚ} {1ℚ} (*ℚ-identityʳ x) (*ℚ-identityˡ 1ℚ))
      (*ℚ-identityʳ x)

  monoval-010 : mv (mono 0 1 0) ≋ y
  monoval-010 =
    ≈ℚ-trans {1ℚ *ℚ ((y *ℚ 1ℚ) *ℚ 1ℚ)} {(y *ℚ 1ℚ) *ℚ 1ℚ} {y}
      (*ℚ-identityˡ ((y *ℚ 1ℚ) *ℚ 1ℚ))
      (≈ℚ-trans {(y *ℚ 1ℚ) *ℚ 1ℚ} {y *ℚ 1ℚ} {y}
        (*ℚ-identityʳ (y *ℚ 1ℚ)) (*ℚ-identityʳ y))

  monoval-001 : mv (mono 0 0 1) ≋ z
  monoval-001 =
    ≈ℚ-trans {1ℚ *ℚ (1ℚ *ℚ (z *ℚ 1ℚ))} {1ℚ *ℚ (z *ℚ 1ℚ)} {z}
      (*ℚ-identityˡ (1ℚ *ℚ (z *ℚ 1ℚ)))
      (≈ℚ-trans {1ℚ *ℚ (z *ℚ 1ℚ)} {z *ℚ 1ℚ} {z}
        (*ℚ-identityˡ (z *ℚ 1ℚ)) (*ℚ-identityʳ z))

  monoval-000 : mv (mono 0 0 0) ≋ 1ℚ
  monoval-000 =
    ≈ℚ-trans {1ℚ *ℚ (1ℚ *ℚ 1ℚ)} {1ℚ *ℚ 1ℚ} {1ℚ}
      (*ℚ-identityˡ (1ℚ *ℚ 1ℚ)) (*ℚ-identityˡ 1ℚ)

  evalℚ-single : (m : Mono) (k : ℤ) → E (term m k ∷ []) ≋ (ℤ→ℚ k) *ℚ (mv m)
  evalℚ-single m k = +ℚ-identityʳ ((ℤ→ℚ k) *ℚ mv m)

  gen-X : E R.X ≋ x
  gen-X = ≈ℚ-trans {E R.X} {1ℚ *ℚ (mv (mono 1 0 0))} {x}
            (evalℚ-single (mono 1 0 0) 1ℤ)
            (≈ℚ-trans {1ℚ *ℚ (mv (mono 1 0 0))} {mv (mono 1 0 0)} {x}
              (*ℚ-identityˡ (mv (mono 1 0 0))) monoval-100)

  gen-Y : E R.Y ≋ y
  gen-Y = ≈ℚ-trans {E R.Y} {1ℚ *ℚ (mv (mono 0 1 0))} {y}
            (evalℚ-single (mono 0 1 0) 1ℤ)
            (≈ℚ-trans {1ℚ *ℚ (mv (mono 0 1 0))} {mv (mono 0 1 0)} {y}
              (*ℚ-identityˡ (mv (mono 0 1 0))) monoval-010)

  gen-Z : E R.Z₁ ≋ z
  gen-Z = ≈ℚ-trans {E R.Z₁} {1ℚ *ℚ (mv (mono 0 0 1))} {z}
            (evalℚ-single (mono 0 0 1) 1ℤ)
            (≈ℚ-trans {1ℚ *ℚ (mv (mono 0 0 1))} {mv (mono 0 0 1)} {z}
              (*ℚ-identityˡ (mv (mono 0 0 1))) monoval-001)

  gen-kP : (k : ℤ) → E (R.kP k) ≋ ℤ→ℚ k
  gen-kP k = ≈ℚ-trans {E (R.kP k)} {(ℤ→ℚ k) *ℚ (mv (mono 0 0 0))} {ℤ→ℚ k}
               (evalℚ-single (mono 0 0 0) k)
               (≈ℚ-trans {(ℤ→ℚ k) *ℚ (mv (mono 0 0 0))} {(ℤ→ℚ k) *ℚ 1ℚ} {ℤ→ℚ k}
                 (*ℚ-cong {ℤ→ℚ k} {ℤ→ℚ k} {mv (mono 0 0 0)} {1ℚ}
                          (≈ℚ-refl (ℤ→ℚ k)) monoval-000)
                 (*ℚ-identityʳ (ℤ→ℚ k)))

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

  ----------------------------------------------------------------------
  -- 5. γ (evalℚ Cᴹfᵢ ≋ C.fᵢ) BY UNIQUENESS, then the LITERAL close.
  --    `encode eᵢ` reduces to `Cᴹfᵢ` and `evalDirect eᵢ` to `C.fᵢ x y z`,
  --    both by refl, so `γᵢ = homAgree eᵢ`.
  ----------------------------------------------------------------------

  γ₁ : E Cᴹf₁ ≋ C.f₁ x y z
  γ₁ = homAgree e₁
  γ₂ : E Cᴹf₂ ≋ C.f₂ x y z
  γ₂ = homAgree e₂
  γ₃ : E Cᴹf₃ ≋ C.f₃ x y z
  γ₃ = homAgree e₃

  literal₁ : E R.f₁ ≋ C.f₁ x y z
  literal₁ = ≈ℚ-trans {E R.f₁} {E Cᴹf₁} {C.f₁ x y z} (evalBridge₁ x y z) γ₁
  literal₂ : E R.f₂ ≋ C.f₂ x y z
  literal₂ = ≈ℚ-trans {E R.f₂} {E Cᴹf₂} {C.f₂ x y z} (evalBridge₂ x y z) γ₂
  literal₃ : E R.f₃ ≋ C.f₃ x y z
  literal₃ = ≈ℚ-trans {E R.f₃} {E Cᴹf₃} {C.f₃ x y z} (evalBridge₃ x y z) γ₃
