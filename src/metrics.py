"""Olasılık tahmini ölçütleri."""
import numpy as np


def implied(oH, oD, oA):
    """Oranlardan marjı (vig) orantısal olarak çıkarıp 'adil' olasılık üretir."""
    inv = np.column_stack([1 / oH, 1 / oD, 1 / oA])
    return inv / inv.sum(1, keepdims=True)


def outcome(hg, ag):
    return np.where(hg > ag, 0, np.where(hg == ag, 1, 2))


def brier(P, y):
    Y = np.eye(3)[y]
    return ((P - Y) ** 2).sum(1).mean()


def logloss(P, y):
    return -np.log(np.clip(P[np.arange(len(y)), y], 1e-12, 1)).mean()


def rps(P, y):
    Y = np.eye(3)[y]
    return (((np.cumsum(P, 1) - np.cumsum(Y, 1)) ** 2)[:, :2].sum(1) / 2).mean()
