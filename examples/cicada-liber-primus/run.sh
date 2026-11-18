#!/usr/bin/env bash
# Rank-based linkage on Liber Primus page-similarity graphs: the real pages, then N null replicates.
# Usage: run.sh path/to/rbl.jar path/to/liber_primus.json [N=20] [workdir=./lp-runs]
set -e
JAR=$(realpath "$1"); LP=$(realpath "$2"); N=${3:-20}; W=${4:-lp-runs}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PYTHON:-python3}
mkdir -p "$W"; cd "$W"
run() {
  rm -rf "run_$1"; mkdir "run_$1"; cd "run_$1"
  "$PY" "$HERE/page_graph.py" "$LP" pages.csv ${2:+--shuffle $2}
  java -Xmx256m -jar "$JAR" pages.csv Ul 8 > rbl.log 2>&1
  printf "%s " "$1"; "$PY" "$HERE/../../tools/visualize/rbl_visualize.py" RBL-*
  cd ..
}
run real
for s in $(seq 1 "$N"); do run "null$s" "$s"; done
