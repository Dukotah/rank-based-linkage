"""Page-similarity graph for the unsolved Liber Primus (Cicada 3301) pages.

Each page is summarised by its distribution over the 29 runes of the Gematria
Primus. The weight of the undirected edge {p, q} is the Jensen-Shannon
divergence (bits) between the two distributions, so lower weight means more
similar: rbl.jar mode Ul.

With --shuffle SEED, all runes of the book are pooled, shuffled, and dealt
back into pages of the original lengths. That is the null model: pages with the
same lengths whose differences are pure sampling noise.

Input is dataset/liber_primus.json from github.com/Dukotah/cicada3301.
"""

import argparse
import json
import math
import random


def page_indices(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return [("p%02d" % p["page"], list(p["indices"])) for p in d["pages"]]


def shuffled(pages, seed):
    pool = [i for _, idx in pages for i in idx]
    random.Random(seed).shuffle(pool)
    out, k = [], 0
    for name, idx in pages:
        out.append((name, pool[k:k + len(idx)]))
        k += len(idx)
    return out


def distribution(idx, n=29):
    c = [0] * n
    for i in idx:
        c[i] += 1
    return [x / len(idx) for x in c]


def jsd(p, q):
    def kl(a, b):
        return sum(x * math.log2(x / y) for x, y in zip(a, b) if x > 0)
    m = [(x + y) / 2 for x, y in zip(p, q)]
    return (kl(p, m) + kl(q, m)) / 2


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("liber_primus_json")
    ap.add_argument("output_csv")
    ap.add_argument("--shuffle", type=int, help="null model: shuffle runes across pages with this seed")
    a = ap.parse_args(argv)
    pages = page_indices(a.liber_primus_json)
    if a.shuffle is not None:
        pages = shuffled(pages, a.shuffle)
    dists = [(name, distribution(idx)) for name, idx in pages]
    with open(a.output_csv, "w", newline="\n") as f:
        for i in range(len(dists)):
            for j in range(i + 1, len(dists)):
                f.write("%s,%s,%.6f\n" % (dists[i][0], dists[j][0], jsd(dists[i][1], dists[j][1])))


if __name__ == "__main__":
    main()
