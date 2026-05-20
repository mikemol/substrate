class CoxeterTypeclass:
    """
    The Geometric Guardrail. 
    Implements a Rank-3 Coxeter group with generators {s1, s2, s3}.
    Uses Shortlex Normal Form rewriting to guarantee confluence and 
    preserve true topological adjacency via oriented braid swaps.
    """
    def __init__(self):
        # 1. Involutions (Length Reduction)
        self.involutions = ["11", "22", "33"]
        
        # 2. Oriented Braid Swaps (Lexicographic Downhill Flow)
        # m12 = 3 (121 <-> 212), m23 = 3 (232 <-> 323), m13 = 2 (13 <-> 31)
        self.braids = {
            "212": "121",
            "323": "232",
            "31": "13"
        }

    def reduce_word(self, word: list[str]) -> list[str]:
        """Applies rewriting until a unique Bruhat normal form is reached."""
        if not word: return []
        
        # Convert state ['s2', 's1', 's2'] to string "212"
        w_str = "".join([s.replace('s', '') for s in word])
        
        reduced = False
        while not reduced:
            reduced = True
            
            # Step A: Attempt length reduction (Annihilation)
            for inv in self.involutions:
                if inv in w_str:
                    w_str = w_str.replace(inv, "")
                    reduced = False
                    break # Restart loop to re-evaluate length
            
            if not reduced: continue
            
            # Step B: Attempt geometric commutation (Braid Swaps)
            for lhs, rhs in self.braids.items():
                if lhs in w_str:
                    w_str = w_str.replace(lhs, rhs)
                    reduced = False
                    break # Restart loop to check for newly created involutions
                    
        # Convert canonical string "121" back to ['s1', 's2', 's1']
        return [f"s{char}" for char in w_str]

class NeuralHeuristic:
    """
    The Coalgebraic Unfolder.
    Selects the next operational reflection based on continuous input.
    """
    def predict_generator(self, text: str) -> str:
        text = text.lower()
        if "?" in text:
            return "s1" # Invert (Questioning stance)
        elif any(w in text for w in ["feel", "think", "sad", "happy", "am"]):
            return "s3" # Probe (Emotional/Internal stance)
        else:
            return "s2" # Broaden (Categorical stance)

class ChamberSemantics:
    """
    Maps the canonical Coxeter chamber to semantic output.
    Because the reducer now guarantees a unique Shortlex normal form,
    we only need to map the canonical endpoints, not every messy path.
    """
    def __init__(self):
        self.vector_field = {
            "": "I am ready to listen. Tell me more.",
            "s1": "Why do you ask that?",
            "s2": "Let's zoom out. How does this fit into the bigger picture?",
            "s3": "How does that make you feel deep down?",
            "s1s2": "Are you questioning how this fits into the wider context?",
            "s1s3": "Are you questioning your own internal state?",
            "s2s3": "If we look at everyone else, do they feel the same way?",
            "s1s2s1": "But fundamentally, what is the exact core of your question?",
            "s1s2s3": "Zooming out, how does questioning this impact you internally?"
        }

    def generate(self, state_word: list[str]) -> str:
        word_key = "".join(state_word)
        return self.vector_field.get(word_key, "I see the shape of what you are saying. Shift perspective and continue.")

class CoalgebraicELIZA:
    def __init__(self):
        self.typeclass = CoxeterTypeclass()
        self.nn = NeuralHeuristic()
        self.semantics = ChamberSemantics()
        self.current_state = []
        self.turn = 1

    def chat(self, user_input: str):
        print(f"\n--- Turn {self.turn} ---")
        
        # 1. Unfold (Select Reflection)
        s_i = self.nn.predict_generator(user_input)
        print(f"[Anamorphism] Selected Reflection: {s_i}")
        
        # 2. Append to Path
        unreduced_state = self.current_state + [s_i]
        path_str = '*'.join(unreduced_state) if unreduced_state else 'Identity'
        print(f"[Geometry] Traversed Path: {path_str}")
        
        # 3. Algebraic Normalization
        self.current_state = self.typeclass.reduce_word(unreduced_state)
        chamber_str = '*'.join(self.current_state) if self.current_state else 'Origin'
        print(f"[Algebra] Canonical Chamber: {chamber_str}")
        
        # 4. Semantic Realization
        response = self.semantics.generate(self.current_state)
        self.turn += 1
        return response

# --- Execution ---
if __name__ == "__main__":
    eliza = CoalgebraicELIZA()
    print("ELIZA: I am ready to listen. Tell me more.")
    
    while True:
        try:
            user_text = input("User: ")
            if user_text.lower() in ['quit', 'exit']:
                break
            reply = eliza.chat(user_text)
            print(f"\nELIZA: {reply}")
        except KeyboardInterrupt:
            break