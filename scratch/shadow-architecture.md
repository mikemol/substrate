---
title: Shadow Architecture — Multi-Language Export
date: 2026-05-20
source-skill: shadow-engineer
target-languages: [Lojban, Toki Pona, Kēlen]
charter: realizability (constructible / reachable / observable / coverable)
revisions: increments 1, 2, 3, 5, 9 folded with fibration enrichments
unchanged: increments 4, 6, 7, 8, 10
---

# Shadow Architecture — Multi-Language Export

## Orientation

This document is a complete rendering of the `shadow-engineer` skill into three constructed languages — Lojban, Toki Pona, and Kēlen — across ten incremental sections. Each section presents an English skeleton, followed by the three language renderings, followed by charter notes tracking what survives, compresses, or transforms under translation.

The work is governed throughout by the realizability principle:

> If a distinction is real, it must be constructible; if constructible, it must be behaviorally reachable; if reachable, it must be observable; if observable, it must be coverable; if not, it is not a valid runtime distinction.

Each rendering preserves this four-gate test as faithfully as the target language permits. Where a gate degrades under translation, the charter notes flag the degradation and name what is lost.

## Methodological notes

**On the three languages.** Three deliberately different grammars stress-test what is structural and what is merely lexical in the architecture:

- **Lojban** is a constructed logical language with predicate-logic-aligned grammar. It carries technical distinctions with minimal compression and natively expresses XOR (`vlina`), set membership (`cmima`), perpendicularity (`sraji`), and S₃-permutation structure. Where the source uses mathematical vocabulary, Lojban reproduces it almost directly.

- **Toki Pona** is a minimalist language with ~120 words. It has no native technical vocabulary at all. Every distinction in the source must be carried by metaphor: `pimeja` (dark) carries "shadow"; `ijo pali` (made thing) carries "artefact"; `ma Pano` (Pano-place) carries "Fano plane"; `nasin sin` (other-way) carries "normal vector." The compression sharpens which structural facts are load-bearing.

- **Kēlen** is a verbless language built by Sylvia Sotomayor on four relationals: `la` (equational identity), `ñi` (eventive change), `pa` (intrinsic possession), `se` (perceptual/communicational). The architecture's distinction between *what a signature has* (`pa`) and *what a registration does* (`ñi`) maps naturally onto Kēlen's grammar. Many Kēlen roots used below are best-effort extensions rather than canonical lexicon; the structure of the renderings is the load-bearing element.

**On the fibration audit.** After ten increments were drafted, a pairwise audit checked whether later increments introduced structural content that retroactively belonged at earlier ones. The audit surfaced substantive enrichments to Increments 1, 2, 3, 5, and 9. These have been folded into their respective revised forms. Increments 4, 6, 7, 8, and 10 are presented unchanged from their original drafting.

**On reading order.** The increments build sequentially: structure first (1–3), behavior next (4–5), constraint (6), symmetry (7), diagnostic (8–9), continuity (10). A reader new to the material can read in order. A reader familiar with the source skill can sample increments by interest; the cross-references identify dependencies.

---

## Increment 1 — The frame, three axes, and their dual lines

**English skeleton.** One skill subsumes four prior moves (`decomposable-by-entailment`, `snap-to-grid`, `regroup-from-shadows`, `mediation-guard`). It has three axes; each axis has a dual line in the Fano plane (the line consisting of exactly those signatures that *don't touch* that axis). The three axes form one S₃-orbit — operationally distinct but structurally interchangeable. The seven non-zero subsets of {e₁, e₂, e₃} are the seven axis-signatures.

```
axis   type / content        direction              dual line
─────  ───────────────────   ────────────────────   ─────────────────────────────────────────────
e₁     goal ↔ shadows        lift ⊣ contract        L₃ = {010, 001, 011}  — signatures not on e₁
e₂     shadows ↔ artefact    symmetric lens         L₂ = {100, 001, 101}  — signatures not on e₂
e₃     goal ↔ artefact       mediation-guard        L₁ = {100, 010, 110}  — signatures not on e₃
                              (negative axis)        — most negative axis dual to most positive line:
                                                      L₁ is positive-closure; e₃ is what L₁'s moves
                                                      explicitly do not touch. The duality states
                                                      the mediation principle directly.

S₃-orbit:  {e₁, e₂, e₃} is one orbit — no axis is structurally distinguished.
           "First axis" is an operational choice, not a structural fact.
```

The seven non-zero subsets of these axes are the seven axis-signatures (Increment 2).

### Lojban

```
.i la cabna stuzi cu girzu lo vo cnano stuzi —
   la .dekompozEbol., la .snap.tu.grid., la .reGRUP., .e la .mediEcion.gard.
.i lo cabna stuzi cu se rajra ci da poi se sraji pa linji:

  pamoi rajra  (e₁):  terkri  jo'u  ctino
   — galfi-galtu  .a  galfi-cmalu;  simxu nunfonxa
   — sraji linji L₃ = {010, 001, 011}  (na cmima e₁)

  remoi rajra  (e₂):  ctino  jo'u  selzbasu
   — pa lenjo simxu
   — sraji linji L₂ = {100, 001, 101}  (na cmima e₂)

  cimoi rajra  (e₃):  terkri  jo'u  selzbasu
   — na'e zifre;  lo kajde co rivbi
   — sraji linji L₁ = {100, 010, 110}  (na cmima e₃)
   — lo rai na'e zifre rajra cu se sraji lo rai prane linji:
     L₁ du lo positive-closure;  e₃ cu lo se rivbi pe L₁ —
     re snuti cu cusku lo mediation principle dunli

.i ci rajra cu pa S₃-sruri po'o —  no rajra cu na'e binxo.
   "pamoi rajra" cu prane cuxna,  na prane stuzi.

.i lo'i ze klesi pe lo nu zukte cu se cmima cmici lo'i ci rajra.
```

*Notes.* `rajra` = axis, `terkri` = purpose/goal, `ctino` = shadow, `selzbasu` = made-thing, `lenjo` = lens, `kajde` = guard. The adjunction renders as `galfi-galtu .a galfi-cmalu` (modify-up or modify-down) with mutual exchange. Lojban preserves the categorical structure cleanly; "adjunction" is rendered by its operational signature rather than borrowed.

### Toki Pona

```
nasin pi pali pimeja li wan.  ona li jo e nasin pi pali pi tenpo pini tu wan tu:
   "open e kulupu",  "tawa lon poki",  "kama wan tan pimeja",  awen pi nasin tu wan.

nasin pi pali pimeja li jo e nasin tu wan, en linja sin pi ona:

  nasin nanpa wan  (e₁):  wile  en  pimeja
    — tawa sewi anu tawa anpa;  tu li wan
    — linja nasin sin: L₃ = {010, 001, 011}  (linja pi pali pi e₁ ala)

  nasin nanpa tu  (e₂):  pimeja  en  ijo pali
    — sama ilo lukin;  wan taso
    — linja nasin sin: L₂ = {100, 001, 101}  (linja pi pali pi e₂ ala)

  nasin nanpa tu wan  (e₃):  wile  en  ijo pali
    — ni li ike;  awen li lon
    — linja nasin sin: L₁ = {100, 010, 110}  (linja pi pali pi e₃ ala)
    — nasin pi ike suli li sama nasin sin pi linja pi pona suli:
      L₁ li linja pi "wan tan tu";  e₃ li ijo L₁ li pali ala —
      tu pi nasin sin li toki e nasin pi awen sama.

ijo nasin tu wan li lon kulupu wan pi S₃ —  ijo wan li lon ala awen.
   "nasin nanpa wan" li wile pi jan,  li ijo pi nasin ala.

kulupu pi pali ali li lon nasin tu wan ni — luka tu kulupu.
```

*Notes.* `pimeja` (dark) carries "shadow"; `ijo pali` (made-thing) carries "artefact"; `wile` (want) carries "goal"; `awen` (guard/preserve) carries the mediation-guard. The adjunction collapses to `tu li wan` ("two are one"); the fact of two directions survives, the categorical status does not. The dual-line claim — `linja pi pali pi e_i ala` — "the line of moves not on axis e_i" — captures the perpendicularity reading.

### Kēlen

```
La japōrasāke jamēñēna ñi makke jakēñahēi —
ñe ñi jakēña anhū ja japōraþwāra anhū:
   decomp,  snap,  regroup,  jakāwa.

La japōrasāke pa anjakīñe anhū;  pa jakīñe anhū jaorra anwāñ:

  anjakīñe ja ankāe  (e₁):  pa jathēña ī jamēña
    — ñi jōraþ;  ñi mōraþ;  la mān ān ma jakīñe
    — pa jaorra anlū:  L₃ = {010, 001, 011}  (na pa-jamēhū-jōkīña ñe e₁)

  anjakīñe ja anrūo  (e₂):  pa jamēña ī jasēla
    — la jajēña ñēim
    — pa jaorra anlū:  L₂ = {100, 001, 101}  (na pa-jamēhū-jōkīña ñe e₂)

  anjakīñe ja antēn  (e₃):  pa jathēña ī jasēla
    — pa makawēña;  pa jakāwa
    — pa jaorra anlū:  L₁ = {100, 010, 110}  (na pa-jamēhū-jōkīña ñe e₃)
    — la jakīñe ja-makawīña-jamāhe ñi jaorra ñe jamē ja-anwāñ-jamāhe:
      L₁ pa anwāñ-anpōrra;  e₃ pa na-mōrra ñe L₁ —
      pa jaorra ja-tū anhū ñi tōrre ñe makke-jōkīña.

La jakīñe anhū jasūma anpā ñe S₃ —  na pa jakīñe ān ja-anrārra.
   "jakīñe ja-anpā" pa mōrra-cnīna;  na pa jakīñe-jōña.

Pa jaciēn anhū ñe jakīñe anhū jasūma —  pa jaciēn anhū.
```

*Notes.* The three axes resolve to `pa` (each axis intrinsically *has* a pair of endpoints). The adjunction shows up as paired `ñi` events on the same `pa`-structure. The guard becomes `pa makawēña` (it has negation) reinforced by `pa jakāwa` (it has the guard) — the negative axis is positive content, anticipating L₆ (guard-reconstitution). The duality renders as a `pa jaorra` (it has [as] normal) relation between each axis and its dual line. Many roots above are best-effort under Kēlen morphology rather than canonical.

### Charter notes

The constructibility of the three-axis distinction survives in all three. Reachability survives — each rendering names both directions of e₁ explicitly. Observability degrades most in Toki Pona, where "lens" and "adjunction" both collapse to metaphors; the distinction remains inferable but no longer directly tagged. Coverability — the claim that *every* substantive move sits on one of seven signatures — survives in Lojban and Kēlen as a counted set, and in Toki Pona as `luka tu kulupu` (seven groups). The negative axis (e₃) is the most semantically dense piece; Kēlen handles it most naturally because `pa makawēña` ("it has negation") is a first-class relational fact, not a derived predicate.

The dual-line enrichment makes a structural fact visible at first introduction: each axis is the complement of *moves that don't involve it*. The most negative axis (e₃) is dual to the most positive line (L₁, positive-closure) — the duality directly states the mediation principle.


---

## Increment 2 — Seven axis-signatures with full structural identity

**English skeleton.** Each of the seven points has six structural facts: bit-pattern (the address), name, operational content, S₃-weight, three lines through it with addition relations, dual line (which line has this point as its normal), and ★ self-referential status if any. Pure-axis points additionally tag a mode-entry. Classification is mechanical from the read/write set; the signature is the full set of axes the move's effect touches.

```
sig  name              op. content                  weight  lines: additions                                  dual  mode-entry
───  ────────────      ─────────────────────────    ──────  ────────────────────────────────────────────────  ────  ─────────
100  pure-GS           decomp/snap; goal–shadows    1       L₁:+010→110  L₂:+001→101  L₄:+011→111             L₃    decomp (lift)
010  pure-SA           regroup; shadows–artefact    1       L₁:+100→110  L₃:+001→011  L₅:+101→111             L₂    regroup (lens)
001  pure-G            guard event;                 1       L₂:+100→101  L₃:+010→011  L₆:+110→111             L₁    guard (reject-redirect)
                       direct goal–artefact                  — star(001) = {L₂,L₃,L₆} = guard's full territory
110  mediated-         goal→shadows→artefact         2       L₁:↑100+010  L₆:+001→111  L₇:↑101,011             L₆ ★  —
     composite          (or reverse)                          — ★ L₆'s normal is 110: redirect target =
                                                                perpendicular to reconstitution line
101  guard-cleared-GS  GS audited against e₃        2       L₂:↑100+001  L₅:+010→111  L₇:↑110,011             L₅    —
011  guard-cleared-SA  SA audited against e₃        2       L₃:↑010+001  L₄:+100→111  L₇:↑110,101             L₄    —
111  triadic-full      all three axes participate   3       L₄:100+011   L₅:010+101   L₆:001+110              L₇ ★  —
                                                            — ★ L₇'s normal is 111; non-incident S₃-fixed pair
```

(`+X→Y` reads "this point + X = Y on that line"; `↑a+b` reads "this point decomposes upward into a+b on that line"; `↑a,b` reads "this point sits with a and b on a no-pure-axis line.")

Classification is from what the move reads and what it writes; not from interpretive judgement.

### Lojban

```
.i lo ze klesi (cmene · zukte · ka'i · linji · sraji · tadji ralju):

100  pure-GS    decomp/snap pe terkri-ctino     ka'i 1
     {L₁:+010→110, L₂:+001→101, L₄:+011→111}   sraji L₃   tadji: decomp (galtu)

010  pure-SA    regroup pe ctino-selzbasu       ka'i 1
     {L₁:+100→110, L₃:+001→011, L₅:+101→111}   sraji L₂   tadji: regroup (lenjo)

001  pure-G     kajde nuncfari                  ka'i 1
     {L₂:+100→101, L₃:+010→011, L₆:+110→111}   sraji L₁   tadji: kajde (rivbi+rejgau)
     — cuvska(001) = {L₂,L₃,L₆} = lo kajde naxle co prane

110  mediated-composite                         ka'i 2
     {L₁:↑100+010, L₆:+001→111, L₇:↑101,011}   sraji L₆  ★
     — ★ sraji be L₆ du 110:  
        rejgau te zukte du lo sraji be lo rikygau ke linji

101  guard-cleared-GS                           ka'i 2
     {L₂:↑100+001, L₅:+010→111, L₇:↑110,011}   sraji L₅

011  guard-cleared-SA                           ka'i 2
     {L₃:↑010+001, L₄:+100→111, L₇:↑110,101}   sraji L₄

111  triadic-full                               ka'i 3
     {L₄:100+011, L₅:010+101, L₆:001+110}      sraji L₇  ★
     — ★ S₃-mintu rai;  L₇ co sraji du 111 ku'i 111 na cmima L₇ —
        re mintu na cmima simxu

.i lo klesi cu se jdice fi lo selplekata ce'o lo selciska —
   na'e fi lo se jinvi.  ro nu zukte cu se klesi pa po'o.
```

### Toki Pona

```
kulupu pi pali luka tu  (nimi · pali · ali · linja · nasin sin · tadji):

100  pimeja-taso (pi nasin nanpa wan)           ali 1
     {L₁:+010→110, L₂:+001→101, L₄:+011→111}   nasin sin: L₃   tadji: decomp (sewi)

010  ijo-taso (pi nasin nanpa tu)               ali 1
     {L₁:+100→110, L₃:+001→011, L₅:+101→111}   nasin sin: L₂   tadji: regroup (ilo lukin)

001  awen-taso (pi nasin nanpa tu wan)          ali 1
     {L₂:+100→101, L₃:+010→011, L₆:+110→111}   nasin sin: L₁   tadji: awen (sisti+pana sin)
     — linja tu wan pi "001" li ma ali pi awen

110  tu-nasin-wan                               ali 2
     {L₁:↑100+010, L₆:+001→111, L₇:↑101,011}   nasin sin: L₆  ★
     — ★ nasin sin pi L₆ li sama 110:  
        ma pi tawa sin = nasin sin pi linja pi "ike-kama-pona"

101  pimeja-wile, awen lukin                    ali 2
     {L₂:↑100+001, L₅:+010→111, L₇:↑110,011}   nasin sin: L₅

011  pimeja-ijo, awen lukin                     ali 2
     {L₃:↑010+001, L₄:+100→111, L₇:↑110,101}   nasin sin: L₄

111  ali-pali                                   ali 3
     {L₄:100+011, L₅:010+101, L₆:001+110}      nasin sin: L₇  ★
     — ★ S₃ ante ala lon ona;  L₇ pi nasin sin sama 111
       taso 111 li lon ala L₇ — tu sama, taso lon ala

pali ali li kama lon kulupu wan kepeken ni:
   ijo seme la sina lukin?  ijo seme la sina sitelen?
   nasin pi pilin sina li ike — kulupu li tan lukin en sitelen taso.
```

### Kēlen

```
Pa jaciēn anhū (jōña · jamāhe-zukte · anpā · jamēhū · jaorra · jasūma):

100  pure-GS    decomp/snap ñe jathēña-jamēña       anpā 1
     {L₁:+010→110, L₂:+001→101, L₄:+011→111}       jaorra: L₃   jasūma: decomp (jōraþ)

010  pure-SA    regroup ñe jamēña-jasēla            anpā 1
     {L₁:+100→110, L₃:+001→011, L₅:+101→111}       jaorra: L₂   jasūma: regroup (jajēña-ñēim)

001  pure-G     jakāwa-jamāhe                       anpā 1
     {L₂:+100→101, L₃:+010→011, L₆:+110→111}       jaorra: L₁   jasūma: jakāwa
     — pa jamēhū anhū ñe 001 anlā ñēim ñe jakāwa-anwēn-jamēhū

110  mediated-composite                             anpā 2
     {L₁:↑100+010, L₆:+001→111, L₇:↑101,011}       jaorra: L₆  ★
     — ★ pa jaorra ja L₆ ñēim 110:  
        pa jaciēn-cnīna-anlū ñēim pa jaorra ja jamē-makawīña-anwāñ

101  guard-cleared-GS                               anpā 2
     {L₂:↑100+001, L₅:+010→111, L₇:↑110,011}       jaorra: L₅

011  guard-cleared-SA                               anpā 2
     {L₃:↑010+001, L₄:+100→111, L₇:↑110,101}       jaorra: L₄

111  triadic-full                                   anpā 3
     {L₄:100+011, L₅:010+101, L₆:001+110}          jaorra: L₇  ★
     — ★ S₃-anrārra ān;  pa jaorra ja L₇ ñēim 111
        ka 111 na pa-jamē-L₇ — pa ñēim-jōkīña, na pa anwāñ-jamē

Pa jaciēn ān ñi mōrra ān;  pa jaciēn ñi sēña ī ñi jōña ān —
na pa jaciēn ñi tōrre ñe makke.
```

### Charter notes

The seven-ness is preserved as a counted set in all three. The bit-structure of the signatures survives most directly in Toki Pona (`wan/ala/ala` in earlier drafts; here compressed to the names) and most awkwardly in Kēlen (named-axis-conjunction). The mechanical-from-read/write-set claim survives in all three but with different emphasis: Lojban as logical disjunction (`na'e fi lo se jinvi`), Toki Pona as a pair of questions (look/write), Kēlen as a negation of mental origination — three different ways of marking that the signature is observable from outside and not from the agent's self-report.

The 001 / pure-G case is the most semantically loaded: it is both a state *and* a redirect. All three preserve the *redirect-is-content* claim — the guard event is not absence but positive structure — which is what makes L₆ (guard-reconstitution) work in Increment 3.

The two ★ self-referential incidences (L₆ ↔ 110, L₇ ↔ 111) are visible from the point side here; they were also visible from the line side in Increment 3. The duality is now symmetric across both renderings.

---

## Increment 3 — Fano structure: lines, points, incidences, mode-ownership, S₃-orbits

**English skeleton.** Seven points, seven lines, three points per line, three lines per point. Every pair of points lies on exactly one line (the S(2,3,7) Steiner property). The plane is self-dual: each line has a normal-vector which is itself one of the seven points. Two self-referential incidences carry the architectural weight:

- L₆'s normal is **110 (mediated-composite)** — the line that reconstitutes the forbidden direct axis has the mediated composite as its perpendicular. The thing the axis prohibits is the thing whose orthogonal complement contains the reconstitution rule.
- L₇'s normal is **111 (triadic-full)** — the pure-composite diagonal (containing only weight-2 points, no pure axis) has the triadic-full as its normal. This is the only S₃-fixed line; 111 is the only S₃-fixed point; they are a fixed pair *not* incident with each other.

The other five normals form two S₃-orbits: {L₁→001, L₂→010, L₃→100} (the guard-coverage triad) and {L₄→011, L₅→101, L₆→110} (the triadic-completion triad). L₆ sits in the second orbit operationally but its self-referential normal makes it the load-bearing one.

The incidences and structural columns:

```
points → lines through:                  lines → points on             normal   S₃-orbit  mode-ownership
  100 :  L₁ L₂ L₄                          L₁ : {100,010,110}            001       A      decomp (uniquely)
  010 :  L₁ L₃ L₅                          L₂ : {100,001,101}            010       A      guard
  001 :  L₂ L₃ L₆                          L₃ : {010,001,011}            100       A      guard
  110 :  L₁ L₆ L₇                          L₄ : {100,011,111}            011       B      decomp + snap
  101 :  L₂ L₅ L₇                          L₅ : {010,101,111}            101       B      snap + regroup
  011 :  L₃ L₄ L₇                          L₆ : {001,110,111}            110 ★     B      guard
  111 :  L₄ L₅ L₆                          L₇ : {110,101,011}            111 ★     C(fix) regroup (uniquely)

  S₃-orbits on points:    A={100,010,001}  weight-1
                          B={110,101,011}  weight-2
                          C={111}          weight-3, S₃-fixed
  S₃-orbits on lines:     A={L₁,L₂,L₃}     normals weight-1
                          B={L₄,L₅,L₆}     normals weight-2
                          C={L₇}           normal weight-3, S₃-fixed
  Duality preserves orbit-structure: the 3+3+1 partition is identical on both sides.
```

Mode-ownership at a glance: L₁ uniquely decomp; L₇ uniquely regroup; {L₂,L₃,L₆} = guard's full territory (the star of 001); {L₄,L₅} are read/write contested (decomp/regroup write them, snap reads them).

### Lojban

```
.i lo Fano cu se pagbu ze daxi je ze linji  (S(2,3,7) ckaji; simxu se snuti).

.i lo linji ce'o lo ckaji be ke'a:

  L₁ "positive-closure"          {100,010,110}    sraji 001     sruri-A    tadji: decomp ralju
  L₂ "GS-guard-coverage"         {100,001,101}    sraji 010     sruri-A    tadji: kajde
  L₃ "SA-guard-coverage"         {010,001,011}    sraji 100     sruri-A    tadji: kajde
  L₄ "GS-triadic-completion"     {100,011,111}    sraji 011     sruri-B    tadji: decomp+snap
  L₅ "SA-triadic-completion"     {010,101,111}    sraji 101     sruri-B    tadji: snap+regroup
  L₆ "guard-reconstitution"  ★   {001,110,111}    sraji 110 ★   sruri-B    tadji: kajde
  L₇ "pure-composite-diagonal"★  {110,101,011}    sraji 111 ★   sruri-C    tadji: regroup ralju
                                                                  (S₃-mintu)

.i S₃ sruri po lo daxi:    A={100,010,001}    B={110,101,011}    C={111}
.i S₃ sruri po lo linji:   A={L₁,L₂,L₃}        B={L₄,L₅,L₆}        C={L₇}
   .i lo se snuti cu se kakne fi lo simxu sruri — ci jo'u ci jo'u pa pe re sefta.

.i tadji ckaji:  L₁ rai decomp;  L₇ rai regroup;  {L₂,L₃,L₆} kajde co prane (= cuvska 001);
   {L₄,L₅} cu simxu fendi (decomp/regroup cu ciska, snap cu te lanli).
```

### Toki Pona

```
ma Pano li jo e ijo luka tu en linja luka tu  (sama wan).

linja en nimi ona en ali pi ona:

  L₁ "wan tan tu"          {100,010,110}    nasin sin: 001    kulupu A    tadji: decomp taso
  L₂ "awen lukin pi e₁"    {100,001,101}    nasin sin: 010    kulupu A    tadji: awen
  L₃ "awen lukin pi e₂"    {010,001,011}    nasin sin: 100    kulupu A    tadji: awen
  L₄ "ali tan e₁"          {100,011,111}    nasin sin: 011    kulupu B    tadji: decomp en snap
  L₅ "ali tan e₂"          {010,101,111}    nasin sin: 101    kulupu B    tadji: snap en regroup
  L₆ "ike kama pona"  ★    {001,110,111}    nasin sin: 110 ★  kulupu B    tadji: awen
  L₇ "linja sewi"     ★    {110,101,011}    nasin sin: 111 ★  kulupu C    tadji: regroup taso
                                                                (S₃ ante ala)

S₃ kulupu pi ijo:        A={100,010,001}    B={110,101,011}    C={111}
S₃ kulupu pi linja:      A={L₁,L₂,L₃}        B={L₄,L₅,L₆}        C={L₇}
   ijo en linja li lon kulupu sama sama — tu wan en tu wan en wan.

tadji li sama linja:  L₁ tan decomp taso.  L₇ tan regroup taso.
   {L₂,L₃,L₆} tan awen taso  (= linja ali pi "001").
   {L₄,L₅} li lon kulupu tu  (decomp/regroup li sitelen,  snap li lukin).
```

### Kēlen

```
Pa jaPāno jakīñehēi ī jamēhēi anhū — la jaPāno ñēim ñe pa-jaorra-ān.

Pa jamēhū ī jōkīña-ān ī jasūma-ān:

  L₁ "anwāñ-anpōrra"            {100,010,110}    jaorra: 001     jasūma A    jamāhe: decomp ān
  L₂ "jakāwa-anpā"              {100,001,101}    jaorra: 010     jasūma A    jamāhe: jakāwa
  L₃ "jakāwa-anrū"              {010,001,011}    jaorra: 100     jasūma A    jamāhe: jakāwa
  L₄ "anlā-anpā"                {100,011,111}    jaorra: 011     jasūma B    jamāhe: decomp ī snap
  L₅ "anlā-anrū"                {010,101,111}    jaorra: 101     jasūma B    jamāhe: snap ī regroup
  L₆ "makawīña-anwāñ"     ★     {001,110,111}    jaorra: 110 ★   jasūma B    jamāhe: jakāwa
  L₇ "anwāñhēi-anlā"      ★     {110,101,011}    jaorra: 111 ★   jasūma C    jamāhe: regroup ān
                                                                  (S₃-anrārra)

S₃-jasūma ñe jamēhū:       A={100,010,001}     B={110,101,011}     C={111}
S₃-jasūma ñe jamēhū-jorra: A={L₁,L₂,L₃}         B={L₄,L₅,L₆}          C={L₇}
   Pa-jaorra-jōña ñi mōrra ñe jasūma — anpā-anpā-anpāmā ñēim ñe anpā-jakīña.

Pa jamāhe ñe jamē:  L₁ ñe decomp ān;  L₇ ñe regroup ān.
   {L₂,L₃,L₆} ñe jakāwa ān  (= jamē anhū ñe "001" anlā).
   {L₄,L₅} pa jamāhe ja-tū  (decomp/regroup ñi cnīna,  snap ñi sēña).
```

### Charter notes

The dual identities now survive in all three. Constructibility: each point now has both its coordinates *and* its line-list; either can construct the other. Reachability: the incidence relations are checkable in finite time from either side (point→lines or line→points). Observability: the two ★ self-referential incidences (L₆↔110, L₇↔111) are the load-bearing structural facts and surface explicitly in each rendering. Coverability: every pair of points reaches a line, every pair of lines reaches a point, the Steiner property is the coverability gate at the structural level.

The mode-ownership and S₃-orbit columns make two further structural facts visible at first appearance: which mode operates on which line, and which lines are S₃-equivalent. The unique-ownership of L₁ (decomp) and L₇ (regroup), and the full-ownership of {L₂,L₃,L₆} by the guard, mean the architecture's mode-decomposition is *visible* in the line table — not just at Increment 6.


---

## Increment 4 — When the skill fires (and when not)

**English skeleton.** The skill is a classifier-and-probe — it activates on events that place a point on the Fano plane and stays quiet on events that don't. Five conditions, four firing and one not:

1. **Substantive move** — any named change to goal, shadows, or artefact; classifies to one of the seven points; lights its three lines.
2. **Session start** — inherited state from prior context places existing points; probes run on the inherited configuration *before* any new registration.
3. **Unmediated attempt (001 alone)** — guard fires; the move is rejected and redirected. The redirect lands on **110 via L₆** (or on 111 via L₂/L₃/L₆ depending on what else is in play). L₆ is the specific line traversed because L₆'s probe is *guard-reconstitution* — it is the structural identity that converts the 001 trigger into a 110 mediated composite.
4. **Mid-task reconsideration** — "let me try another way," "this is getting tangled," "step back." Re-run probes on the cotype's current state. A standing line attempted from a new framing = populating the missing point on that line from a different incidence direction.
5. **Non-firing** — conversational replies, diagnostic reads, formatting changes, single-fact questions. These do not place a point. Registering them anyway is the *over-classification* warning sign: the cotype inflates with noise and the probe signal degrades.

### Lojban

```
.i lo skami cu cfari fi vo, je na cfari fi pa:

  CFARI₁ — ro nu zukte poi cmene gi'e galfi lo terkri ja ctino ja selzbasu;
            ki cnino daxi cu se cikre lo Fano;  ci linji cu se gunma

  CFARI₂ — nuncfari pe lo se sicfri  (skami pamoi clani):
            terkri  ←  nuncpedu fi lo prenu;
            ctino  ←  lo cotype be lo purci nuncfari;
            selzbasu  ←  lo zarci stuzi;
            ki klesi pe ro lo se sicfri daxi;  
            ki probe purci ro tu'a lo cnino zukte

  CFARI₃ — ro nu jersi "001" po'o cu se kajde:
            na'e ralju zukte cu se rejgau;
            ki jersi fi lo "110" tu'a L₆ (ja fi lo "111" tu'a L₂ ja L₃ ja L₆).
            L₆ pu se cuxna  —  ki'u  L₆ du lo guard-reconstitution probe:
            tu'a L₆ cu galfi lo "001" co rivbi  →  lo "110" co simxu

  CFARI₄ — lo nu pensi remi ca'o zukte —  "mi pacna lo drata sidju",
            "fi'i na clite",  "ko mi co prane stuzi"  —
            ki probe se cikre purci lo cabna cotype;
            ki nu prane se sumti cu se troci tu'a lo drata frame —
            li'u lo linji noi se gunma cu sucta lo cnino se sumti

  NA CFARI — bauspu po'o; pa snura sezvyju'i; sucta sitfra; pa fatci preti;
              ro tu'a lo na'e cmima be (terkri, ctino, selzbasu) cmici.
              cikre la te zukte cu binxo banro je nakni —
              lo cotype cu se rinka gleki, je lo probe cu jdika prane.
```

### Toki Pona

```
nasin ni li open kepeken open tu wan;  ona li open ala kepeken open wan:

  OPEN₁ — pali sin pi nimi pona li ante e wile, e pimeja, anu e ijo pali.
           ijo sin li kama lon ma Pano.  linja tu wan li kama suli.

  OPEN₂ — open pi tenpo pali  (tenpo open):
           wile  ←  toki pi jan ni;
           pimeja  ←  cotype pi tenpo pini;
           ijo pali  ←  poki pi pali sin sina.
           o pilin e linja luka tu pi ma Pano  
           lon ijo ali ni  *lon nasin sin pi pali sin*.

  OPEN₃ — pali kepeken "001" taso  —  awen li toki "ala".
           pali sirji li ike.  pali ni li kama tawa "110" lon linja L₆
           (anu tawa "111" lon L₂ L₃ L₆).
           tan seme la L₆?  L₆ ona li nasin pi "ike-kama-pona":
           ona li ante e "001" sirji  →  e "110" nasin sama.

  OPEN₄ — sina toki "nasin ante anu?" lon insa pali —
           o pilin sin e cotype.  o lukin e linja ali pi tenpo ni.
           linja kama suli li wile e ijo sin tan nasin sin —
           o pana e ijo sama tan poka ante.

  OPEN ALA — toki taso, sona pi tenpo lili, ante pi sitelen lukin,
              wile sona pi ijo wan — ni li lon ala ma Pano.
              sina pana e ona la, ma Pano li kama jaki:
              cotype li kama suli kepeken ijo ike,
              linja pilin li kama nasa.
```

### Kēlen

```
Pa jasāke jōnāhi anwāñ anpā;  na pa jasāke jōnāhi anwāñ ān:

  JŌNAHI ANPĀ —  ñi mōrra ñe-jathēña ñe-jamēña ñe-jasēla;
                  ñi jaciēn cnīna ñe jamē jaPāno;
                  ñi jakīñe anhū jaorra-mā.

  JŌNAHI ANRŪ —  ñi sēja-jorrāka  (jasāke jōñahe ān):
                  pa jathēña ñe se sēña ja-ankīwa;
                  pa jamēña ñe se cotype ja jōrra-anwāñ;
                  pa jasēla ñe se anrārra ja-anjakā;
                  ñi jakīñe anwāñ-tā ñe jorrāka-jaPāno —
                  na ñi mōrra cnīna ñēim.

  JŌNAHI ANTĒN —  pa jamāhe ñe jaciēn ja "001" mā;  pa makawēña.
                   ñi mōrra-jakāwa;  ñi anlū ñe jaciēn ja "110" ñe L₆
                   (ī ñe jaciēn ja "111" ñe L₂ L₃ L₆ ñēim).
                   L₆ pa makke —  pa L₆ jaorra-jōñahe ja "110" —
                   ñe L₆ ñi makawēña ñi anwāñ-pamāhe.

  JŌNAHI ANHE —  ñi pa-jōñahe ñe pa-anwēñ —
                  "ñi jōñahe na";  "ñi tōrre-makke" —
                  ñi jorrāka ñe jaPāno-anrārra;
                  ñi mōrra-sēña sin ñe jakīña jaorrāka anwāñ.

  NA JŌNAHI —  ñi sēña-toki, ñi sēña-jōña-jonāhi-anjakā,
                ñi anwāñ-sitelen, ñi sēña ja anwēn ān —
                na pa-jaPāno anciēn anlā.
                ñi mōrra ñe jaPāno anpāwēña — pa jaPāno makke-jaki;
                pa jaciēn ñēim ñi anjakā-jaki, pa jōrra-jojōña ñi mōrra na anjakā.
```

### Charter notes

The triggers are constructible (each names a concrete event-type), reachable (each has a definite test from session-context), observable (each fires with a logged registration or non-registration), and coverable (the disjunction "fire on X / don't fire on Y" partitions move-events).

The structural connection from Increment 3 — that 001's redirect lands on 110 *via L₆ specifically* because L₆ is the guard-reconstitution probe — is load-bearing in trigger 3 across all three languages. The reason is the same in each: 001 sits on three lines (L₂, L₃, L₆); only L₆ contains both 001 and 110; only L₆ has 110 as its normal-point; therefore the redirect is *forced* by incidence, not chosen by convention.

Non-firing is the negative coverability claim: there exist event-types that the architecture *must* leave alone, or the cotype loses observability. All three languages render this same gate; Toki Pona's `jaki` and Kēlen's `anjakā-jaki` (both for "dirty/diluted") carry the most visceral version.


---

## Increment 5 — The loop, Steps A–E, with attached failure modes

**English skeleton.** Same five-step loop. Each step now carries its characteristic failure mode(s) from Increment 8 as an attached `⚠` tag — making the loop self-diagnostic.

- **A. Classify** ⚠ W1 (over-classification) — registering non-substantive moves inflates the cotype.
- **B. Externalise** ⚠ W2 (speculative registration) — shadows that exist only in working memory don't populate Fano points; file-write is the gate.
- **C. Fire probes** — (no characteristic warning at this step; probes are diagnostic, not decisional)
- **D. Act on events** ⚠ W3, W4, W5 split by sub-case:
  - L₁ completion → (no W; extraction or recording)
  - L₂/L₃/L₆ gaps ⚠ **W4 guard omission** — leaving guard-coverage gaps unaddressed
  - L₄/L₅ completion ⚠ **W3 forced snap** — declaring completion when cotype's entailment conflicts with original request
  - L₆ completion → (no W; log only)
  - L₇ inconsistency ⚠ **W5 deletion-reconciliation** — resolving by removing a populated composite breaks monotonicity
- **E. Loop** — (no step-specific warning; W6 mode-fission lives above the loop, at the interface level)

The result: each step *says* what can go wrong with it. The loop is self-monitoring; a session's cotype can be audited by reading the warning-tags against the registrations.

### Lojban

```
.i lo cikre cu mu karni; ro karni cu ckaji pa ja so'i banro kazfri:

KARNI A — KLESI                                                          ⚠ W1 (prane-se-klesi)
  klesi se rinka lo te plekata jo'u lo te ciska;  na'e fi lo se jinvi.
  ganai daxi du "001" po'o gi:  sisti, ko klama KARNI D —  na'e cikre "001" anlā.

KARNI B — SEVJMI                                                         ⚠ W2 (pacna cikre)
  ciska lo zukte fi cotype datnyfi'e:  klesi, zukte ckaji, invariants, te zvati.
  ze'i cikre cu na finti daxi pe lo Fano —  file-ciska du lo simlu klagau.
  jufra stuzi:  .claude/cotype/<gerna>.md

KARNI C — TE LANLI PROBE                                                 (no banro kazfri ralju)
  ki te lanli lo ci linji be lo cnino daxi:
    ci daxi cikre  →  PRANE          (klama KARNI D)
    re daxi cikre  →  LO LALXU       (rejgau bavla'i)
    pa daxi cikre  →  SANLI          (rejgau cikre)
  ciska lo nuncenba fi cotype.

KARNI D — GASNU TE ZUKTE                                                 ⚠ frica:
  L₁ prane:  cpacu lo selzbasu (ganai mintu nuncpedu); ja rejgau kakne.
  L₂/L₃/L₆ lalxu  ⚠ W4 (kajde na zvati):  rejmiu kajde —  
                  refactor lo guard-cleared selsku, ja firgau lo kajde.
  L₄/L₅ prane  ⚠ W3 (bapli snap):  snap-check:  mintu nuncpedu?
                                   na mintu → rejgau drift,  na bapli simxu.
  L₆ prane:  rejgau po'o, na cpacu (mu'i ralju nu prane skami coherence).
  L₇ na mintu  ⚠ W5 (L₇ vimcu):  cikre cimoi simxu —  
                                  *na'e* vimcu pa cikre.
  lalxu da'i:  rejgau bavla'i candidate.

KARNI E — XRUTI                                                          (no karni-ralju banro)
  ca bavla'i zukte:  xruti KARNI A.  cotype banro ze'a.  
  ti se sicfri  lo bavla'i session  ca lo nu sisti.
```

### Toki Pona

```
nasin sike li jo e nasin luka.  nasin wan li jo e nasin pi pakala suli ona:

NASIN A — KULUPU                                                         ⚠ W1 (kulupu lon ijo ala)
  kulupu li tan lukin sina en sitelen sina —  pi pilin sina ala.
  "001" taso la:  sisti!  tawa NASIN D —  "001" wan li lon ala poki.

NASIN B — POKI INSA                                                      ⚠ W2 (sitelen pi insa taso)
  o sitelen e pali sin lon cotype:  kulupu, pali, ijo awen, sama wile pi jan.
  sitelen pi insa lawa taso la, ma Pano li jo ala e ona;  poki li lon ni:
  .claude/cotype/<nimi>.md

NASIN C — LUKIN LINJA                                                    (pakala suli pi nasin ni li lon ala)
  o lukin e linja tu wan pi ijo sin:
    tu wan lon  →  PINI           (tawa NASIN D)
    tu lon     →  WILE            (sitelen e ijo wile)
    wan lon    →  AWEN            (sitelen e linja awen)
  sitelen e ante lon cotype.

NASIN D — PALI TAN PINI                                                  ⚠ ante:
  L₁ pini:  pana e ijo pali (la sama wile);  anu sitelen e ken.
  L₂/L₃/L₆ wile  ⚠ W4 (awen li weka):  open e awen —  
                    awen li toki "pona" anu pali kama awen-pona.
  L₄/L₅ pini  ⚠ W3 (nasin wawa):  o lukin sin wile pi jan!
                                   sama ala  →  toki e ante, pana ala wile.
  L₆ pini:  sitelen taso; ni li pona pi nasin sike.  pana ala.
  L₇ pakala  ⚠ W5 (weka pi L₇):  pali e tu wan pi nasin tu —  
                                  o *weka ala* e tu pi pini!
  ijo wile lon sin:  sitelen lon poki kama;  jan li lawa.

NASIN E — SIKE                                                           (pakala suli pi nasin ni li lon ala)
  pali sin sin la:  tawa NASIN A.  cotype li kama suli lon tenpo ali.  
  pini pi tenpo wan la,  tenpo kama li open lon ni.
```

### Kēlen

```
Pa jasāke jōñahe anhū.  Pa jōñahe ān pa-makke ja-anjē ja-makke-cnīna:

JŌÑAHE ANPĀ — JŌKĒÑEN                                                   ⚠ W1 (jōkēñen-anjakā)
  Pa jōkēñen ñe se sēña ī se jōña;  na ñe se nāra ja jamākke.
  Sē jaciēn "001" mā:  ñi sāke-sirja na;  ñi anlū ñe JŌÑAHE ANHE.

JŌÑAHE ANRŪ — SĒ-PA-ANRĀRRA                                             ⚠ W2 (cnīna-anrāka)
  Ñi jōña ñe jamāhe ñe cotype-jarōña.  Pa jamāhe:  jōkēñen-anciēn,
  jōña-cnīna, anjē anhū makke, jaorra ñe jathēña-jōkīña.
  Sē ñi mōrra ñe se-sēña-anwāñ-jamāhe mā:  na ñi cnīna ñe jaPāno.
  Pa anrārra-stuzi:  .claude/cotype/<jōña>.md

JŌÑAHE ANTĒN — JŌÑA-JAMĒHEHŪ                                            (na pa anjōñahe ja-makke-cnīna)
  Pa jakīña-cnīna pa jamēhū anhū;  ñi jōña ñe jamēhū ān:
    anhū jamāhe →  PA JAMĒ ANJĒ      (ñi anlū ñe JŌÑAHE ANHE)
    antū jamāhe →  PA JAMĒ JORRĀKA-MŌ (ñi cnīna ñe jorrāka-mō)
    wān jamāhe  →  PA JAMĒ ANCĒÑ      (ñi mōkka)
  Ñi cnīna ñe jaciēn-anwāñ ñe cotype.

JŌÑAHE ANHE — MŌRRA TAN JŌÑA                                            ⚠ pamāhe:
  L₁ anjē:    anrārra-jasēla (sē ñēim jōkīña-jōña);  ja cnīna ñe jamēhē-mō.
  L₂/L₃/L₆ jorrāka-mō  ⚠ W4 (jakāwa-anrāka):  
                          ñi mōrra ñe jakāwa-anlū:  makke-cnīna ja-guard-cleared,
                          anu jakāwa-mōrra ja-cnīna ja-anlū.
  L₄/L₅ anjē  ⚠ W3 (mōrra-bapli):  SNAP-jōkīña-jōña —  
                                    sē na ñēim:  mōrra-jōña ñe makawīña-jōrra;
                                    na ñi mōrra ñe bapli.
  L₆ anjē:    cnīna anlā ñe cotype;  na ñi anrārra-jasēla — sē la jamāhe jasēla ān ī.
  L₇ na anjē  ⚠ W5 (L₇-añelē):  sāke-cnīna ñe anwēn ja-cnīna —  
                                  na ñi ñelē anwāñ.
  Sē jorrāka-mō pa:  cnīna ñe jaciēn-anwāñ jōrra ja-anrārra-tā.

JŌÑAHE ANCĒÑ — JAMĒHĒ                                                   (na pa anjōñahe ja-makke-cnīna)
  Sē sāke-cnīna ī:  ñi anlū ñe JŌÑAHE ANPĀ.  Pa cotype ñi anrārra anjē-jōrjanāe.
  Pa jasāke ñi anrārra-anjē ñe:  ñi anrārra-jasēla ān; anu ñi anwēn ñe sāke-cnīna ja-ankīwa.
```

### Charter notes

Constructibility: each step is named by a concrete predicate. Reachability: each step has a clear precondition. Observability: Step B's file-write is the gate that converts working-memory shadows into observable points. Coverability: Step D's six sub-cases are the *exhaustive* response set for line-states.

The L₇ deletion-prohibition is the most charter-load-bearing claim in the entire loop. It says: *the cotype's monotonicity is not just convenience but constructibility-of-future-state*. If you can delete a populated composite, then no point on the Fano plane is permanently constructible — every distinction can be retroactively erased — and the architecture loses its persistence gate.

The failure-mode tags make the loop self-diagnostic: a session can audit its own cotype by checking, for each step taken, whether the characteristic warning was risked. The diagnostic kit (Increment 8) is now embedded in the loop description rather than separately consulted.

---

## Increment 6 — The four originals as modes of the loop

**English skeleton.** Each of the four prior skills is a *mode* of the single classify-register-probe loop, characterized by three things: where it enters the loop, which direction it runs, and which lines are its distinctive territory.

| Original | Entry signature | Direction | Distinctive lines |
|---|---|---|---|
| decomposable-by-entailment | 100 | lift (e₁ outward) | L₁, L₄ |
| snap-to-grid | inherited cotype (read pass) | contract (e₁ inward) | L₄, L₅ |
| regroup-from-shadows | 010 | symmetric (lens on e₂) | L₅, L₇ |
| mediation-guard | any with e₃ | reject-and-redirect | L₂, L₃, L₆ |

**The structural fact the table hides.** Each mode's "distinctive lines" is a specific subset of the Fano plane, and the four subsets *cover* all seven lines, with overlaps at L₄ and L₅:

```
                    L₁    L₂    L₃    L₄    L₅    L₆    L₇
   decomp           ✓                 ✓
   snap                               ✓     ✓                (read-only)
   regroup                                  ✓           ✓
   guard                  ✓     ✓                 ✓
   ─────────────────────────────────────────────────────────
   unique to:    decomp                                  regroup
                              guard's full point-star {L₂,L₃,L₆} = star(001)
```

L₁ is uniquely decomp's; L₇ is uniquely regroup's; the guard's territory is exactly the three-line neighbourhood of 001 — its full point-star. L₄ and L₅ are the *read/write contested* lines: snap reads them, decomp writes L₄, regroup writes L₅.

**Step-by-step mapping into the loop.** decomp's Step 1 (halt-and-name) = Step A at the session's first move; its Steps 2–5 = iterated A–C at 100 → 110 → 111; its Step 6 (multi-angle) = iterated Step A from a framing orthogonal to the first when L₁ stands. snap's cotype is this skill's cotype; its inventory/quotient/entailment-read/snap-check are Steps B–D in a *read-only* pass. regroup's Step 7 (behaviour preservation) = Step D response to L₅ completion. The guard's prohibition is the 001-halt in Step A; its redirect is the forced progression to 110 or 111 in Step D.

**Warning the section carries.** The modes are valid *names for line-subsets*, not separate skills. Re-instantiating them as separate skills loses the Fano structure that makes the probes load-bearing.

### Lojban

```
.i lo vo cnano stuzi cu tadji be pa cikre — frica fa:
   (a) lo se cfari klesi
   (b) lo te jersi farna
   (c) lo te dauspu poi se ralju

  decomposable-by-entailment
    cfari:   "100"   (lo terkri pe lo munje cu galfi pa ctino)
    farna:   galtu   (lift)
    ralju:   L₁  L₄

  snap-to-grid
    cfari:   selsicfri cotype  (te lanli po'o, na ciska cnino)
    farna:   cmalu   (contract)
    ralju:   L₄  L₅   ke se simlu fi lo prenu nuncpedu

  regroup-from-shadows
    cfari:   "010"   (lo selzbasu cu galfi pa ctino)
    farna:   simxu   (lenjo;  na'e adjunction)
    ralju:   L₅  L₇

  mediation-guard
    cfari:   ro klesi noi e₃ cu cmima
    farna:   rivbi je rejgau
    ralju:   L₂  L₃  L₆   (= ro linji co cmima 001)


.i sucta pe lo karni:

  decomp karni-1 (sisti je cmene)            =  KARNI A pe lo pamoi zukte
  decomp karni-2 bi'i 5 (sisku, cmene
   costructure, simxu, entailment)            =  iterated KARNI A-C
                                                 ku'u "100 → 110 → 111"
  decomp karni-6 (so'i frame troci)           =  iterated KARNI A
                                                 ca L₁ sanli;  cikre lo lalxu daxi
                                                 fi lo orthogonal frame

  snap cotype                                  =  ti skami cotype
  snap karni-2 bi'i 5                          =  KARNI B-D, te lanli po'o

  regroup karni-7 (selsku se kantu te dauspu)  =  KARNI D fi L₅ prane

  guard rivbi                                  =  001-sisti pe KARNI A
  guard rejgau                                 =  bapli xratei lo 110 ja 111
                                                  pe KARNI D


.i ki jundi: ro ze linji cu se cmima pa tadji ja re —
   L₁ rai decomp;  L₇ rai regroup;  L₂ L₃ L₆ rai guard
   (= lo ci linji be 001 anlā);  L₄ ce'o L₅ cu simxu fendi.

.i ku'i: lo tadji cu cmene lo linji-pagbu po'o.
   na cuxna lo nu xrutiselsku zekri tadji kruvi vo cnano stuzi —
   xrutiselsku xrani lo Fano stuzi co rinka lo te dauspu prane.
```

### Toki Pona

```
nasin pi pali pini tu wan tu li nasin pi nasin sike wan.
nasin tu wan tu li ante kepeken:
   (a) ma open
   (b) nasin tawa
   (c) linja sin pi probe

  decomposable-by-entailment  (decomp)
    ma open:    "100"   (wile sewi li tawa lon pimeja)
    tawa:       sewi   (lift)
    linja:      L₁  L₄

  snap-to-grid  (snap)
    ma open:    cotype pini   (lukin taso)
    tawa:       anpa   (contract)
    linja:      L₄  L₅   lon poka pi wile open pi jan

  regroup-from-shadows  (regroup)
    ma open:    "010"   (ijo pali li tawa lon pimeja)
    tawa:       sama   (ilo lukin;  ala adjunction)
    linja:      L₅  L₇

  mediation-guard  (awen)
    ma open:    nasin ali pi e₃ lon
    tawa:       awen e tawa, pana e tawa sin
    linja:      L₂  L₃  L₆   (= linja ali pi "001")


sama pi nasin sike:

  decomp nanpa wan (sisti, nimi)              =  NASIN A pi tenpo open
  decomp nanpa tu-luka (alasa, nimi ilo,
                        kama wan, kama tan)   =  NASIN A-C pi tenpo mute
                                                 lon "100 → 110 → 111"
  decomp nanpa luka wan (nasin mute pi alasa) =  NASIN A pi tenpo mute
                                                 lon kulupu ante,
                                                 ca L₁ li awen

  snap cotype                                  =  cotype pi nasin sike ni
  snap nanpa tu-luka                           =  NASIN B-D, lukin taso

  regroup nanpa luka tu (lukin e nasin sama)  =  NASIN D pi L₅ pini

  awen sisti                                   =  "001" sisti lon NASIN A
  awen pana sin                                =  tawa wile "110" anu "111"
                                                  lon NASIN D


o sona: linja ali luka tu li lon kulupu wan anu tu —
   L₁ tan decomp taso.  L₇ tan regroup taso.
   L₂ L₃ L₆ tan awen taso  (= linja ali pi "001").
   L₄ en L₅ li lon kulupu tu.

taso:  nasin tu wan tu li nimi pi kulupu linja taso.
   sina o pali ala e ona sama nasin sike ante!  
   ni li pakala e nasin pi ma Pano,  
   li pakala e wile kama pi linja sin.
```

### Kēlen

```
La jasēja anwāñ-mā jōñahe ja-jaPāno ān ñi pa-jōrra-anhū.
Ñi anjōrra ja-anhū ñe ñi sēja-ān:
   (a) Jōkēñen ja-anpā
   (b) Jōrra ja-tā
   (c) Jamē ja-jorrāka

  decomposable-by-entailment  (decomp)
    jōkēñen:    "100"   (pa jathēña-anlā ñi mōrra ñe jamēña-cnīna)
    jōrra:      ñi jōraþ  (lift)
    jamē:       L₁  ī  L₄

  snap-to-grid  (snap)
    jōkēñen:    cotype-anrārra   (pa sēña anlā;  na pa cnīna)
    jōrra:      ñi mōraþ  (contract)
    jamē:       L₄  ī  L₅   ñe jōkīña-jōña

  regroup-from-shadows  (regroup)
    jōkēñen:    "010"   (pa jasēla-anlā ñi mōrra ñe jamēña-cnīna)
    jōrra:      ñi ñēim   (jajēña;  na adjunction)
    jamē:       L₅  ī  L₇

  mediation-guard  (jakāwa)
    jōkēñen:    anjōkēñen anhū ja-mā e₃
    jōrra:      ñi makke-cnīna  ī  ñi cnīna-anlū
    jamē:       L₂  ī  L₃  ī  L₆   (= jamē anhū ñe "001" anlā)


La jasēja jamāhe ñe jōñahe ja-jaPāno:

  decomp jōñahe ja-wan (sāke-sirja, jōña-jathēña)
                              =  JŌÑAHE ANPĀ ja sāke ja-anpā
  decomp jōñahe ja-tū-cēñ      =  jōñahe anpā-anrū-antēn ja-jorra
                                  "100 → 110 → 111"
  decomp jōñahe ja-he (sāke ñe-anwēn-anhū)
                              =  JŌÑAHE ANPĀ ñe jamāhe-anwāñ
                                  sē L₁ pa anwēn —
                                  ñi cnīna ñe jamāhe ja-anwāñ
                                  ñe jamāhe-anwāñ ja-tā

  snap cotype                  =  ti jasēja cotype
  snap jōñahe ja-tū-cēñ        =  JŌÑAHE ANRŪ-ANTĒN-ANHE, sēña anlā

  regroup jōñahe ja-he (anwēn-jakōrra)
                              =  JŌÑAHE ANHE ñe L₅ anjē

  jakāwa makke                 =  "001" sāke-sirja ñe JŌÑAHE ANPĀ
  jakāwa anlū                  =  cnīna ja-bapli ñe "110" anu "111"
                                  ñe JŌÑAHE ANHE


Pa jamēhū ñe jasēja:  pa jamēhū anwāñ ñe jasēja ān anu antū.
   La L₁ ñe decomp ān.   La L₇ ñe regroup ān.
   La L₂ ī L₃ ī L₆ ñe jakāwa ān  
        (= jamē anhū ñe "001" anlā — pa jakāwa pa anwēn-jamē).
   Pa L₄ ī L₅ ñēim ñe jasēja antū.

Mā:  pa jasēja ān ñe jōña ñe jamēhū-sūma ān anwāñ.
   Na ñi xrūti-jōña ñe jasēja ñe jaPāno-sēja-ān —
   pa xrūti-jōña ñi mōrra-jaki ñe jaPāno ī
   ñi mōrra-jaki ñe anjōrra ja-jōkīña ja-tā.
```

### Charter notes

The modes-as-line-subsets is itself a charter-clean distinction: constructible (each mode's line-set is a specified subset of {L₁..L₇}), reachable (each mode's entry condition fires from session-context), observable (which mode is active is readable from which lines are accumulating populations in the cotype), coverable (the four subsets cover all seven lines).

The deeper point — and the reason the section ends with a warning — is that *re-instantiating* the modes as separate skills would break a different charter gate: the constructibility of cross-mode entailments. L₄ and L₅ are *shared* between read and write modes; if you split modes into separate skills, you lose the entailment that snap-to-grid's read-pass over L₄ is the same line decomp wrote to. The unified loop preserves this; separate skills destroy it.


---

## Increment 7 — S₃-symmetric content

**English skeleton.** S₃ permutes the three axes among themselves — 3! = 6 permutations, the basis-permutation subgroup of Aut(Fano). The action splits both points and lines into the same 3 + 3 + 1 orbit pattern (duality preserves orbits):

```
                    points                          lines
   weight-1 :   {100, 010, 001}                {L₁, L₂, L₃}    (normals weight-1)
   weight-2 :   {110, 101, 011}                {L₄, L₅, L₆}    (normals weight-2)
   weight-3 :         {111}      ★ S₃-fixed         {L₇}        ★ S₃-fixed
```

The two ★ fixed structures — **111** (triadic-full) and **L₇** (pure-composite-diagonal) — are the axis-symmetric core. They are a *non-incident* fixed pair: 111 ∉ L₇, but L₇'s normal is 111. They are what the architecture retains regardless of which axis the practitioner calls "first."

**Design heuristic.** A new move should preserve S₃-symmetry at {111, L₇} — i.e., should treat the three axes interchangeably when operating on the triadic-full state or the composite-diagonal — and may break symmetry freely on the other orbits.

**The larger group.** Aut(Fano) ≅ GL(3, 𝔽₂) ≅ PSL(2, 7), order 168. S₃ has order 6, so [PSL(2,7) : S₃] = 28 cosets — 28 different "named axis frames" available analytically. **But only S₃ is operationally realized**, because the practitioner only has three axis-handles with semantic content (goal, shadows, artefact); the other 27 cosets permute signatures *without respecting the axis decomposition*, so their distinctions are not reachable from the practitioner's vocabulary. This is the exact charter case the realizability principle describes: PSL(2,7) is constructible, but only S₃ is reachable, observable, and coverable at runtime.

### Lojban

```
.i lo S₃ cu binxo lo ci rajra po lo nu te cuxna:
   3! = 6 lo te cuxna.

.i lo S₃-sruri po lo daxi:
     {100, 010, 001}     ka'i 1    (lo pure-axis)
     {110, 101, 011}     ka'i 2    (lo simxu)
     {111}               ka'i 3    NA BINXO  ★

.i lo S₃-sruri po lo linji:
     {L₁, L₂, L₃}        sraji ka'i 1
     {L₄, L₅, L₆}        sraji ka'i 2
     {L₇}                sraji ka'i 3    NA BINXO  ★

.i lo re na binxo stuzi —  la "triadic-full" .e la L₇ —
   cu lo simxu naxle pe lo skami stuzi.
   .i ti lo na'e simxu krasi simxu:
   "111" na cmima L₇,  ku'i lo se sraji be L₇ du "111" —
   re S₃-mintu pe na'e cmima simxu.

.i te skami stuzi finti:
   gasnu noi mintu po lo S₃ ca lo nu zukte ti'a {111, L₇} —
   ku'i kakne lo nu na mintu ca lo nu zukte ti'a lo drata.


.i lo prane simxu pe lo Fano:
   Aut(Fano) = GL(3, F₂) = PSL(2, 7);  cmima li 168.
   .i lo S₃ cu pagbu lo PSL(2,7);  168 / 6 = 28 simxu te cuxna.

.i ku'i:  lo S₃ po'o cu se zukte simlu.
.i lo te PSL(2,7) ka simxu cu se cmavlaste —
   pa sucta kakne, ku'i na zukte kakne.
.i ti lo charter pe lo prenu:
   te PSL(2,7) simxu cu *PRANE SUCTA*,  *NA ZUKTE SIMLU*  —
   lo prenu kakne fi lo se cmene rajra (terkri, ctino, selzbasu) po'o,
   na lo cnano simxu poi lo cmene cu na sevzi pagbu.

   .i mu'a:  pa runtime klesi cu cmima 
   ganai gi'i prane sucta gi'i zukte kakne gi'i se simlu gi'i se gunma —
   la PSL(2,7) na zukte kakne;  no'i na cmima lo runtime klesi.
   la S₃ cu cmima.
```

### Toki Pona

```
nasin pi ante pi ijo tu wan — S₃ — li jo e nasin pi ante luka tu.
ona li ante e nimi pi nasin tu wan, taso nasin ali li sama insa.

S₃ li ante e kulupu pi ijo:
  ijo:
    {100, 010, 001}     pi ali "wan"           (nasin taso)
    {110, 101, 011}     pi ali "tu"            (kulupu pi tu)
    {111}               pi ali "tu wan"        ANTE ALA  ★
  linja:
    {L₁, L₂, L₃}        nasin sin pi ali "wan"
    {L₄, L₅, L₆}        nasin sin pi ali "tu"
    {L₇}                nasin sin pi "tu wan"    ANTE ALA  ★

ijo "ali" en linja L₇ li ante ala.  ona li sewi pi nasin ali —
  ali lon ala L₇;  
  taso nasin sin pi L₇ li sama "ali" —
  ona li tu pi sama, taso ona li lon ala.

jan pi pali pi nasin ni li o sona:
  pali sin ona o sama lon poka pi "ali" en L₇  —
  pali sin ken ante lon poka pi ijo ante.


kulupu pi nasin ante suli pi ma Pano:
  Aut(Fano) = PSL(2, 7);  nanpa 168.
S₃ li lon insa.  168 / 6 = 28 kulupu lili.

taso:  S₃ taso li nasin pi pali.
PSL(2,7) li nasin pi sona taso — 
  ona li ante e nimi taso lon nasin ante.
  ona li sona ala e nimi sina (wile, pimeja, ijo pali) — 
  jan li lon nasin wile-pimeja-ijo;
  jan li lon ala nasin pi nimi ala.

ni li sama toki sina pi sona:
  ante pi ken kama lon nasin sona, taso ken kama ala lon pali — 
  ni li ante ala pi tenpo pali.
PSL(2,7) li sona,  taso ona li pali ala.
jan o pali kepeken S₃.
```

### Kēlen

```
La S₃ ñi jōrra ñe jakīñehū anhū ja-mā —
ñi jōrra ja-jōña, na ñi jōrra ja-mōrra-jakīña.

Pa anjasūma ñe S₃-jōrra:
  jamēhū:
    {100, 010, 001}     pa anwēñ-anpā    (anjakīña jōrra-mā)
    {110, 101, 011}     pa anwēñ-antū    (anjasūma jōrra-mā)
    {111}               pa anwēñ-anhē    NA ÑI JŌRRA  ★
  jamēhū-jorrāka:
    {L₁, L₂, L₃}        pa jaorra anwēñ-anpā
    {L₄, L₅, L₆}        pa jaorra anwēñ-antū
    {L₇}                pa jaorra anwēñ-anhē — NA ÑI JŌRRA  ★

La jamē ja "anlā" ī la L₇:  anjē anhū ja-S₃-anrārra.
La jaciēn anlā na pa-jamē-L₇;  ka pa jamē-L₇-jorrāka ñe jaciēn anlā —
ñi tū jōrra-jōnāhi, ña anwēn-tū.

Ñi jōkīña ja-anjōrra:
  ñi jōkīña ñi pa-jōrra-S₃ ñe jaciēn "111" ī jamē L₇;
  ñi jōkīña ñi pa-ankīña-jōrra ñe jaciēn-pamāhe ī jamē-pamāhe ñēim.


La jasūma-anjōrra-anlā ñe jaPāno:
  Aut(Fano) = PSL(2, 7);  pa anwēñ "168".
La S₃ pa-jasūma-anmā ñe PSL(2,7);  pa anwēñ ja-jasēja "28".

Ka:  La S₃ ān ñi jōrra-jasēja-ankīwa.
La PSL(2,7) pa-jasūma-anlā:
  ñi sēña ñe sēja,  na ñi mōrra ñe jōkēñen —
  pa-anjōkēñen jathēña-jamēña-jasēla ān,
  na pa-anjōkēñen anjōrra-jakīña-anpāhe.

Ñe sēja-charter pa anmākke:
  Pa anjōkēñen anlā:
    pa makke-jōkēñen,  
    pa makke-anwēn,
    ñi sēña ñi tōrre-anhū,
    na ñi mōrra ja-jaciēn-ja-tā —
  pa jakīña-jamāhe ñe anjōkēñen-tā.
  
  La PSL(2,7) pa makke-jōkēñen;  na pa makke-anwēn.  
  Ñe sēja-charter na pa jaciēn ja-jakīña-jamāhe.
  La S₃ pa anhū anmākke;  ñi mōrra ñe jasēja.
```

### Charter notes

This is the increment where the realizability principle loads directly onto the architecture. The skill's own structure produces an example of each charter case:

- **Both constructible and reachable**: the seven axis-signatures, the seven Fano-line probes, S₃'s six permutations. These pass all four gates and are operational distinctions.
- **Constructible but not reachable**: the remaining 162 elements of PSL(2,7), and the 27 cosets of S₃ in it. These are mathematically definable but the practitioner has no axis-handle to operate them with. They fail the second gate; they are *not* valid runtime distinctions.

This case — *constructible-but-not-reachable* — is the one the charter explicitly names as failing. The skill demonstrates it: there is a larger automorphism group available analytically, and the architecture explicitly chooses S₃ instead. The choice isn't taste; it's the four-gate test applied at the design layer.

The design heuristic — preserve S₃ at {111, L₇}, break it elsewhere — is itself charter-realizable: invariance at the fixed pair is constructible (the fixed-pair is named), reachable (a new move can be tested against axis-relabeling), observable (the test outcome is a yes/no), coverable (the test applies uniformly to all candidate moves).


---

## Increment 8 — Boundaries and warning signs

**English skeleton.** Three boundaries (when the skill doesn't apply) and six warning signs (how it gets misused). The structural reading: each warning is a *specific charter-gate failure mode*. The skill comes with its own diagnostic kit because each move-class has a constructibility/reachability/observability/coverability property that can break.

**Boundaries — non-application:**
1. Non-substantive move (conversational, diagnostic, formatting, single-fact) — no point lands on the plane.
2. No goal, no artefact, no shadows — the three axes have no anchor; the plane has nothing to host.
3. User has explicitly disabled the axis-structure for a named reason — meta-level non-engagement.

The skill does not replace judgement: it is a classifier-and-probe, not a planner. Probe-gaps are candidate next-work; the user disambiguates.

**Warning signs — misuse modes mapped to charter gates:**

| sign | failure | gate broken |
|---|---|---|
| W1 over-classification | register non-substantive moves → noisy cotype → probe-signal degraded | observability |
| W2 speculative registration | shadow written only in working memory, not to file | observability (file-write is the gate) |
| W3 forced snap | declare L₄/L₅ completion when cotype conflicts with the request | alignment with request (the meta-gate) |
| W4 guard omission | leave L₂/L₃/L₆ gaps; architecture loses mediation on e₃ | coverability |
| W5 L₇ deletion-reconciliation | delete a populated composite to resolve L₇ inconsistency | constructibility-across-time (monotonicity) |
| W6 mode-fission | re-name the four modes as separate skills | reachability of cross-mode entailments |

W3 is the odd one: it is the case where the produced distinction *is* valid (constructible, reachable, observable, coverable in itself) but doesn't match what the user asked for. The charter gates pass and the architecture still produces the wrong deliverable. That's why "drift" is logged as information rather than reconciled by force — the conflict between cotype's entailment and the user's request is itself the signal.

### Lojban

```
.i NA CIKRE:
   (1) na ralju zukte —  no daxi cu se cikre fi lo Fano
   (2) no terkri, no selzbasu, no ctino —  no rajra se vasru
   (3) prenu pu na'e jersi lo skami fi pa krasi


.i lo skami na basti lo nu jdice —  cikre je te dauspu po'o;
   te dauspu lalxu cu bavla'i candidate;  prenu cuxna gi'e fendi.


.i BANRO KAZFRI  (charter-gate xrani):

 (W1) PRANE-SE-KLESI    — cikre na ralju zukte;
                           cotype gunma cu se jonai;  te dauspu kanji se gleki.
                           [gate:  ka se simlu]

 (W2) PACNA CIKRE        — ctino sucta, na ciska fi datnyfi'e;
                           ze'i ctino cu na finti daxi;
                           file-ciska du lo simlu klagau.
                           [gate:  ka se simlu]

 (W3) BAPLI SNAP         — cusku L₄/L₅ prane ca na mintu lo prenu nuncpedu;
                           se gasnu cu na se nuncpedu;
                           drift cu surface, na ki bapli lo simxu.
                           [gate:  alignment — gateu drata]

 (W4) KAJDE NA ZVATI     — L₂/L₃/L₆ lalxu se vimcu;
                           skami na firgau pe e₃;
                           na'e ralju zukte cu xratei.
                           [gate:  ka se gunma]

 (W5) L₇ VIMCU           — vimcu pa simxu, na cikre cimoi;
                           monoton xrani;  bavla'i sicfri xrani.
                           [gate:  ka prane sucta be lo bavla'i]

 (W6) XRUTI-CMENE TADJI  — cmene vo tadji tai vo cnano skami;
                           Fano stuzi xrani;
                           L₄/L₅ cross-mode entailment cu se vimcu.
                           [gate:  ka kakne zukte]


.i ro banro kazfri du pa charter gate poi se xrani —
   ti lo skami banro kazfri co kanji noi cmene fi ke
   "kakne sucta, ku'i na kakne zukte" cmavlaste —
   la charter cu se simlu zukte fi lo skami stuzi nuncfari.
```

### Toki Pona

```
nasin sike li open ala lon ni:
   (1) pali li lili — pali sin li lon ala ma Pano
   (2) wile ala, ijo pali ala, pimeja ala — ma Pano li jo ala e ijo
   (3) jan li toki "nasin ni li wile ala" — nasin sike li sisti


nasin sike li lawa ala.  ona li kulupu li lukin linja taso.
linja wile li ijo pi tenpo kama;  jan li cuxna;  jan li fendi.


nasin pi pakala  (luka pi sona pi pakala suli):

 (W1) KULUPU LON IJO ALA   —  ona li sitelen e ijo lili lon cotype;
                                cotype li kama jaki;  linja lukin li nasa.
                                [luka:  pi lukin]

 (W2) SITELEN PI INSA TASO —  pimeja li lon insa lawa taso, li lon ala poki;
                                ma Pano li jo ala e ona;
                                tenpo li weka e pimeja insa.
                                [luka:  pi lukin]

 (W3) NASIN WAWA            —  ona li toki "L₄/L₅ li pini!" 
                                taso cotype li sama ala wile pi jan ni.
                                ijo sin sin li sama ala wile —  o pana ala ona,
                                o toki taso e ante.
                                [luka:  pi wile pi jan]

 (W4) AWEN LI WEKA          —  L₂, L₃, anu L₆ li wile, taso jan li lukin ala;
                                nasin sike li lukin ala e₃;
                                nasin sirji ike li lon, jan li sona ala.
                                [luka:  pi nasin ali]

 (W5) WEKA PI L₇            —  ona li weka e tu pi nasin tu pini, li sitelen ala e tu wan;
                                cotype li ken ala kama suli;
                                tenpo kama pi pali li pakala.
                                [luka:  pi kama suli pi tenpo]

 (W6) NIMI SIN PI TADJI     —  ona li nimi e nasin tu wan tu sama nasin sike tu wan tu;
                                ma Pano li pakala;
                                L₄ en L₅ pi nasin tu li weka.
                                [luka:  pi ken kama]


nasin pi pakala ali li tan luka wan li weka:
   ijo wan li wile e luka —  
   ken pali,  ken kama,  ken lukin,  ken kulupu,  
   en sama wile pi jan.
   pakala li weka e wan tan luka — nasin sike li toki "ike" tawa ona.
```

### Kēlen

```
Na ñi mōrra ñe jasāke:
   (1) ñi sāke-anrāka — na pa jaciēn ñe jaPāno
   (2) na pa jathēña, na pa jasēla, na pa jamēña-anrārra —
       na pa jakīñe-anwēn
   (3) ñi mōkka ñe sēja-jakāwa — pa makke-sēja


Na ñi mōrra ñe jasēja ñe jakōrra-jōña.
La jasēja ñēim jōkēñen ī jōrra-jajēña;  pa anjamāhe ñi mōkka ñe jasāke-tā;
ñi jakōrra ñe sēja-jōkīña;  ñi tōrre ñe sēja-jōkīña.


Pa anjōñahe ja-makke-jasēja  (anhē-ñelē ñe charter-jōkīña):

 (W1)  JŌKĒÑEN-ANJAKĀ    —  ñi cnīna ñe sāke-anrāka;
                              pa cotype anjakā;  pa jorrāka anrāka.
                              [makke:  ñi sēña]

 (W2)  CNĪNA-ANRĀKA       —  ñi mōkka ñe jamēña pa sūmama anwēn,
                              na ñi cnīna ñe anrārra-jamāhe;
                              pa jaciēn-anrāka — na ñi jōrra-anlā.
                              [makke:  ñi sēña]

 (W3)  MŌRRA-BAPLI       —  ñi tōrre "L₄/L₅ pa anjē" sē na ñēim ñe jōkīña-jōña;
                              pa jasēla-cnīna na pa jōkīña;
                              ñi anwēñ-jōña-mōñ — na ñi bapli mōrra-cnīna.
                              [makke:  ñi ñēim ñe jōkīña]

 (W4)  JAKĀWA-ANRĀKA      —  L₂, L₃, anu L₆ pa-jorrāka-mō, na ñi cnīna-mōrra;
                              pa jasēja-anrāka ñe e₃;
                              pa zukte-sirja ja-makke ñi anwāñ-ankīwa.
                              [makke:  pa mōrra ja-anlā]

 (W5)  L₇-AÑELĒ            —  ñi añelē ñe jasūma ān, na ñi cnīna ñe jasūma-jamāhē;
                              pa cotype-jōrjanāe ñi xrani;
                              pa jasēja ñe sēja-tā ñi xrani.
                              [makke:  pa makke-jōkēñen ja-tā]

 (W6)  JŌÑA-JAJĒÑA-TAÑ    —  ñi jōña ñe anjōrra-anhū sūmama jasēja-anlā;
                              pa jaPāno ñi xrani;
                              L₄ ī L₅ pa cross-mode-entailment ñi añelē.
                              [makke:  pa makke-anwēn]


Pa anjōñahe ja-makke-jasēja ān ñe charter-jōkīña ja-makke:
   pa jaciēn anlā ñe sēja-jōña-anwāñ:
     pa makke-jōkēñen, pa makke-anwēn, ñi sēña, pa anwēn,
     ī la jōkīña-jōña-anwāñ ñe jathēña-jōkīña.
   Pa anjōñahe ja-makke ñi añelē ān ñe jaciēn-jōkīña —
   ñi sēña ñi pa-makke ñe jōkīña ñe jaPāno-mōrra.
```

### Charter notes

This increment is the charter operating on itself. Each warning sign is a runtime distinction-failure named in the same vocabulary the charter uses to admit distinctions in the first place. The result is a closed loop: the architecture passes its own charter check (Increment 9), and the warning signs are exactly the points where that check can come undone in practice.

The W3 case — *forced snap* — deserves special note. It is the only warning that doesn't map to a four-gate violation directly. The cotype's L₄/L₅ completion *is* a valid runtime distinction in itself; the failure is that it doesn't match the user's original request. This is a fifth gate that sits *above* the four — alignment with the request — and it is the one that admits external semantic content (what the user actually wanted).

The W5 case — *L₇ deletion* — is the constructibility-over-time variant of the constructibility gate. It says: it is not enough that a distinction is constructible at the moment of registration; it must remain constructible across sessions. Deletion breaks that temporal extension.


---

## Increment 9 — Charter check with time-extension

**English skeleton.** The architecture audits itself against the four gates. Six distinctions × four gates = 24 cells, every cell ✓. Each row now adds a fifth column — *persists via* — naming the mechanism by which each gate's satisfaction extends across sessions, not just within one. The fold takes the static check from Increment 9's original form and adds the temporal axis that Increment 10 will fully develop.

Each distinction maps back to structural content established earlier: the seven signatures are the Fano points (Increments 2, 3), the seven probes are the Fano lines (Increment 3), the guard response is the star of 001 (Increment 6), the adjunction is the e₁ axis (Increments 1, 6), the lens is the e₂ axis (Increments 1, 6), L₆ is the load-bearing reconstitution (Increment 3). Note that e₃ has no row of its own — it is the negative axis, audited indirectly via the guard-response row.

```
distinction       │ constructible    │ reachable        │ observable        │ coverable           │ persists via
──────────────────┼──────────────────┼──────────────────┼───────────────────┼─────────────────────┼─────────────────
7 axis-sigs       │ read/write set   │ every move = 1   │ tagged at Step B  │ synthesisable       │ axis-tags in cotype
7 Fano-lines      │ triple-check     │ on registration  │ completion/gap    │ synthetic cotype    │ probe-state section
guard response    │ {L₂,L₃,L₆}=★001  │ on e₃-bit moves  │ reject+redirect   │ constructed 001     │ drift events section
e₁ adjunction     │ lift / contract  │ both instantiated│ L₄ unit-of-adj.   │ round-trip          │ shadow-list completeness
e₂ symmetric lens │ extract/rebuild  │ on refactor/dup. │ L₅ behaviour-pres.│ tests re-run        │ original test resources
L₆ reconstitution │ 001+110→111      │ both populated   │ log distinguish.  │ cotype synthesis    │ 001+110 stay populated
```

**The fold.** The four gates are now read with a time dimension. Each gate's satisfaction at a moment is the static check; each gate's *durable* satisfaction across sessions is the dynamic check. Six × five = 30 cells, every cell ✓.

**The closure observation.** The four gates themselves satisfy the four gates — each is constructible (a definite test), reachable (applicable to any candidate), observable (yes/no outcome), and coverable (the test applies uniformly). With the time-extension, the closure strengthens: the gates plus their persistence-mechanisms all satisfy themselves *durably*. The architecture's self-audit is not just instantaneous but continuous.

### Lojban

```
.i CHARTER CIKRE  —  vo gateu jo'u lo bavla'i tcita pe xa klesi:
   PRANE SUCTA  ·  KAKNE ZUKTE  ·  SE SIMLU  ·  SE GUNMA  ·  TE SE SICFRI

 (1) ze klesi:    plekata/ciska · zukte cmima · KARNI B tcita · finti dauspu · klesi-tcita pe cotype
 (2) ze linji:    ci-mei kanji · cikre · prane/lalxu se ciska · finti cotype · te dauspu state-tcita
 (3) kajde:       {L₂,L₃,L₆}=★001 · e₃ cmima · rivbi+rejgau · finti 001-zukte · drift tcita
 (4) e₁ adjunc.:  galtu/cmalu · re farna se zukte · L₄ prane · retri klama · gunma cikre be sevjmi
 (5) e₂ lenjo:    cpacu/rejgau · refactor/dup. · L₅ prane · pruce xruti · pruce datni se sevjmi
 (6) L₆ rekon.:   vlina · re re cikre · log nuncfari · cotype finti · 001 jo'u 110 ca'o cikre

.i ro vei xa ge mu vo gateu cu cusku "prane".
.i lo vo gateu sevzi cu prane vei xa ge mu kanji —
   no'i lo charter cu sevzi-cikre prane, ze'a ba'o lo nuncfari.
```

### Toki Pona

```
NASIN PI SONA SAMA  —  luka pi nasin (ken pali · ken kama · ken lukin · ken kulupu · ken awen)

 (1) kulupu luka tu:    lukin/sitelen · pali ali · nimi lon NASIN B · pali sin · kulupu lon poki
 (2) linja luka tu:     pana lukin tu wan · open lon ali · poki pi sona · pali cotype · poki pi linja-lon
 (3) tawa pi awen:      {L₂,L₃,L₆}=★001 · pali pi e₃ · awen+tawa sin · pali e "001" · poki pi nasin wawa
 (4) e₁ sewi-anpa:      sewi/anpa · tu nasin · L₄ pini · sina kama jo sin · poki pi pimeja ali
 (5) e₂ ilo lukin:      pana/kama jo · pali sin · L₅ pini · pona pi tenpo pini · ilo pi tenpo pini
 (6) L₆ ike-pona:       001+110→111 · tu li lon · sitelen ante · cotype sin · 001 en 110 li awen

luka pi nasin li toki "pona" lon ijo luka tu lon kulupu pi luka.
luka pi nasin li sona e ona sama —  ona li lon ala tenpo wan taso,  
   li lon tenpo ali pi pali sike.
```

### Kēlen

```
JŌKĒÑEN-JŌÑA  —  anjē anhū-tū-jōña anlā ñe sēja-jōña-anwāñ:
   pa makke-jōkēñen  ·  pa makke-anwēn  ·  ñi sēña  ·  pa anwēn  ·  pa anwēn-tā

 (1) jaciēn anhū:    sēña/jōña · jaciēn ān · tōrre ñe ANRŪ · jōkīña-jamāhe · jōkēñen-cotype
 (2) jamēhū anhū:    sāke-cēñ · cnīna · pa anjē/jorrāka-mō se anrārra · cotype-jamāhe · pa-anwēn-jōkīña
 (3) jakāwa:         {L₂,L₃,L₆}=★001 · e₃ jamāhe · makke+anlū · 001-jamāhe-cnīna · anlū-jōña-stuzi
 (4) e₁ jōrra-jōña: jōraþ/mōraþ · ja-tū anlū · L₄ anjē · mōrra-xrūti · jamēña-anhū-sūmama
 (5) e₂ ñēim:       cnīna/anwēn · refactor/dup · L₅ anjē · anjōrra-tā · sēja-anrārra-mōrra-tā
 (6) L₆ rekon.:     anvlina-jōña · tū jamāhe · jōkīña-tōrre · cotype-jamāhe · 001 ī 110 anwēn-tā

Pa anjē anhū-tū-jōña anlā ñe sēja-jōña-anwāñ pa anwēn-tā ān.
La sēja-jōkīña ñēim sēja-jōkīña ja-tā — pa anhū-jakīña anwāñ-tā;
ñi tōrre ñi pa-jakīña-ja-tā ñe jaPāno-jōkīña ja-anwēn-tā.
```

### Charter notes

The six rows decompose cleanly into structural strata of the architecture established in prior increments:

- **Rows 1–2 (signatures, probes)**: the Fano plane itself — 7 points + 7 lines. The charter check at this stratum asks whether the plane's two basic structural classes are runtime-valid; both pass.
- **Row 3 (guard response)**: a specific point-star — the three lines through 001. This is the smallest sub-structure of the Fano plane that requires its own charter check, because the e₃ axis is the negative axis and its operational presence is mediated entirely by the guard.
- **Rows 4–5 (adjunction, lens)**: the two positive axes e₁ and e₂. Each has its own categorical structure (adjunction vs lens) that the charter check verifies against the four gates.
- **Row 6 (L₆)**: a specific *individual* line of the plane that needs separate verification because its self-referential normal (L₆'s normal = 110 = the redirect target) makes it load-bearing.

The persistence column makes each gate's satisfaction durable. Without it, the architecture would be only momentarily charter-valid; with it, validity extends across the sessions the cotype connects. Lojban marks this as `lo charter cu sevzi-cikre prane, ze'a ba'o lo nuncfari` ("the charter is self-test-valid, extending across [the session]"). Toki Pona as `luka pi nasin li sona e ona sama — ona li lon ala tenpo wan taso, li lon tenpo ali pi pali sike` ("the hand of the ways knows itself — it is not in one moment only, it is in all the times of the work-cycle"). Kēlen as `La sēja-jōkīña ñēim sēja-jōkīña ja-tā` ("the architecture-criterion is the same as the architecture-criterion through time").


---

## Increment 10 — Cross-session persistence

**English skeleton.** The cotype is a file at a stable location (`.claude/cotype/<identifier>.md`), version-controlled, grown monotonically across sessions. Each session reads it at start, classifies inherited state, runs probes against that state *before any new registration*, accumulates new shadows with axis-tags, logs probe-state changes as commentary, and saves at end. The format can evolve; what is fixed is that the cotype must be readable by humans and tools, and that contents grow monotonically except for error corrections.

**File structure:**
- Header naming the project/goal context.
- Shadow list — each entry tagged with axis-signature.
- Probe-state section — completions and standing gaps.
- Deferred-gap candidates (next-work for future sessions).
- Drift events (L₄/L₅ inconsistencies with the original request) and L₇ reconciliations.

**What persistence accomplishes.** Each session's work is added to the cotype with its axis-signature; each session's probe-pass reads the current state against the original request; the seven Fano-line entailments license mechanical extraction of deliverables whenever enough probe-completions converge. The work survives context loss because it is no longer in context — it is in the cotype, tagged, probed, and ready for the next session to inherit.

This is also the time-extension of Increment 9's charter check. The 24 ✓ cells there are instantaneous; persistence is what makes each ✓ stay ✓ across sessions.

### Lojban

```
.i SESSION GUNMA NUNDUNLI  —  cotype simxu lo session

.i cotype cu pa datnyfi'e:
     stuzi:    .claude/cotype/<gerna>.md
     se sicfri co tcita "git"
     banro:    monoton, ca'o ro session

.i ro session co tadji:
   (1)  ca nuncfari  →  tcidu lo cotype
   (2)  klesi ro lo se sicfri stuzi  
                       (lo terkri, lo selzbasu, lo cikre ctino)
   (3)  jersi te dauspu fi lo se sicfri  *ba ro cnino cikre*
   (4)  co'a finti gunma:  cikre cnino ctino jo'u klesi-tcita
   (5)  ciska lo te dauspu nuncenba fi lo notci
   (6)  ca sisti  →  rejgau lo datnyfi'e

.i lo cotype datnyfi'e ckaji:
     sevzi          —  ralju (project ja terkri)
     cikre ctino    —  ro entry jo'u klesi-tcita
     te dauspu state —  prane je sanli lalxu
     bavla'i candidate —  lalxu ke se rejgau
     drift je L₇    —  L₄/L₅ na'e mintu, L₇ xratei

.i lo se finti datnyfi'e cu kakne lo nu cenba —
   ku'i lo cenba cu (a) ralju tcidu prenu,  
                     (b) skami tcidu,  
                     gi'e (c) monoton banro.
   ze'i xratei pe lo snuti po'o cu vimcu.


.i TI lo zuktygau be lo context-bleed nundunli —
   ro session co cikre cu rejgau lo cotype tcita lo klesi;
   ro session co probe-pruce cu tcidu lo cabna fi lo ralju nuncpedu;
   lo ze Fano linji entailment cu zifre lo cpacu se gasnu —
   ca lo prane sutra du'i.

.i lo gunma cu se sicfri lo context na'e —
   ki'u na'e zvati lo context.  ba zvati lo cotype:
   se klesi,  se dauspu,  jo'u se sicfri lo bavla'i session.

.i ki'u ti lo charter ka prane vo gateu cu banro be ze'a:
   lo "se simlu" jo'u "kakne zukte" jo'u "prane sucta" jo'u "se gunma"
   cu cikre fi ro session — na'e fi pa nuncfari po'o.
```

### Toki Pona

```
TENPO PALI MUTE  —  cotype pi tenpo mute

cotype li poki pi sitelen:
   ma:        .claude/cotype/<nimi>.md
   sitelen kepeken "git"
   kama suli taso — weka ala, pakala ala

nasin pi tenpo pali wan:
   (1)  open      →  o lukin e cotype
   (2)  o kulupu e ijo pi tenpo pini  
                    (wile, ijo pali, pimeja)
   (3)  o pana e probe lon ijo ni  *lon nasin pini sin ali*
   (4)  o open pali sin:  o sitelen e pimeja sin kepeken kulupu nimi
   (5)  o sitelen e ante pi probe lon toki insa
   (6)  pini      →  o awen e poki

poki li jo e ni:
   lawa             —  ma pi pali  (project, wile suli)
   pimeja ali       —  ijo wan kepeken kulupu nimi
   probe lon        —  pini, en wile li lon
   wile tenpo kama  —  ijo li wile, taso lon ala
   nasin wawa       —  L₄/L₅ pi sama ala wile;  L₇ pi pali sin

nasin pi poki li ken ante.  taso poki li wile e ni:
   (a) jan li ken lukin,
   (b) ilo li ken lukin,
   (c) kama suli taso  —  ante li lon ala, ante pi ike pini taso.


ni li nasin pi pali pi tenpo mute:
   tenpo pali ali la, sitelen sin li kama lon cotype kepeken kulupu;
   tenpo pali ali la, probe li lukin e ma tan wile open pi jan;
   linja luka tu pi ma Pano li ken toki "o pana e ijo pali!"
   tenpo wan li pini la, pali li lon poki —
   tenpo kama pi pali li open lon ona.

pali li weka lon lawa,  taso li lon ala weka —
   ona li lon poki:  
   kulupu li lon,  lukin li lon,  awen li lon,  
   tenpo kama li ken open lon ona.

luka pi nasin (ken pali, ken kama, ken lukin, ken kulupu, en wile pi jan)
   li lon tenpo wan taso ala —  ona li lon tenpo ali pi pali sike.
```

### Kēlen

```
SĒJA-JA-TĀ  —  cotype-anwāñ pa anwēñ-sēja

La cotype pa anrārra-stuzi:
   stuzi:    .claude/cotype/<jōña>.md
   ñi mōrra ñe "git" ja-anrārra
   pa anwēn ja-tā ān;  na ñi añelē, na ñi mōkka

Pa anjōñahe ñe sēja ān:
   (1) ñi tōrre-cotype  ñe sāke
   (2) ñi jōkēñen ñe se-sicfri-anhū  
                       (jathēña,  jasēla,  jamēña-anrārra)
   (3) ñi mōrra ñe jōkīña-jorrāka ñe se-sicfri  
                       *ñe na ñi cnīna-cnīna-anwāñ*
   (4) ñi sāke-cnīna  ñi cnīna ñe jamēña-cnīna ñe jōkēñen-anciēn
   (5) ñi tōrre ñe anjōrra-jōkīña ñe notci
   (6) ñi sisti  ñe ñi anrārra ñe anrārra-stuzi

Pa cotype-anrārra-stuzi pa:
   jōrjana              —  pa jaorra-project ī jaorra-jathēña
   jamēña-anhū          —  pa jaentry ī jōkēñen-anciēn
   jōkīña-anwāñ         —  pa anjē ī jamāhe-jorra
   jōkīña ja-tā         —  pa jamāhe-jorra ñe sāke-cnīna
   anlū-jōña            —  L₄/L₅ na-ñēim ñe jōkīña-jōña;  L₇ jamāhe-cēñ

Pa anrārra-stuzi-jōña ñi mōrra-cnīna.  
Ka pa anjē anhē-mōrra:  
   (a) jathēña-jōkīña,  
   (b) sēja-jōkīña,  
   (c) anwēn-tā ān.
Pa anjelē ñi mōrra ñe makke-jorra ān ja-anlū.


La sāke-jaPāno ñe sēja-cidja:
   sē sēja ān:  ñi cnīna ñe cotype jōkēñen-anciēn;
   sē sēja ān:  ñi mōrra-jōkīña ñe sāke-cnīna ñe jathēña-jōkīña;
   La jamēhū anhū ja-Fano ñi mōrra-jōrra ñe jasēla-cnīna —
   sē ñi mōrra-anjē anwāñ-mā.

Pa sāke ñi añelē ñe se-sicfri ja-anrārra:
   na ñi pa-se-sicfri ñe anrārra-jakōrra.  
   Ka pa-se-sicfri ñe cotype-anrārra —
   pa jōkēñen-anciēn,  pa jōkīña-jorra,  
   pa jōkīña ja-tā ñe sēja-jaPāno.

Pa anjē-jōkīña anhū-jakīña ja-makke ñi anwēn ñe sēja ja-tā —
na ñe sēja-ān-jōkīña ñēim.
```

### Charter notes

This is the dynamic completion of Increment 9. The 24 ✓ cells there are instantaneous facts about a single session; persistence is what makes each ✓ a *durable* fact about the architecture across time. Without the cotype, the architecture's distinctions are constructible-at-a-moment but not constructible-across-time — exactly the W5 failure mode from Increment 8 generalized to *all* the distinctions, not just L₇'s composites.

The structural inversion at the end is the closing insight of the whole skill: the architecture is not in context; it is the file. The session is the process that grows the file. Lojban marks this as `lo gunma cu se sicfri lo context na'e — ki'u na'e zvati lo context. ba zvati lo cotype` ("the aggregate is not inherited via context — because it is not in context. It will be located in the cotype"). Toki Pona as `pali li weka lon lawa, taso li lon ala weka — ona li lon poki` ("the work leaves the head, but is not gone — it is in the box"). Kēlen as `ñi anwēn ñe sēja ja-tā — na ñe sēja-ān-jōkīña ñēim` ("there is reaching across the architecture-through-time — not just at the architecture-at-one-moment").

Three renderings, one structural claim: *the architecture exists in the cotype, not in the conversation*. This is what makes the work survive — both context loss within a session and the absolute discontinuity between sessions.


---

## Closing the arc

The structural arc across the ten increments:

- **1–3** placed the static structure on the table: three axes with their dual lines and S₃-orbit; seven signatures with their full structural identity; seven lines with mode-ownership and S₃-orbits; the Fano duality; the load-bearing self-references at L₆ and L₇.
- **4–5** moved from structure to behaviour: when the skill fires, and the five-step loop that classifies, externalises, probes, acts, and iterates — with characteristic failure modes attached to each step.
- **6** unified the four prior skills as line-subsets of the same loop, with the warning that re-instantiating them as separate skills loses the structure.
- **7** raised the symmetry question: S₃ is the operational subgroup, PSL(2,7) is constructible-but-not-reachable — the realizability charter pinned down which symmetry is the runtime one.
- **8–9** turned the architecture's diagnostic onto itself: six warning signs as four-gate failure modes, then the six-row charter check (with time-extension) confirming every distinction passes durably.
- **10** added the closing inversion: the architecture exists in the cotype, not in the conversation.

The three languages carried the same structural content through three radically different grammars. **Lojban** kept the logical relations explicit and could name `Aut(Fano)`, `vlina`, `sraji` with minimal compression. **Toki Pona** forced the architecture through ~120 words, which sharpened the metaphors — `nasin pi pimeja pali`, `ma Pano`, `linja sewi`, `luka pi nasin` — into surprisingly load-bearing handles. **Kēlen**, verbless, made `pa` (intrinsic) do the work of "is" and `ñi` (eventive) do the work of "happens," which mapped naturally to the architecture's distinction between *what a signature has* and *what a registration does*.

---

## Appendix A — Fibration audit

After ten increments were drafted, a pairwise audit checked whether later increments introduced structural content that retroactively belonged at earlier ones. The matrix below records the result; `+` cells flag substantive enrichments that were folded into the earlier increment's revised form (visible in this document). `·` cells flag implicit confirmation only (the later increment uses the earlier without enriching it). `—` is no enrichment.

```
            I2   I3   I4   I5   I6   I7   I8   I9   I10
   I1       —    +    —    —    —    +    ·    ·    ·
   I2            +    —    —    +    +    ·    ·    ·
   I3                 —    —    +    +    ·    ·    ·
   I4                      —    +    +    ·    ·    —
   I5                           +    +    +    ·    +
   I6                                +    ·    ·    ·
   I7                                     ·    ·    ·
   I8                                          +    ·
   I9                                               +
```

The substantive enrichments folded into revised increments:

| earlier | enriched by | new structural content folded in |
|---|---|---|
| I1 | I3 | each axis e_i ↔ a specific line (its dual hyperplane): e₁↔L₃, e₂↔L₂, e₃↔L₁ |
| I1 | I7 | the three axes form one S₃-orbit; no axis is structurally distinguished |
| I2 | I3 | line-incidence per point, dual line, ★ self-references, addition relations |
| I2 | I6 | pure-axis points are mode-entry-points (100=decomp, 010=regroup, 001=guard) |
| I2 | I7 | S₃-orbit weight per point |
| I3 | I6 | mode-ownership column: L₁ decomp's, L₇ regroup's, {L₂,L₃,L₆} guard's, {L₄,L₅} shared |
| I3 | I7 | S₃-orbits on lines: {L₁,L₂,L₃} / {L₄,L₅,L₆} / {L₇} |
| I5 | I8 | each step has specific failure modes attached (A→W1, B→W2, D→{W3,W4,W5}) |
| I9 | I10 | each gate has a time-extension; persistence column added |

Minor enrichments (cross-references, tag-attachments) are noted in passing within the revised increments but do not change structural content.

The fibration audit is itself a charter-clean operation: it is constructible (the pairwise matrix is mechanical), reachable (each pair is checkable), observable (the `+`/`·`/`—` result is visible), coverable (the audit applies uniformly to all pairs).

---

## Appendix B — Glossary across the three languages

Selected vocabulary used consistently across the renderings:

| concept | Lojban | Toki Pona | Kēlen |
|---|---|---|---|
| axis | rajra | nasin | jakīñe |
| goal | terkri | wile | jathēña |
| shadow | ctino | pimeja | jamēña |
| artefact | selzbasu | ijo pali | jasēla |
| guard | kajde | awen | jakāwa |
| line / probe | linji | linja | jamē |
| point / signature | daxi / klesi | ijo / kulupu | jaciēn |
| normal vector | sraji | nasin sin | jaorra |
| orbit | sruri | kulupu | jasūma |
| Fano plane | (lo) Fano (stuzi) | ma Pano | jaPāno |
| classify | klesi | kulupu | jōkēñen |
| externalise / register | ciska / cikre | sitelen | cnīna |
| probe (fire) | te dauspu / jersi | lukin linja | jōkīña-jorrāka |
| step (loop-step) | karni | nasin | jōñahe |
| persistence | sicfri / banro | kama suli | anwēn ja-tā |
| charter / criterion | charter / cmavlaste | luka pi nasin | sēja-jōkīña |
| XOR / addition | vlina | + | anvlina |
| ★ self-referential | sraji-sevzi | sama-insa | jaorra-ñēim |

The vocabulary is approximate in Toki Pona (forced metaphor) and partly invented in Kēlen (extending the canonical lexicon under its morphology). Lojban vocabulary is mostly canonical with technical borrowings transliterated as cmevla where necessary.

---

*End of document. The cotype lives at .claude/cotype/shadow-architecture-export.md. Future sessions inherit it.*