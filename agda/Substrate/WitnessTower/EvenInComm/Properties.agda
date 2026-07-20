------------------------------------------------------------------------
-- Substrate.WitnessTower.EvenInComm.Properties
--
-- ◆ip-cap-reverse — the DEEP containment Aₙ ⊆ [Sₙ,Sₙ]: every EVEN Coxeter
-- derivation is a product of commutators, as a TERM:
--
--   even→InComm : (g : CoxGen τ) → signW g ≡ false → InComm τ
--
-- Together with CommutatorSubgroup.InComm→even (the easy [Sₙ,Sₙ] ⊆ Aₙ),
-- this closes [Sₙ,Sₙ] = Aₙ.
--
-- The single genuinely-new combinatorial content is `conj-gtransp`: a
-- general transposition conjugated by any permutation is the transposition
-- of the images. From it the disjoint-double-transposition case is ONE
-- commutator; the adjacent case is two commutators via the braid; the
-- identity case is sadj-involution. Everything downstream (word→perm
-- bridge, the trichotomy, the fold) replays existing apply-*/compose-* idioms.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.EvenInComm.Properties where

open import Substrate.WitnessTower.EvenInComm
  using (Tri; tri-eq; tri-adj; tri-adj'; tri-sep; tri-sep';
         AllInj1; ai-nil; ai-cons)

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin; _≟_)
  renaming (zero to fzero; suc to fsuc; suc-injective to fsuc-inj)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂; subst)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Vec using (lookup; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.SnGroup
  using (apply; apply-compose; apply-id; apply-injective;
         compose-is-perm; compose-id-left; compose-id-right)
open import Substrate.WitnessTower.CyclicGrounding using (compose-assoc)
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym using (inv-unique)
open import Substrate.WitnessTower.SignCommutator
  using (inverse; inverse-right; commutator)
open import Substrate.WitnessTower.CommutatorSubgroup using (InComm; ic-id; ic-comm; ic-∘)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral
  using (sadj; inj1; CoxGen; cox-id; cox-s; cox-∘)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral.Properties
  using (coxeter-complete)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
  using (tp; sadj-realizes; sadj-is-perm; sign; signW; sign-wd; inj1≢suc)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid
  using (Sep; sep0; sepS; cox-braid)
open import Substrate.WitnessTower.SignAbelianization using (sadj-involution)
open import Substrate.WitnessTower.SignGrade2Generated using (flatten; even→grade2)
open import Substrate.Algebra.ParityKernel.Universal using (Gr2Gen; g2-nil; g2-pair)
open import Substrate.Foundation.Bool using (Bool; false)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)

------------------------------------------------------------------------
-- STEP 0.  An adjacent transposition is its own inverse.
------------------------------------------------------------------------

inverse-sadj : {n : ℕ} (j : Fin n) →
               inverse (sadj n j) (sadj-is-perm n j) ≡ sadj n j
inverse-sadj {n} j =
  inv-unique (sadj n j) (inverse (sadj n j) (sadj-is-perm n j)) (sadj n j)
             (inverse-right (sadj n j) (sadj-is-perm n j))
             (sadj-involution j)

------------------------------------------------------------------------
-- 1.  swapFin — a general transposition on Fin via decidable equality,
--     with its three defining "value" lemmas (variables never reduce the
--     ≟-dispatch, so these are what we rewrite with).
------------------------------------------------------------------------

swapFin : {n : ℕ} (a b x : Fin n) → Fin n
swapFin a b x with x ≟ a
... | yes _ = b
... | no  _ with x ≟ b
...   | yes _ = a
...   | no  _ = x

swapFin-here : {n : ℕ} (a b : Fin n) → swapFin a b a ≡ b
swapFin-here a b with a ≟ a
... | yes _ = refl
... | no ¬p = ⊥-elim (¬p refl)

swapFin-there : {n : ℕ} (a b : Fin n) → ¬ (b ≡ a) → swapFin a b b ≡ a
swapFin-there a b b≢a with b ≟ a
... | yes p = ⊥-elim (b≢a p)
... | no  _ with b ≟ b
...   | yes _ = refl
...   | no ¬q = ⊥-elim (¬q refl)

swapFin-else : {n : ℕ} (a b x : Fin n) → ¬ (x ≡ a) → ¬ (x ≡ b) → swapFin a b x ≡ x
swapFin-else a b x x≢a x≢b with x ≟ a
... | yes p = ⊥-elim (x≢a p)
... | no  _ with x ≟ b
...   | yes q = ⊥-elim (x≢b q)
...   | no  _ = refl

swapFin-at-b : {n : ℕ} (a b : Fin n) → swapFin a b b ≡ a
swapFin-at-b a b with b ≟ a
... | yes q = q
... | no ¬q with b ≟ b
...   | yes _ = refl
...   | no ¬r = ⊥-elim (¬r refl)

swapFin-invol : {n : ℕ} (a b x : Fin n) → swapFin a b (swapFin a b x) ≡ x
swapFin-invol a b x with x ≟ a
... | yes p = trans (swapFin-at-b a b) (sym p)
... | no ¬p with x ≟ b
...   | yes q = trans (swapFin-here a b) (sym q)
...   | no ¬q = swapFin-else a b x ¬p ¬q

swapFin-injective : {n : ℕ} (a b : Fin n) {i j : Fin n} →
                    swapFin a b i ≡ swapFin a b j → i ≡ j
swapFin-injective a b {i} {j} e =
  trans (sym (swapFin-invol a b i))
        (trans (cong (swapFin a b) e) (swapFin-invol a b j))

------------------------------------------------------------------------
-- 2.  gtransp — the general transposition as a permutation, its action,
--     that it is a permutation, its involution, and its self-inverse.
------------------------------------------------------------------------

gtransp : {n : ℕ} (a b : Fin n) → Perm n
gtransp a b = tabulate (swapFin a b)

apply-gtransp : {n : ℕ} (a b i : Fin n) → apply (gtransp a b) i ≡ swapFin a b i
apply-gtransp a b i = lookup∘tabulate (swapFin a b) i

gtransp-is-perm : {n : ℕ} (a b : Fin n) → IsPerm (gtransp a b)
gtransp-is-perm a b i j e =
  swapFin-injective a b
    (trans (sym (apply-gtransp a b i)) (trans e (apply-gtransp a b j)))

gtransp-involution : {n : ℕ} (a b : Fin n) →
                     compose (gtransp a b) (gtransp a b) ≡ id-perm n
gtransp-involution a b = apply-injective (λ i →
  trans (apply-compose (gtransp a b) (gtransp a b) i)
        (trans (cong (apply (gtransp a b)) (apply-gtransp a b i))
               (trans (apply-gtransp a b (swapFin a b i))
                      (trans (swapFin-invol a b i) (sym (apply-id i))))))

inverse-gtransp : {n : ℕ} (a b : Fin n) →
                  inverse (gtransp a b) (gtransp-is-perm a b) ≡ gtransp a b
inverse-gtransp a b =
  inv-unique (gtransp a b) (inverse (gtransp a b) (gtransp-is-perm a b)) (gtransp a b)
             (inverse-right (gtransp a b) (gtransp-is-perm a b))
             (gtransp-involution a b)

------------------------------------------------------------------------
-- 3.  sadj IS the gtransp of its two positions: sadj n k = (inj1 k , suc k).
--     Bridge tp (structural) to swapFin (decidable) via a suc-recursion.
------------------------------------------------------------------------

swapFin-suc : {n : ℕ} (a b i : Fin n) →
              swapFin (fsuc a) (fsuc b) (fsuc i) ≡ fsuc (swapFin a b i)
swapFin-suc a b i with i ≟ a
... | yes _ = refl
... | no  _ with i ≟ b
...   | yes _ = refl
...   | no  _ = refl

tp-swapFin : {n : ℕ} (k : Fin n) (i : Fin (ℕ.suc n)) →
             tp k i ≡ swapFin (inj1 k) (fsuc k) i
tp-swapFin fzero fzero               = refl
tp-swapFin fzero (fsuc fzero)        = refl
tp-swapFin fzero (fsuc (fsuc i))     = refl
tp-swapFin (fsuc k) fzero            = refl
tp-swapFin (fsuc k) (fsuc i)         =
  trans (cong fsuc (tp-swapFin k i))
        (sym (swapFin-suc (inj1 k) (fsuc k) i))

sadj-is-gtransp : {n : ℕ} (k : Fin n) → sadj n k ≡ gtransp (inj1 k) (fsuc k)
sadj-is-gtransp {n} k = apply-injective (λ i →
  trans (sadj-realizes n k i)
        (trans (tp-swapFin k i)
               (sym (apply-gtransp (inj1 k) (fsuc k) i))))

------------------------------------------------------------------------
-- 4.  conj-gtransp — THE novel lemma: w · (a b) · w⁻¹ = (w a , w b).
------------------------------------------------------------------------

conj-gtransp : {n : ℕ} (w : Perm n) (pw : IsPerm w) (a b : Fin n) →
               compose w (compose (gtransp a b) (inverse w pw))
               ≡ gtransp (apply w a) (apply w b)
conj-gtransp {n} w pw a b = apply-injective step
  where
    iv = inverse w pw
    -- w undoes its own inverse pointwise.
    wy : (x : Fin n) → apply w (apply iv x) ≡ x
    wy x = trans (sym (apply-compose w iv x))
                 (trans (cong (λ z → apply z x) (inverse-right w pw)) (apply-id x))
    -- the pointwise heart, after stripping the two composes.
    core : (x : Fin n) → apply w (swapFin a b (apply iv x))
                        ≡ swapFin (apply w a) (apply w b) x
    core x with apply iv x ≟ a
    ... | yes p =
      sym (trans (cong (swapFin (apply w a) (apply w b)) x≡wa)
                 (swapFin-here (apply w a) (apply w b)))
      where
        x≡wa : x ≡ apply w a
        x≡wa = trans (sym (wy x)) (cong (apply w) p)
    ... | no ¬p with apply iv x ≟ b
    ...   | yes q =
      sym (trans (cong (swapFin (apply w a) (apply w b)) x≡wb)
                 (swapFin-at-b (apply w a) (apply w b)))
      where
        x≡wb : x ≡ apply w b
        x≡wb = trans (sym (wy x)) (cong (apply w) q)
    ...   | no ¬q =
      trans (wy x)
            (sym (swapFin-else (apply w a) (apply w b) x x≢wa x≢wb))
      where
        x≢wa : ¬ (x ≡ apply w a)
        x≢wa = λ e → ¬p (pw (apply iv x) a (trans (wy x) e))
        x≢wb : ¬ (x ≡ apply w b)
        x≢wb = λ e → ¬q (pw (apply iv x) b (trans (wy x) e))
    step : (x : Fin n) →
           apply (compose w (compose (gtransp a b) iv)) x
           ≡ apply (gtransp (apply w a) (apply w b)) x
    step x =
      trans (apply-compose w (compose (gtransp a b) iv) x)
            (trans (cong (apply w) (apply-compose (gtransp a b) iv x))
                   (trans (cong (apply w) (apply-gtransp a b (apply iv x)))
                          (trans (core x)
                                 (sym (apply-gtransp (apply w a) (apply w b) x)))))

------------------------------------------------------------------------
-- 5.  Structural distinctness lemmas (no arithmetic — induct on Fin/Sep).
------------------------------------------------------------------------

-- inj1≢suc reused from OrientationRigCatPermSign (same proposition).
suc≢inj1 : {n : ℕ} (j : Fin n) → ¬ (fsuc j ≡ inj1 j)
suc≢inj1 j = λ e → inj1≢suc j (sym e)

-- Sep i j (i below j by ≥2): inj1 i ≠ suc j (the two overlap positions miss).
sep→inj1≢suc : {m : ℕ} {i j : Fin m} → Sep i j → ¬ (inj1 i ≡ fsuc j)
sep→inj1≢suc (sep0 k) = λ ()
sep→inj1≢suc (sepS s) = λ e → sep→inj1≢suc s (fsuc-inj e)

-- Sep j i (j below i by ≥2): still inj1 i ≠ suc j (i above j).
sepr→inj1≢suc : {m : ℕ} {i j : Fin m} → Sep j i → ¬ (inj1 i ≡ fsuc j)
sepr→inj1≢suc (sep0 k) ()
sepr→inj1≢suc (sepS s) = λ e → sepr→inj1≢suc s (fsuc-inj e)

------------------------------------------------------------------------
-- 6.  STEP 2a — equal indices: sₖ² = id ∈ [Sₙ,Sₙ].
------------------------------------------------------------------------

pairInComm-eq : {m : ℕ} (i : Fin m) → InComm (compose (sadj m i) (sadj m i))
pairInComm-eq i = subst InComm (sym (sadj-involution i)) ic-id

------------------------------------------------------------------------
-- 7.  STEP 2b — adjacent (braid) generators: ab is TWO commutators.
--     Given a,b involutions with the braid a(ba)=b(ab): (ab)² = ba, so
--     commutator a b = (ab)² = ba and ab = (ba)² = (commutator a b)².
------------------------------------------------------------------------

adj-InComm : {N : ℕ} (a b : Perm N) (pa : IsPerm a) (pb : IsPerm b) →
             compose a a ≡ id-perm N → compose b b ≡ id-perm N →
             compose a (compose b a) ≡ compose b (compose a b) →
             InComm (compose a b)
adj-InComm {N} a b pa pb aa bb braid =
  subst InComm final-eq (ic-∘ (ic-comm a b pa pb) (ic-comm a b pa pb))
  where
    -- (xy)² = yx for involutions x,y with braid x(yx)=y(xy).
    prod-sq : (x y : Perm N) → compose x x ≡ id-perm N → compose y y ≡ id-perm N →
              compose x (compose y x) ≡ compose y (compose x y) →
              compose (compose x y) (compose x y) ≡ compose y x
    prod-sq x y xx yy br =
      trans (compose-assoc x y (compose x y))
            (trans (cong (compose x) (sym (compose-assoc y x y)))
                   (trans (sym (compose-assoc x (compose y x) y))
                          (trans (cong (λ z → compose z y) br)
                                 (trans (compose-assoc y (compose x y) y)
                                        (cong (compose y) xyy)))))
      where
        xyy : compose (compose x y) y ≡ x
        xyy = trans (compose-assoc x y y)
                    (trans (cong (compose x) yy) (compose-id-right x))
    -- commutator a b = a·b·a⁻¹·b⁻¹ = a·b·a·b = (ab)² (involutions).
    inv-a : inverse a pa ≡ a
    inv-a = inv-unique a (inverse a pa) a (inverse-right a pa) aa
    inv-b : inverse b pb ≡ b
    inv-b = inv-unique b (inverse b pb) b (inverse-right b pb) bb
    comm-sq : commutator a b pa pb ≡ compose (compose a b) (compose a b)
    comm-sq = cong (compose (compose a b)) (cong₂ compose inv-a inv-b)
    final-eq : compose (commutator a b pa pb) (commutator a b pa pb) ≡ compose a b
    final-eq =
      trans (cong₂ compose comm-sq comm-sq)
            (trans (cong₂ compose (prod-sq a b aa bb braid)
                                  (prod-sq a b aa bb braid))
                   (prod-sq b a bb aa (sym braid)))

------------------------------------------------------------------------
-- 8.  STEP 2c — disjoint transpositions: sᵢsⱼ = ONE commutator [sᵢ,w],
--     where w = (inj1 i inj1 j)(suc i suc j) conjugates sᵢ to sⱼ.
------------------------------------------------------------------------

disjoint-InComm : {m : ℕ} (i j : Fin m) →
                  ¬ (inj1 i ≡ fsuc j) → ¬ (fsuc j ≡ inj1 i) →
                  InComm (compose (sadj m i) (sadj m j))
disjoint-InComm {m} i j i≢j' j'≢i =
  subst InComm comm-eq (ic-comm s w ps pw)
  where
    g1 = gtransp (inj1 i) (inj1 j)
    g2 = gtransp (fsuc i) (fsuc j)
    w  = compose g1 g2
    pw : IsPerm w
    pw = compose-is-perm g1 g2 (gtransp-is-perm (inj1 i) (inj1 j))
                               (gtransp-is-perm (fsuc i) (fsuc j))
    s  = sadj m i
    ps : IsPerm s
    ps = sadj-is-perm m i
    -- w sends the two positions of sᵢ to the two positions of sⱼ.
    wai : apply w (inj1 i) ≡ inj1 j
    wai = trans (apply-compose g1 g2 (inj1 i))
                (trans (cong (apply g1) g2-on) g1-on)
      where
        g2-on : apply g2 (inj1 i) ≡ inj1 i
        g2-on = trans (apply-gtransp (fsuc i) (fsuc j) (inj1 i))
                      (swapFin-else (fsuc i) (fsuc j) (inj1 i) (inj1≢suc i) i≢j')
        g1-on : apply g1 (inj1 i) ≡ inj1 j
        g1-on = trans (apply-gtransp (inj1 i) (inj1 j) (inj1 i))
                      (swapFin-here (inj1 i) (inj1 j))
    wbi : apply w (fsuc i) ≡ fsuc j
    wbi = trans (apply-compose g1 g2 (fsuc i))
                (trans (cong (apply g1) g2b) g1b)
      where
        g2b : apply g2 (fsuc i) ≡ fsuc j
        g2b = trans (apply-gtransp (fsuc i) (fsuc j) (fsuc i))
                    (swapFin-here (fsuc i) (fsuc j))
        g1b : apply g1 (fsuc j) ≡ fsuc j
        g1b = trans (apply-gtransp (inj1 i) (inj1 j) (fsuc j))
                    (swapFin-else (inj1 i) (inj1 j) (fsuc j) j'≢i (suc≢inj1 j))
    comm-eq : commutator s w ps pw ≡ compose (sadj m i) (sadj m j)
    comm-eq =
      trans (cong (λ z → compose (compose s w) (compose z (inverse w pw)))
                  (inverse-sadj i))
            (trans (compose-assoc s w (compose s (inverse w pw)))
                   (cong (compose s) conj-result))
      where
        conj-result : compose w (compose s (inverse w pw)) ≡ sadj m j
        conj-result =
          trans (cong (λ z → compose w (compose z (inverse w pw))) (sadj-is-gtransp i))
                (trans (conj-gtransp w pw (inj1 i) (fsuc i))
                       (trans (cong₂ gtransp wai wbi) (sym (sadj-is-gtransp j))))

------------------------------------------------------------------------
-- 9.  STEP 3 — the trichotomy classifier for a pair of gen-indices.
------------------------------------------------------------------------

tri-suc : {m : ℕ} {i j : Fin m} → Tri i j → Tri (fsuc i) (fsuc j)
tri-suc (tri-eq e)   = tri-eq (cong fsuc e)
tri-suc (tri-adj k)  = tri-adj (fsuc k)
tri-suc (tri-adj' k) = tri-adj' (fsuc k)
tri-suc (tri-sep s)  = tri-sep (sepS s)
tri-suc (tri-sep' s) = tri-sep' (sepS s)

classify : {m : ℕ} (i j : Fin m) → Tri i j
classify fzero          fzero          = tri-eq refl
classify fzero          (fsuc fzero)   = tri-adj fzero
classify fzero          (fsuc (fsuc j)) = tri-sep (sep0 j)
classify (fsuc fzero)   fzero          = tri-adj' fzero
classify (fsuc (fsuc i)) fzero         = tri-sep' (sep0 i)
classify (fsuc i)       (fsuc j)       = tri-suc (classify i j)

------------------------------------------------------------------------
-- 10. STEP 2 assembled — a pair of generators is in the commutator subgroup.
------------------------------------------------------------------------

pairInComm : {m : ℕ} (i j : Fin m) → InComm (compose (sadj m i) (sadj m j))
pairInComm {m} i j with classify i j
... | tri-eq e   = subst (λ z → InComm (compose (sadj m i) (sadj m z))) e (pairInComm-eq i)
... | tri-adj k  =
  adj-InComm (sadj m (inj1 k)) (sadj m (fsuc k))
             (sadj-is-perm m (inj1 k)) (sadj-is-perm m (fsuc k))
             (sadj-involution (inj1 k)) (sadj-involution (fsuc k)) (cox-braid k)
... | tri-adj' k =
  adj-InComm (sadj m (fsuc k)) (sadj m (inj1 k))
             (sadj-is-perm m (fsuc k)) (sadj-is-perm m (inj1 k))
             (sadj-involution (fsuc k)) (sadj-involution (inj1 k)) (sym (cox-braid k))
... | tri-sep s  = disjoint-InComm i j (sep→inj1≢suc s) (λ e → sep→inj1≢suc s (sym e))
... | tri-sep' s = disjoint-InComm i j (sepr→inj1≢suc s) (λ e → sepr→inj1≢suc s (sym e))

------------------------------------------------------------------------
-- 11. STEP 1 — the word→perm bridge over inj1-only words.
--     A flattened Coxeter derivation is a word of `inj1 j` letters; its
--     interpretation `wordPermA` rebuilds the underlying permutation.
------------------------------------------------------------------------

wordPermA : {n : ℕ} {w : Word (Fin n)} → AllInj1 w → Perm n
wordPermA {n} ai-nil          = id-perm n
wordPermA (ai-cons {m} j rest) = compose (sadj m j) (wordPermA rest)

AllInj1-++ : {n : ℕ} {a b : Word (Fin n)} → AllInj1 a → AllInj1 b → AllInj1 (a ++ b)
AllInj1-++ ai-nil          pb = pb
AllInj1-++ (ai-cons j pa) pb = ai-cons j (AllInj1-++ pa pb)

wordPermA-++ : {n : ℕ} {a b : Word (Fin n)} (pa : AllInj1 a) (pb : AllInj1 b) →
               wordPermA (AllInj1-++ pa pb) ≡ compose (wordPermA pa) (wordPermA pb)
wordPermA-++ ai-nil          pb = sym (compose-id-left (wordPermA pb))
wordPermA-++ (ai-cons {m} j pa) pb =
  trans (cong (compose (sadj m j)) (wordPermA-++ pa pb))
        (sym (compose-assoc (sadj m j) (wordPermA pa) (wordPermA pb)))

flatten-allInj1 : {n : ℕ} {τ : Perm n} (g : CoxGen τ) → AllInj1 (flatten g)
flatten-allInj1 cox-id      = ai-nil
flatten-allInj1 (cox-s j)   = ai-cons j ai-nil
flatten-allInj1 (cox-∘ g h) = AllInj1-++ (flatten-allInj1 g) (flatten-allInj1 h)

flatten-builds : {n : ℕ} {τ : Perm n} (g : CoxGen τ) → wordPermA (flatten-allInj1 g) ≡ τ
flatten-builds cox-id      = refl
flatten-builds (cox-s j)   = compose-id-right (sadj _ j)
flatten-builds (cox-∘ g h) =
  trans (wordPermA-++ (flatten-allInj1 g) (flatten-allInj1 h))
        (cong₂ compose (flatten-builds g) (flatten-builds h))

------------------------------------------------------------------------
-- 12. STEP 4 — the fold: an even (pair-decomposed) inj1-word is InComm.
------------------------------------------------------------------------

foldInComm : {n : ℕ} {w : Word (Fin n)} (ai : AllInj1 w) → Gr2Gen w → InComm (wordPermA ai)
foldInComm ai-nil                     g2-nil               = ic-id
foldInComm (ai-cons i ai-nil)         ()
foldInComm (ai-cons {m} i (ai-cons j ai-rest)) (g2-pair _ _ gr-rest) =
  subst InComm (compose-assoc (sadj m i) (sadj m j) (wordPermA ai-rest))
        (ic-∘ (pairInComm i j) (foldInComm ai-rest gr-rest))

------------------------------------------------------------------------
-- 13. Aₙ ⊆ [Sₙ,Sₙ] — every even Coxeter derivation is a product of
--     commutators, and (perm-level) every even permutation is.
------------------------------------------------------------------------

even→InComm : {n : ℕ} {τ : Perm n} (g : CoxGen τ) → signW g ≡ false → InComm τ
even→InComm g e =
  subst InComm (flatten-builds g) (foldInComm (flatten-allInj1 g) (even→grade2 g e))

even→InComm-perm : {n : ℕ} (σ : Perm n) (pf : IsPerm σ) → sign σ ≡ false → InComm σ
even→InComm-perm σ pf e =
  even→InComm (coxeter-complete σ pf)
              (trans (sym (sign-wd (coxeter-complete σ pf))) e)
