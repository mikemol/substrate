import re
import random

class CoxeterTypeclass:
    """
    The Symbolic Guardrail. 
    Implements a Rank-3 Coxeter group with generators {s1, s2, s3}.
    Relations: s_i^2 = 1, (s1 s2)^3 = 1, (s2 s3)^3 = 1, (s1 s3)^2 = 1.
    """
    def __init__(self):
        # We represent words as strings of numbers for easy regex reduction. 
        # e.g., state [s2, s1] -> "21"
        self.relations = [
            # s_i^2 = 1 (Reflections cancel themselves out)
            ("11", ""), ("22", ""), ("33", ""),
            # (s1 s2)^3 = 1 -> 121212 cancels to identity
            ("121212", ""), ("212121", ""),
            # (s2 s3)^3 = 1
            ("232323", ""), ("323232", ""),
            # (s1 s3)^2 = 1 (Commuting generators)
            ("1313", ""), ("3131", "")
        ]

    def reduce_word(self, word: list[str]) -> list[str]:
        """Applies virtuous circularity. Compresses the state to its canonical form."""
        if not word: return []
        
        # Convert list ['s2', 's1'] to string "21"
        w_str = "".join([s.replace('s', '') for s in word])
        
        reduced = False
        while not reduced:
            reduced = True
            for pattern, replacement in self.relations:
                if pattern in w_str:
                    w_str = w_str.replace(pattern, replacement)
                    reduced = False # Continue checking until no relations apply
                    
        # Convert string "21" back to list ['s2', 's1']
        return [f"s{char}" for char in w_str]

class NeuralHeuristic:
    """
    The Continuous Unfolder (Toy Version).
    In a real system, this is an NN predicting the next generator.
    Here, it's a heuristic mapping user input to a geometric direction.
    """
    def predict_generator(self, text: str) -> str:
        text = text.lower()
        if "?" in text:
            return "s1" # Invert (Questioning stance)
        elif any(w in text for w in ["feel", "think", "sad", "happy", "am"]):
            return "s3" # Probe (Emotional/Internal stance)
        else:
            return "s2" # Broaden (Categorical stance)

class ProceduralGenerator:
    """
    Maps the coherentist state chamber (the reduced word) to language.
    """
    def __init__(self):
        self.responses = {
            "": "I am ready to listen. Tell me more.",
            "s1": "Why do you ask that?",
            "s2": "Let's zoom out. How does this fit into the bigger picture?",
            "s3": "How does that make you feel deep down?",
            "s2s1": "But fundamentally, what is the core question you are asking?",
            "s1s3": "Are you questioning your own feelings about this?",
            "s3s2": "If we look at everyone else, do they feel the same way?",
            # A fallback for other valid combinatorial chambers
            "default": "I see. Let's shift our perspective. Go on."
        }

    def generate(self, state_word: list[str]) -> str:
        word_key = "".join(state_word)
        return self.responses.get(word_key, self.responses["default"])

class CoalgebraicELIZA:
    def __init__(self):
        self.typeclass = CoxeterTypeclass()
        self.nn = NeuralHeuristic()
        self.generator = ProceduralGenerator()
        self.current_state = []
        self.turn = 1

    def chat(self, user_input: str):
        print(f"\n--- Turn {self.turn} ---")
        
        # 1. Neural Prediction (Anamorphism)
        s_i = self.nn.predict_generator(user_input)
        print(f"[NN] Selected Generator: {s_i}")
        
        # 2. Append to state
        unreduced_state = self.current_state + [s_i]
        print(f"[Math] Unreduced Word: {'*'.join(unreduced_state) if unreduced_state else 'Identity'}")
        
        # 3. Apply Coxeter Relations
        self.current_state = self.typeclass.reduce_word(unreduced_state)
        print(f"[Math] Reduced Chamber: {'*'.join(self.current_state) if self.current_state else 'Identity (Origin)'}")
        
        # 4. Procedural Generation
        response = self.generator.generate(self.current_state)
        self.turn += 1
        return response

# --- Run the Loop ---
if __name__ == "__main__":
    eliza = CoalgebraicELIZA()
    print("ELIZA: I am ready to listen. Tell me more.")
    
    while True:
        user_text = input("User: ")
        if user_text.lower() in ['quit', 'exit']:
            break
        reply = eliza.chat(user_text)
        print(f"ELIZA: {reply}")