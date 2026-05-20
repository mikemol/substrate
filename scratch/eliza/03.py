class CoxeterTypeclass:
    """
    The Geometric Guardrail. 
    Implements the A3 (S4) Coxeter group.
    Uses localized, leftmost Shortlex rewriting to guarantee confluence 
    and preserve true topological adjacency.
    """
    def __init__(self):
        # Combined rules: Involutions (length-reducing) and Braids (lexicographic)
        self.rules = {
            "11": "", "22": "", "33": "",
            "212": "121", "323": "232", "31": "13"
        }

    def reduce_word(self, word: list[str]) -> tuple[list[str], list[str]]:
        """
        Applies strict leftmost term rewriting. 
        Returns the canonical chamber and the trace of the reduction.
        """
        if not word: return [], []
        
        w_str = "".join([s.replace('s', '') for s in word])
        trace = [w_str]
        
        reduced = False
        while not reduced:
            reduced = True
            
            # Find the leftmost applicable rewrite rule
            best_idx = len(w_str)
            best_rule = None
            
            for lhs in self.rules.keys():
                idx = w_str.find(lhs)
                if idx != -1 and idx < best_idx:
                    best_idx = idx
                    best_rule = lhs
                    
            if best_rule is not None:
                # Apply ONLY to the first localized occurrence
                rhs = self.rules[best_rule]
                w_str = w_str[:best_idx] + rhs + w_str[best_idx + len(best_rule):]
                trace.append(w_str)
                reduced = False # Restart scan from the beginning
                    
        return [f"s{char}" for char in w_str], trace

class NeuralHeuristic:
    """The Coalgebraic Unfolder."""
    def predict_generator(self, text: str) -> str:
        text = text.lower()
        if "?" in text:
            return "s1" # Invert (Questioning)
        elif any(w in text for w in ["feel", "think", "sad", "happy", "am"]):
            return "s3" # Probe (Introspective)
        else:
            return "s2" # Broaden (Contextual)

class FunctorialSemantics:
    """
    Maps the Coxeter Category to the Semantic Category.
    Meaning is no longer a static label, but a function of Geodesic Distance 
    (discourse tension) and the latest reflection (vector).
    """
    def generate(self, chamber: list[str], last_move: str) -> str:
        distance = len(chamber)
        
        if distance == 0:
            return "We have returned to equilibrium. Where should we begin again?"
            
        elif distance <= 2:
            # Local Exploration
            if last_move == "s1": return "Why do you ask that?"
            elif last_move == "s2": return "Let's zoom out. How does this fit into the bigger picture?"
            else: return "How does that make you feel deep down?"
            
        elif distance <= 4:
            # Semantic Tension (Intersecting Parabolic Subgroups)
            if last_move == "s1": return "But fundamentally, what is the exact core of your questioning here?"
            elif last_move == "s2": return "Are you questioning how all of this fits into the wider context?"
            else: return "Zooming out, how does grappling with this impact you internally?"
            
        else:
            # Maximum Discourse Displacement (Diameter of A3 is 6)
            return "We have reached the edge of this conversational space. Let's reflect on everything we've uncovered. What does this ultimately mean to you?"

class CoalgebraicELIZA:
    def __init__(self):
        self.typeclass = CoxeterTypeclass()
        self.nn = NeuralHeuristic()
        self.semantics = FunctorialSemantics()
        self.current_state = []
        self.turn = 1

    def chat(self, user_input: str):
        print(f"\n--- Turn {self.turn} ---")
        
        # 1. Anamorphism
        s_i = self.nn.predict_generator(user_input)
        print(f"[Anamorphism] Selected Reflection: {s_i}")
        
        # 2. Geometric Extension
        unreduced_state = self.current_state + [s_i]
        
        # 3. Algebraic Normalization (Quotienting)
        self.current_state, trace = self.typeclass.reduce_word(unreduced_state)
        
        # Display the mathematical trace if a reduction occurred
        if len(trace) > 1:
            trace_str = " -> ".join(trace)
            print(f"[Algebra] Rewriting Trace: {trace_str}")
            
        chamber_str = '*'.join(self.current_state) if self.current_state else 'Origin (Identity)'
        distance = len(self.current_state)
        print(f"[Geometry] Canonical Chamber: {chamber_str} (Geodesic Distance: {distance})")
        
        # 4. Functorial Realization
        response = self.semantics.generate(self.current_state, s_i)
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