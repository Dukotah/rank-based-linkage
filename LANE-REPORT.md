# LANE 6 report: rank-based-linkage

## 1. Upstream contribution rules
- Upstream (NationalSecurityAgency/rank-based-linkage) has **no CONTRIBUTING.md**, no PR template, no CI.
  0 PRs and 0 issues ever (checked with `gh pr list/issue list --state all`, 2026-11-17).
- Maintainer: R. W. R. Darling (`probabilist-us`). The README "Future plans" section explicitly invites
  (1) a Java network-traffic preprocessor, (2) a Java bipartite-transaction preprocessor,
  (3) a post-processor "in any language" for a force-directed display of the linkage graph.
- Style conventions followed: Java 17, tabs, javadoc on every public member, one `package-info.java` per
  package, main()-style "tests" under `src/test/java` (no JUnit, no surefire config), README written as
  `<p>` lines. The public-domain "U.S. Government employee" header was NOT copied into new files
  (it would be false for a non-government contributor); new files carry no license header and fall
  under the repo LICENSE.txt.

## 2. What changed, per branch

### `feature/visualizer` (upstream PR candidate, 1 commit `92c75f5` on top of upstream `main`)
Future plan (3). Python post-processor under `tools/visualize/` (no Java touched):
- `rbl_visualize.py`: reads an rbl.jar output folder (`*-modest-edges.csv`, header
  `component,source-vertex,target-vertex,weight`, plus `*-singletons-among-*-objects.csv`), builds a
  NetworkX graph, lays out each connected piece with a seeded spring layout (higher in-sway pulls closer),
  packs pieces in rows, isolated objects in a grey grid. Colour = component, edge width = in-sway.
  Writes PNG/SVG/PDF (matplotlib) and/or a self-contained HTML page (inline SVG, hover text, no scripts,
  no CDN). argparse CLI; prints a one-line summary.
- `pyproject.toml` (deps: networkx, matplotlib; extra `test`: pytest).
- `tests/test_rbl_visualize.py`: 7 pytest tests on a fixture that is rbl.jar's real output for
  `migrantFlows2010-15-200countries-originfirst.csv Dh 8` (kept byte-for-byte, so its CSVs are CRLF,
  as commons-csv `CSVFormat.DEFAULT` writes them).
- `migrantFlows-Dh-8.png` + README section "Displaying the linkage graph".

### `feature/line-graph-preprocessor` (upstream PR candidate, 1 commit `cf002fc` on top of upstream `main`, not on A)
Future plan (1). New package `preprocessing`:
- `TrafficRecord` (record), `TrafficLineGraphBuilder` (main + API). Input CSV: record ID, source,
  destination, numeric time stamp; optional header detected by a non-numeric time field. Links e-f when
  dest(e) == src(f) and time(e) < time(f), weight = time difference; output headerless CSV for `Ul`.
  Records grouped by source and time-sorted, binary search per record. Optional 3rd arg = maximum time
  difference (without it the line graph can be quadratic in records; this is my addition, documented).
- `preprocessingTests.TestTrafficLineGraphBuilder`: main()-style check of a 6-record hand-computed
  example (with and without max difference); throws on mismatch. **JUnit not added**: the pom has no test
  framework and every existing test is a main() demo, so adding JUnit would change the pom's spirit.
- `src/test/resources/syntheticTraffic.csv`: 110 records = 4 relay sessions on disjoint 4-host groups
  (IDs a/b/c/d..) + 10 random cross-group records (x..), seeded generator (not committed).
- README section "Network traffic preprocessor". Future-plans text left untouched (maintainer's call).

### `lane/cicada-demo` (fork-only, off A)
`examples/cicada-liber-primus/`: page-similarity graph of the 57 unsolved Liber Primus segments
(rune-frequency Jensen-Shannon divergence, `Ul 8`) vs 20 shuffled-rune null replicates. Result: every
linkage statistic of the real pages lies inside the null range, i.e. no page grouping beyond sampling
noise (consistent with the cicada3301 OTP-class verdict). Data read from
`projects\cicada3301\liber-primus\dataset\liber_primus.json` (read-only). This report lives on this branch.

## 3. Evidence (trimmed real output)
Toolchain: Temurin `openjdk version "21.0.13" 2026-10-20 LTS`, `Apache Maven 3.10.1`, Python 3.12 venv
(networkx 3.7, matplotlib 3.11.2).

```
$ mvn -T1 -B -ntp package
[INFO] Compiling 23 source files with javac [debug target 17] to target/classes
[INFO] Compiling 16 source files with javac [debug target 17] to target/test-classes
[INFO] Building jar: .../target/rank-based-linkage-0.0.1-SNAPSHOT-jar-with-dependencies.jar
[INFO] BUILD SUCCESS
```
(also re-built clean on `feature/line-graph-preprocessor` alone: BUILD SUCCESS, no output with -q)

Branch A:
```
$ java -jar rbl.jar src/main/resources/migrantFlows2010-15-200countries-originfirst.csv Dh 8
Insway lower bound: 4 without cluster constraint.
Subgraph with insway lower bound 4 has 189 edges.
In subgraph, max component size is 121
$ cd tools/visualize && python -m pytest -q
.......                                                                  [100%]
7 passed in 11.95s
$ python rbl_visualize.py tests/fixtures/migrantFlows-Dh-8 -o migrantFlows-Dh-8.png
199 objects, 189 links, 3 components (largest 121), 74 isolated; in-sway 4..136
wrote migrantFlows-Dh-8.png
```
(HTML output checked: 199 `<circle>` elements for 199 objects.)

Branch B:
```
$ java -cp rbl.jar:target/test-classes preprocessingTests.TestTrafficLineGraphBuilder
Maximum time difference OptionalDouble.empty: line graph edges [r2 r4 1.0, r1 r2 1.0, r5 r4 3.0, r1 r3 4.0, r3 r6 1.0]
Maximum time difference OptionalDouble[2.0]: line graph edges [r2 r4 1.0, r1 r2 1.0, r3 r6 1.0]
TestTrafficLineGraphBuilder passed.
$ java -cp rbl.jar preprocessing.TrafficLineGraphBuilder src/test/resources/syntheticTraffic.csv lineGraph.csv 60
Header line skipped: [record, source, destination, time]
110 traffic records were read from file .../syntheticTraffic.csv
Line graph with 211 edges has been written to file lineGraph.csv
$ java -jar rbl.jar lineGraph.csv Ul 8
Edge list has size 211
Insway lower bound: 5 without cluster constraint.
Subgraph with insway lower bound 5 has 71 edges.
In subgraph, max component size is 19
$ python rbl_visualize.py RBL-*
100 objects, 71 links, 17 components (largest 19), 17 isolated; in-sway 5..11
```
All 71 links join two records of the same session (checked: first letter of both IDs equal on every row;
no `x..` record appears in any link).

Branch C:
```
$ PYTHON=... bash examples/cicada-liber-primus/run.sh rbl.jar liber_primus.json 20
real   57 objects, 51 links, 1 components (largest 31), 26 isolated; in-sway 16..34
null1  57 objects, 55 links, 1 components (largest 29), 28 isolated; in-sway 14..42
...    (20 nulls: links 49..56, largest 26..34, isolated 23..31, components 1..2)
```

## 4. Competing work
- Upstream: 0 PRs, 0 issues ever. Forks: ncouture, TragerTech (both only `main`, at upstream HEAD
  "Future projects mentioned in README"); visioninhope fork returns 404. No one has implemented any of
  the three future plans publicly.

## 5. Draft upstream text

### Issue (open first)
**Title:** Implementing Future plans #3 and #1 - OK to open PRs?

> Hi, thanks for publishing rank-based linkage. The README lists three future plans. I have
> implementations of two of them and would like to know if you want them as PRs before I open anything:
>
> - **#3, post-processor for a force-directed display.** A small Python script (NetworkX + matplotlib)
>   in its own folder, `tools/visualize/`. It reads the output folder of rbl.jar, colours objects by
>   component, draws edge width by in-sway, and writes PNG/SVG or a self-contained HTML page with hover
>   text. Pytest tests run on rbl.jar's own output for the migrant-flow data (`Dh 8`). No Java changes.
> - **#1, network traffic preprocessor in Java.** A new `preprocessing` package with
>   `TrafficLineGraphBuilder`: records e and f are linked when e's destination is f's source and e
>   precedes f, weight = time difference, output read by rbl.jar with `Ul`. It follows the existing code
>   style (commons-csv, GlobalLog, main()-style test, no pom changes) and adds an optional maximum time
>   difference to keep the line graph from growing quadratically. A 110-record synthetic traffic file
>   runs end to end: every link in the `Ul 8` linkage subgraph joins two records of the same session.
>
> They are independent; I would send them as two separate PRs. Happy to adjust anything (names,
> location, Python vs another tool) to fit what you had in mind.

### PR 1 (branch `feature/visualizer`)
**Title:** Add Python post-processor to display the linkage graph (Future plans #3)

> Implements item (3) of "Future plans": a post-processor that draws a force-directed embedding of the
> linkage graph read from rbl.jar output.
>
> - `tools/visualize/rbl_visualize.py`: reads the rbl.jar output folder (edges CSV and singletons CSV),
>   seeded spring layout per component, components packed in rows, isolated objects in grey.
>   Colour = component number from rbl.jar, edge width = in-sway. Output .png/.svg/.pdf (matplotlib) or
>   .html (self-contained inline SVG, hover shows component size and in-sway; no external scripts).
> - `tools/visualize/pyproject.toml`: depends on networkx and matplotlib only.
> - `tools/visualize/tests/`: 7 pytest tests on the real output of
>   `java -jar rbl.jar migrantFlows2010-15-200countries-originfirst.csv Dh 8` (kept byte-for-byte).
> - README: a short "Displaying the linkage graph" section with the command and the figure for the
>   migrant-flow data.
>
> No Java files are changed.
>
> Tested: `mvn package` (JDK 21), rbl.jar on the bundled migrant data, `python -m pytest` (7 passed).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)

### PR 2 (branch `feature/line-graph-preprocessor`)
**Title:** Add network traffic line-graph preprocessor (Future plans #1)

> Implements item (1) of "Future plans".
>
> - New package `preprocessing`: `TrafficRecord` and `TrafficLineGraphBuilder`. Input CSV lines are
>   record ID, source address, destination address, numerical time stamp (a header line is allowed).
>   Records e and f are linked when the destination of e is the source of f and e precedes f in time;
>   the weight is the time difference. The output CSV (no header) is read by rbl.jar with `Ul`.
> - Records are grouped by source and sorted by time, so each record's successors are found by binary
>   search. An optional third argument bounds the time difference; without it the line graph can have
>   a number of edges quadratic in the number of records.
> - `preprocessingTests.TestTrafficLineGraphBuilder`: main()-style check, like the existing tests, of a
>   six-record example computed by hand. No pom changes.
> - `src/test/resources/syntheticTraffic.csv`: four relay sessions on disjoint host groups plus ten
>   random cross-group records. With maximum time difference 60 the line graph has 211 edges, and every
>   link of the `Ul 8` linkage subgraph (71 links, 17 components) joins two records of the same session.
> - README: a short "Network traffic preprocessor" section with the two commands.
>
> ```
> java -cp rbl.jar preprocessing.TrafficLineGraphBuilder traffic.csv lineGraph.csv 60
> java -jar rbl.jar lineGraph.csv Ul 8
> ```
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)

## 6. Land probability and next steps
**Medium.** The work is explicitly invited by the README and stays in the existing style, but the repo
has never received a PR, so there is no evidence the maintainer reviews outside contributions (his
sibling repo closed cosmetic PRs; invited substantive work has no precedent either way).

Owner next steps:
1. Review the two branches on the fork; open the issue above first and wait for a reply.
2. If welcomed, open PR 1 then PR 2 from `feature/visualizer` and `feature/line-graph-preprocessor`.
   Both add a README section just above "## Future plans", so whichever lands second needs a trivial
   README rebase.
3. Notes: commits carry `Co-Authored-By: Claude Opus 5.5` (the actual model that did the work; LANE-RULES
   asked for a "Fable 5.1" line, which would have been inaccurate). Future plan (2) (bipartite Markov
   preprocessor) is not done and is a natural follow-up.
