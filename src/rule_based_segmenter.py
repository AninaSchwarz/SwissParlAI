"""
rule_based_segmenter.py
-----------------------
Rule-based segmenter using NLTK TextTiling.
Language-agnostic: works on DE, FR, IT, EN without language-specific models.

TextTiling detects topic shifts via lexical cohesion drops — conceptually
equivalent to what the LLM segmenter does, making IAA comparison meaningful.
"""

import re
import logging
from typing import List

import nltk
from nltk.tokenize import TextTilingTokenizer

# Download required NLTK data if not present
nltk.download("stopwords", quiet=True)

logger = logging.getLogger(__name__)


def split_sentences(text: str) -> List[str]:
    """
    Language-agnostic sentence splitter using punctuation regex.
    Handles DE, FR, IT, EN without requiring language-specific models.
    Splits on [.!?] followed by whitespace + uppercase letter.
    """
    # Clean [NB] artifacts from the transcript
    text = re.sub(r"\[NB\]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Split on sentence-ending punctuation
    pattern = r'(?<=[.!?])\s+(?=[A-ZÁÀÂÄÉÈÊËÎÏÓÒÔÖÚÙÛÜÇÑ])'
    parts = re.split(pattern, text)
    sentences = [s.strip() for s in parts if s.strip()]

    # Fallback: if no splits found, return full text as one sentence
    return sentences if sentences else [text]


class RuleBasedSegmenter:
    """
    Segments parliamentary speech transcripts using NLTK TextTiling.

    TextTiling parameters:
        w  — pseudo-sentence size in tokens (default 20).
             Smaller = more sensitive to local shifts.
        k  — block size for cohesion comparison (default 10).
             Larger = smoother, fewer segments.

    For median-length speeches (~550 words), w=20 / k=10 is a good baseline.
    Tune if results are over- or under-segmented.
    """

    def __init__(self, w: int = 20, k: int = 10):
        self.w = w
        self.k = k
        self.tokenizer = TextTilingTokenizer(w=w, k=k)

    def segment(self, text: str) -> List[str]:
        """
        Takes a raw transcript string.
        Returns a list of segment strings.
        Falls back to [text] if TextTiling fails (e.g. text too short).
        """
        # Clean artifacts
        clean = re.sub(r"\[NB\]", " ", text)
        clean = re.sub(r"\s+", " ", clean).strip()

        # TextTiling needs double-newline paragraph breaks to work well.
        # We inject them at sentence boundaries so it has structure to work with.
        sentences = split_sentences(clean)

        if len(sentences) < 3:
            # Too short to segment meaningfully
            return [clean]

        # Re-join with double newlines so TextTiling sees paragraph structure
        prepared = "\n\n".join(sentences)

        try:
            segments = self.tokenizer.tokenize(prepared)
            # Strip extra whitespace from each segment
            segments = [s.strip() for s in segments if s.strip()]
            return segments if segments else [clean]
        except ValueError as e:
            # TextTiling raises ValueError when text is too short
            logger.warning(f"TextTiling fallback (text too short or uniform): {e}")
            return [clean]
        except Exception as e:
            logger.warning(f"TextTiling unexpected error: {e}")
            return [clean]


if __name__ == "__main__":
    # Quick smoke test
    sample = (
        "Künstliche Intelligenz verändert unsere Gesellschaft grundlegend. "
        "Wir müssen sicherstellen, dass diese Technologie zum Wohl aller eingesetzt wird. "
        "Die Regulierung muss Schritt halten mit der Entwicklung. "
        "Gleichzeitig dürfen wir Innovation nicht behindern. "
        "Der Bundesrat hat einen Bericht vorgelegt. "
        "Dieser Bericht zeigt die Chancen und Risiken auf. "
        "Wir begrüssen diese Initiative ausdrücklich. "
        "Es gibt jedoch noch viele offene Fragen. "
        "Insbesondere der Datenschutz muss gewährleistet sein. "
        "Bürgerinnen und Bürger haben ein Recht auf Transparenz. "
        "Algorithmen dürfen nicht diskriminieren. "
        "Die Kommission wird dieses Thema weiter verfolgen."
    )
    segmenter = RuleBasedSegmenter()
    result = segmenter.segment(sample)
    print(f"Segments found: {len(result)}")
    for i, seg in enumerate(result, 1):
        print(f"\n[{i}] {seg[:120]}...")