"""Zemí - chapter retrieval for the lector's slips.

Two legs over the same passage windows, fused per document:
  1. lexical: BM25 weights precomputed per (term, window), stored as uint8 in a term-major CSR;
     a query is a bincount over the posting lists of its terms.
  2. dense: a small int8 ONNX sentence encoder embeds the query; passage vectors (int8) were
     embedded offline. Cosine similarity against every window.
A document scores as its best window in each leg; the two document scores are z-normalised and
mixed with weights from config.json.

index/ layout (written by build/build_index.py):
    config.json   tokenizer settings, BM25 scale, encoder settings, fusion weights
    docs.json     document ids, in document-number order
    win_doc.npy   int32 window -> document number (windows of a document are contiguous)
    vocab.txt     one stemmed term per line (line number = term id)
    postings.npz  indptr (uint32), win (uint16/uint32), imp (uint8)
    vectors.npy   uint8 (n_windows, dim/2), 4-bit codes of the L2-normalised passage vectors
    vec_step.npy  float32 (dim,), quantisation step per dimension
    encoder.onnx  int8 sentence encoder; tokenizer.json next to it
"""
from __future__ import annotations

import json
import os
import re
import unicodedata

import numpy as np

STOP = frozenset("""a an the of and or to in on at by for from with as is are was were be been being this that these those it
its into than then there their they them he she his her we you not no but if so such which who whom whose what when where why
how all any each more most other some very can could would should may might will do does did have has had about over under
between through during before after i me my our your us also just only own same too s t""".split())

# Spanish words the slips mix in, mapped to the English the corpus uses.
SPANISH = {
    "ano": "year", "anos": "years", "guerra": "war", "iglesia": "church", "gente": "people", "mujeres": "women",
    "mujer": "woman", "hombres": "men", "hombre": "man", "historia": "history", "capitulo": "chapter",
    "parte": "part", "donde": "where", "eso": "that", "espanoles": "spaniards", "espanol": "spanish",
    "ciudad": "city", "pueblo": "town", "rio": "river", "isla": "island", "azucar": "sugar", "tabaco": "tobacco",
    "esclavos": "slaves", "esclavo": "slave", "rey": "king", "barco": "ship", "barcos": "ships", "puerto": "port",
    "dinero": "money", "tierra": "land", "agua": "water", "nino": "child", "ninos": "children", "casa": "house",
    "calle": "street", "libro": "book", "musica": "music", "fiesta": "festival", "muerte": "death",
}
# Spanish function words in a slip carry nothing; dropped from queries only (names keep them in the corpus).
SPANISH_STOP = frozenset("de la el los las del y en que por para con sobre un una lo al se su sus".split())
WORD = re.compile(r"[a-z0-9]+")


def fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


class Analyzer:
    """Text -> stemmed terms. Used verbatim at build time (build/ imports this file)."""

    def __init__(self, spanish: bool = True):
        import Stemmer

        self.stem = Stemmer.Stemmer("english").stemWord
        self.spanish = spanish
        self.cache: dict[str, str] = {}

    def terms(self, text: str, query: bool = False) -> list[str]:
        out = []
        for w in WORD.findall(fold(text)):
            if query and self.spanish:
                if w in SPANISH_STOP:
                    continue
                if w in SPANISH:  # keep the word (it may be a name) and add its English meaning
                    out.append(self._stem(SPANISH[w]))
            if w in STOP or (len(w) < 2 and not w.isdigit()):
                continue
            out.append(self._stem(w))
        return out

    def _stem(self, w: str) -> str:
        s = self.cache.get(w)
        if s is None:
            s = self.cache[w] = self.stem(w)
        return s


def _softmax_free_mean(hidden: np.ndarray, mask: np.ndarray) -> np.ndarray:
    m = mask[..., None].astype(np.float32)
    return (hidden * m).sum(1) / np.maximum(m.sum(1), 1e-9)


class Retriever:
    def __init__(self, index_dir: str) -> None:
        p = lambda name: os.path.join(index_dir, name)  # noqa: E731
        with open(p("config.json"), encoding="utf-8") as fh:
            self.cfg = json.load(fh)
        with open(p("docs.json"), encoding="utf-8") as fh:
            self.doc_ids = json.load(fh)
        self.win_doc = np.load(p("win_doc.npy"))
        self.n_win = len(self.win_doc)
        self.n_doc = len(self.doc_ids)
        # first window of each document, for reduceat
        self.doc_start = np.flatnonzero(np.r_[True, self.win_doc[1:] != self.win_doc[:-1]]).astype(np.int64)
        with open(p("vocab.txt"), encoding="utf-8") as fh:
            self.vocab = {t: i for i, t in enumerate(fh.read().split("\n"))}
        post = np.load(p("postings.npz"))
        self.indptr = post["indptr"].astype(np.int64)
        self.win = post["win"]
        self.imp = post["imp"]
        self.analyzer = Analyzer(self.cfg.get("spanish", True))
        self.fuse = self.cfg["fusion"]

        enc = self.cfg.get("encoder")
        self.session = None
        if enc:
            import onnxruntime as ort
            from tokenizers import Tokenizer

            so = ort.SessionOptions()
            so.intra_op_num_threads = 1
            so.inter_op_num_threads = 1
            so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            self.session = ort.InferenceSession(p("encoder.onnx"), so, providers=["CPUExecutionProvider"])
            self.input_names = {i.name for i in self.session.get_inputs()}
            self.tok = Tokenizer.from_file(p("tokenizer.json"))
            self.tok.enable_truncation(enc.get("max_len", 96))
            self.tok.no_padding()
            self.enc = enc
            packed = np.load(p("vectors.npy"))  # uint8 (n_windows, dim/2): two 4-bit codes per byte
            table = np.array([[b >> 4, b & 15] for b in range(256)], dtype=np.float32)
            self.vectors = table[packed].reshape(len(packed), -1)
            self.step = np.load(p("vec_step.npy")).astype(np.float32)
            self.embed("warm up")

    # -- legs -------------------------------------------------------------
    def lexical(self, query: str) -> np.ndarray:
        ids = [self.vocab[t] for t in dict.fromkeys(self.analyzer.terms(query, query=True)) if t in self.vocab]
        if not ids:
            return np.zeros(self.n_win, dtype=np.float32)
        sl = [slice(self.indptr[i], self.indptr[i + 1]) for i in ids]
        wins = np.concatenate([self.win[s] for s in sl])
        imps = np.concatenate([self.imp[s] for s in sl]).astype(np.float32)
        return np.bincount(wins, weights=imps, minlength=self.n_win).astype(np.float32)

    def embed(self, query: str) -> np.ndarray:
        e = self.tok.encode(self.enc.get("query_prefix", "") + query)
        ids = np.asarray([e.ids], dtype=np.int64)
        mask = np.asarray([e.attention_mask], dtype=np.int64)
        feed = {"input_ids": ids, "attention_mask": mask}
        if "token_type_ids" in self.input_names:
            feed["token_type_ids"] = np.zeros_like(ids)
        hidden = self.session.run(None, feed)[0]
        if hidden.ndim == 3:
            v = hidden[0, 0] if self.enc.get("pooling") == "cls" else _softmax_free_mean(hidden, mask)[0]
        else:
            v = hidden[0]
        v = v.astype(np.float32)
        return v / (np.linalg.norm(v) + 1e-9)

    def dense(self, query: str) -> np.ndarray:
        # dequantised vector = codes * step + lo; the lo term adds the same constant to every window
        return self.vectors @ (self.step * self.embed(query))

    # -- ranking ----------------------------------------------------------
    @staticmethod
    def _z(x: np.ndarray) -> np.ndarray:
        s = x.std()
        return (x - x.mean()) / s if s > 0 else x * 0.0

    def doc_scores(self, query: str) -> np.ndarray:
        f = self.fuse
        lex_doc = np.maximum.reduceat(self.lexical(query), self.doc_start)
        score = f.get("w_lex", 1.0) * self._z(lex_doc)
        if self.session is not None and f.get("w_dense", 0) > 0:
            dense_doc = np.maximum.reduceat(self.dense(query), self.doc_start)
            score = score + f["w_dense"] * self._z(dense_doc)
        return score

    def search(self, query: str, k: int = 3) -> list[str]:
        s = self.doc_scores(query)
        k = min(k, self.n_doc)
        top = np.argpartition(-s, k - 1)[:k]
        top = top[np.argsort(-s[top], kind="stable")]
        return [self.doc_ids[i] for i in top]
