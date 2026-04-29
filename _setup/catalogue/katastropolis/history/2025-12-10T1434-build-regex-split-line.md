### Session 2025-12-10 14:34

#### Problem
Build a regex that parses a line like:

```
[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}
```

into three parts:
- A list of `'.'` and `'#'` from the square brackets
- A sequence of integer lists from the `(...)` groups
- A list of integers from the trailing `{...}`

#### Recommended approach (Kotlin/Java regex)
In Java/Kotlin regex, a repeated capturing group only keeps the last capture. So use a master regex to capture the three logical zones, and a secondary regex to iterate the repeated parenthesized groups.

1) Master regex — captures the three zones (cells, all paren groups as a chunk, scores):

```
^\[(?<cells>[.#]+)]\s+(?<groups>(?:\(\d+(?:,\d+)*\)\s+)+)\{(?<scores>\d+(?:,\d+)*)}$
```

- `cells` → the `'.'`/`'#'` sequence inside `[]`
- `groups` → the entire text that consists of one or more `(...)` lists separated by spaces
- `scores` → the comma-separated integers inside `{}`

2) Secondary regex — iterate each `(...)` group inside `groups` and split numbers:

```
\((\d+(?:,\d+)*)\)
```

#### Kotlin example
```kotlin
val line = "[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}"

val master = Regex(
  """^\[(?<cells>[.#]+)]\s+(?<groups>(?:\(\d+(?:,\d+)*\)\s+)+)\{(?<scores>\d+(?:,\d+)*)}$"""
)
val paren = Regex("\\((\\d+(?:,\\d+)*)\\)")

val m = master.matchEntire(line) ?: error("No match: $line")

val cells: List<Char> = m.groups["cells"]!!.value.toList()

val groupLists: List<List<Int>> = paren.findAll(m.groups["groups"]!!.value)
  .map { it.groupValues[1].split(',').map(String::toInt) }
  .toList()

val scores: List<Int> = m.groups["scores"]!!.value.split(',').map(String::toInt)

println(cells)       // ['.', '#', '#', '#', '.', '#']
println(groupLists)  // [[0,1,2,3,4], [0,3,4], [0,1,2,4,5], [1,2]]
println(scores)      // [10, 11, 11, 5, 10, 5]
```

#### Notes
- The spaces between the `(...)` groups are matched by `\s+`. If there can be tabs or variable whitespace, this still works. If you want exactly one space, change `\s+` to a literal single space.
- If you need to make the braces or parentheses optional in other lines, wrap those parts in optional groups (e.g., `(?: ... )?`) accordingly.

---

### Session 2025-12-10 14:36 — Can we avoid the second regex?

Yes. You can use a single regex in a tokenizing pass with `findAll`, leveraging the `\G` anchor to continue matching from where the previous match ended. This avoids a separate "paren regex" while still extracting all groups.

Single-pass pattern:

```
\G(?:\[(?<cells>[.#]+)]\s*|\((?<group>\d+(?:,\d+)*)\)\s*|\{(?<scores>\d+(?:,\d+)*)\}\s*)
```

Kotlin example:

```kotlin
val line = "[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}"

val token = Regex(
  """\G(?:\[(?<cells>[.#]+)]\s*|\((?<group>\d+(?:,\d+)*)\)\s*|\{(?<scores>\d+(?:,\d+)*)\}\s*)"""
)

val cells = mutableListOf<Char>()
val groupLists = mutableListOf<List<Int>>()
var scores: List<Int> = emptyList()

var pos = 0
while (true) {
  val m = token.find(line, pos) ?: break
  val g = m.groups
  g["cells"]?.value?.let { cells += it.toList() }
  g["group"]?.value?.let { groupLists += it.split(',').map(String::toInt) }
  g["scores"]?.value?.let { scores = it.split(',').map(String::toInt) }
  pos = m.range.last + 1
}

require(pos == line.length) { "Unparsed tail at position $pos in: $line" }

println(cells)      // ['.', '#', '#', '#', '.', '#']
println(groupLists) // [[0,1,2,3,4], [0,3,4], [0,1,2,4,5], [1,2]]
println(scores)     // [10, 11, 11, 5, 10, 5]
```

Why this works:
- `\G` ensures each next match starts exactly at the end of the previous match, so the whole line is consumed in order.
- The alternation captures one of: the bracketed cells, a parenthesized list, or the final braces list, each time.
- Named groups indicate which branch matched, letting you collect results without a second regex.

Notes:
- If you prefer not to manage `pos` manually, you can still use `findAll` and fold over matches, but to enforce full coverage of the line, the `pos` loop with `\G` is clearer.
- If input can include leading/trailing spaces, allow a leading `^\s*` and final `\s*$` in a wrapping check, or incorporate optional whitespace at the start/end of the tokenization loop.
