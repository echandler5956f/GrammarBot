# backend/ml.py

import torch
import difflib
from transformers import (
    T5Tokenizer, T5ForConditionalGeneration,
    AutoTokenizer, AutoModelForSequenceClassification
)
from typing import List, Tuple

class GrammarCorrector:
    def __init__(
        self,
        correction_model_name: str = "vennify/t5-base-grammar-correction",
        classification_model_name: str = "typeform/distilbert-base-uncased-mnli"
    ):
        # Grammar Correction Model
        self.correction_tokenizer = T5Tokenizer.from_pretrained(correction_model_name)
        self.correction_model = T5ForConditionalGeneration.from_pretrained(correction_model_name)
        self.correction_model.eval()

        # Error Classification Model
        self.classification_tokenizer = AutoTokenizer.from_pretrained(classification_model_name)
        self.classification_model = AutoModelForSequenceClassification.from_pretrained(classification_model_name)
        self.classification_model.eval()

        # Example labels (you would replace these with your own if your model is custom-trained)
        self.error_labels = [
            "Spelling Error",
            "Punctuation Error",
            "Verb Tense Error",
            "Determiner Error",
            "Other Grammar Error"
        ]

        # Move models to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.correction_model.to(self.device)
        self.classification_model.to(self.device)

    def correct_text(self, text: str) -> str:
        input_ids = self.correction_tokenizer.encode("grammar: " + text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            output_ids = self.correction_model.generate(
                input_ids,
                max_length=128,
                num_beams=4,
                early_stopping=True
            )
        corrected_text = self.correction_tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return corrected_text

    def get_error_spans(self, original_text: str, corrected_text: str) -> List[Tuple[str, str]]:
        original_tokens = original_text.split()
        corrected_tokens = corrected_text.split()

        sm = difflib.SequenceMatcher(None, original_tokens, corrected_tokens)
        diffs = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                o_span = " ".join(original_tokens[i1:i2])
                c_span = " ".join(corrected_tokens[j1:j2])
                if o_span.strip() or c_span.strip():
                    diffs.append((o_span, c_span))
        return diffs

    def classify_error(self, original_span: str, corrected_span: str) -> str:
        combined_text = f"Original: {original_span} | Corrected: {corrected_span}"
        inputs = self.classification_tokenizer(
            combined_text, return_tensors="pt", truncation=True, max_length=64
        ).to(self.device)

        with torch.no_grad():
            logits = self.classification_model(**inputs).logits

        predicted_label_id = torch.argmax(logits, dim=1).cpu().item()

        if predicted_label_id < len(self.error_labels):
            return self.error_labels[predicted_label_id]
        else:
            return "Other Grammar Error"

    def analyze_text(self, text: str) -> dict:
        corrected = self.correct_text(text)
        diffs = self.get_error_spans(text, corrected)
        results = []
        for orig_span, corr_span in diffs:
            if orig_span.strip() == corr_span.strip():
                continue
            e_type = self.classify_error(orig_span, corr_span)
            results.append({
                "original_span": orig_span,
                "corrected_span": corr_span,
                "error_type": e_type
            })
        return {
            "corrected_text": corrected,
            "errors": results
        }