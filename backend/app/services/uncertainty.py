"""
Active uncertainty quantification for Human-in-the-Loop triage.
"""

import math
from typing import List, Dict, Any, Tuple

def calculate_shannon_entropy(probabilities: List[float]) -> float:
    """
    Computes normalized Shannon entropy across class prediction distribution:
    H(p) = -sum(p_i * log2(p_i)) / log2(C)
    """
    if not probabilities or len(probabilities) <= 1:
        return 0.0
    
    # Filter non-zero
    valid_probs = [p for p in probabilities if p > 1e-7]
    if not valid_probs:
        return 0.0

    entropy = -sum(p * math.log2(p) for p in valid_probs)
    max_entropy = math.log2(len(probabilities))
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
    return min(1.0, max(0.0, normalized_entropy))

def evaluate_detection_uncertainty(
    confidence: float,
    class_probs: List[float] = None,
    uncertainty_threshold: float = 0.35
) -> Tuple[float, bool]:
    """
    Assesses uncertainty score and determines whether sample should be routed
    to the Human-in-the-Loop review queue.
    """
    if class_probs and len(class_probs) > 1:
        entropy = calculate_shannon_entropy(class_probs)
    else:
        # Proxy uncertainty from confidence distance from certainty
        # Confidence near 0.5 has maximum uncertainty; confidence near 1.0 has minimal
        entropy = max(0.0, min(1.0, 2.0 * (1.0 - confidence)))

    # Composite uncertainty score
    uncertainty_score = round(entropy, 4)
    flagged = (uncertainty_score > uncertainty_threshold) or (confidence < 0.65)
    return uncertainty_score, flagged

