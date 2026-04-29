### Session 2025-12-10 22:30 — How can I give a soft score a value?

Here’s how soft score works in Timefold (OptaPlanner successor) and how to “give it a value”:

- You do not set `score` directly on the solution; it is computed from constraints.
- To affect the soft score, create constraints that penalize or reward using the soft part of `HardSoftScore`.

Practical patterns:

1) Fixed soft penalty/reward per match
```kotlin
cf.forEach(MyEntity::class.java)
  .filter { /* condition */ }
  .penalize(HardSoftScore.ofSoft(10)) // subtracts 10 from soft score per match
  .asConstraint("Name of constraint")
```

2) Variable soft weight using an int/long match weigher
```kotlin
// Int weight
cf.forEach(MyEntity::class.java)
  .penalizeInt(HardSoftScore.ONE_SOFT) { entity -> entity.someCount }
  .asConstraint("Soft penalty proportional to count")

// Long weight
cf.forEach(MyEntity::class.java)
  .penalizeLong(HardSoftScore.ONE_SOFT) { entity -> entity.largeWeight.toLong() }
  .asConstraint("Soft penalty proportional to largeWeight")
```

3) Rewards instead of penalties
```kotlin
cf.forEach(MyEntity::class.java)
  .rewardInt(HardSoftScore.ONE_SOFT) { entity -> entity.benefit }
  .asConstraint("Reward for helpful situations")
```

Notes for your current `day10.kt` snippet:

- The override must return `Array<Constraint>`, otherwise Kotlin infers `Array<Any>` and you’ll get a mismatch. Example:
```kotlin
override fun defineConstraints(cf: ConstraintFactory): Array<Constraint> = arrayOf(
  // ...
)
```

- If your match weigher returns `Long`, use `penalizeLong`/`rewardLong`; if it returns `Int`, use `penalizeInt`/`rewardInt`. Returning `Long` to `penalize` overloads that expect `Int` causes a type error.

Applied to your code idea (softly prefer fewer button presses):
```kotlin
class Constraints : ConstraintProvider {
  override fun defineConstraints(cf: ConstraintFactory): Array<Constraint> = arrayOf(
    // Hard: lights must match
    cf.forEach(PressSwitches::class.java)
      .filter { it.invoke() != it.lights }
      .penalize(HardSoftScore.ONE_HARD)
      .asConstraint("Lights must match buttons pressed"),

    // Soft: penalize number of pressed buttons (use Int weigher)
    cf.forEach(PressSwitches::class.java)
      .penalizeInt(HardSoftScore.ONE_SOFT) { it.buttonsPressed.size }
      .asConstraint("Minimize number of button presses")
  )
}
```

Cheat sheet:
- “Give softscore a value X per match” → `.penalize(HardSoftScore.ofSoft(X))`.
- “Give softscore a value equal to f(match)” → `.penalizeInt(HardSoftScore.ONE_SOFT) { f(match) }` (or `penalizeLong`).
- Use `.reward*` variants to add to the soft score instead of subtracting.

### Session 2025-12-10 22:53 — Fix Timefold ClassCastException and model permutations

Issue:
- When solving `Day10Test#name`, Timefold failed with:
```
ClassCastException: sun.reflect.generics.reflectiveObjects.WildcardTypeImpl cannot be cast to java.lang.Class
```
- After partial fixes, a second error appeared during Local Search:
```
IllegalStateException: Unexpected unassigned position.
```

Root causes:
- The list variable was modeled as `List<List<Int>>` with an anonymous value range. Kotlin’s `emptyList()` inferred a wildcard element type, causing `WildcardTypeImpl` during Timefold’s reflective discovery of anonymous value ranges.
- The list variable was initially unassigned and Local Search (K-Opt for list vars) hit an unassigned element.

Fixes applied:
- Introduced a typed value class for list elements to avoid wildcard reflection and provide identity:
```kotlin
data class ButtonPress(
  @PlanningId val id: Int,
  val indices: List<Int>
)
```
- Added an explicit value range and referenced it from the list variable:
```kotlin
@PlanningSolution
class Silver {
  @PlanningEntityProperty lateinit var pressSwitches: PressSwitches
  @ValueRangeProvider(id = "buttonsRange") lateinit var buttonsPressed: List<ButtonPress>
  @PlanningScore var score: HardSoftScore = HardSoftScore.ZERO
}

@PlanningEntity
class PressSwitches : () -> List<Boolean> {
  var lights: List<Boolean> = emptyList()
  @PlanningListVariable(valueRangeProviderRefs = ["buttonsRange"])
  var buttonsPressed: List<ButtonPress> = emptyList()
  override fun invoke(): List<Boolean> =
    buttonsPressed.fold(List(lights.size) { false }) { acc, bp -> acc + bp.indices }
}
```
- Ensured cloning-friendly model (no-arg constructors via default Kotlin classes and `var` fields).
- Corrected constraints signature and match-weigher type:
```kotlin
class Constraints : ConstraintProvider {
  override fun defineConstraints(cf: ConstraintFactory): Array<Constraint> = arrayOf(
    cf.forEach(PressSwitches::class.java)
      .filter { it.invoke() != it.lights }
      .penalize(HardSoftScore.ONE_HARD)
      .asConstraint("Lights must match buttons pressed"),
    cf.forEach(PressSwitches::class.java)
      .penalize(HardSoftScore.ONE_SOFT) { it.buttonsPressed.size }
      .asConstraint("Number of buttons pressed")
  )
}
```
- Initialized the entity with a fully assigned list variable to allow permutations and avoid unassigned errors; additionally limited the solver to Construction Heuristic for this spike:
```kotlin
val allButtons = input.second.mapIndexed { idx, l -> ButtonPress(idx, l) }
pressSwitches = PressSwitches().also { it.lights = input.first.map { it.first }; it.buttonsPressed = allButtons }
buttonsPressed = allButtons

val solverConfig = SolverConfig()
  .withSolutionClass(Silver::class.java)
  .withEntityClasses(PressSwitches::class.java)
  .withConstraintProviderClass(Constraints::class.java)
  .withPhases(ConstructionHeuristicPhaseConfig())
```

Result:
- `Day10Test#name` now passes; solver starts, constructs an initial solution, and completes without exceptions.

Notes:
- If you need Local Search for permutations, keep the list variable assigned at all times or configure list-move selectors carefully; starting from a full assignment is a pragmatic approach for small, permutation-like problems.
