from dataclasses import dataclass

from util import PhraseTuple

@dataclass
class Align:
    order: int
    sentence: PhraseTuple
    target: PhraseTuple 
    sim: float

    def __hash__(self):
        return hash((self.order, self.sentence))


class Aligner:
    def __init__(self, aligns: dict={}):
        self._aligns = aligns

    def __len__(self):
        return len(self._aligns)

    def __getitem__(self, k):
        return self._aligns[k]

    def __setitem__(self, k, v: PhraseTuple):
        self._aligns[k] = v

    def __iter__(self):
        return self._aligns.values().__iter__()

    def __next__(self):
        return self._aligns.values().__next__()

    def __contains__(self, s):
        return hash(s) in [hash(k) for k in self._aligns.keys()]

    def __str__(self):
        return self._aligns.__str__()
