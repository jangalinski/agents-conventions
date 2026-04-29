### Inject a custom properties file into `gradle.extra` from `settings.gradle.kts`

Here’s a compact, production‑friendly example that loads a custom properties file (e.g., `gradle/config/project.properties`) and injects every key/value into `extra` at settings level, and optionally propagates them to all projects’ `extra` as well.

```kotlin
// settings.gradle.kts

// Change this to wherever you keep your custom file
val customPropsFile = file("gradle/config/project.properties")

if (customPropsFile.isFile) {
  // In a real settings.gradle.kts file you can: `import java.util.Properties`
  // or use fully qualified name as below
  val props = java.util.Properties()
  customPropsFile.inputStream().use(props::load)

  // Put into settings-level extra
  props.forEach { k, v ->
    extra[k.toString()] = v.toString()
  }

  // Optionally propagate to every project so `project.extra["key"]` works everywhere
  gradle.beforeProject {
    props.forEach { k, v ->
      extra[k.toString()] = v.toString()
    }
  }

  println("[settings] Loaded ${props.size} props from ${customPropsFile}")
} else {
  println("[settings] No custom properties found at ${customPropsFile}")
}
```

#### How to use the injected values
- In any `build.gradle.kts` (root or subproject):
  ```kotlin
  val myValue = extra["some.key"] as String
  ```
- If you also propagated via `beforeProject`, the same works in every subproject without additional setup.

#### Notes
- `extra` is Gradle’s `ExtraPropertiesExtension`. Values you set here are accessible as `extra["key"]` in Kotlin DSL.
- This does not make them available via `providers.gradleProperty("key")`; that mechanism reads Gradle project properties (e.g., `gradle.properties` or `-Pkey=...`). If you need that, you can also map them into `startParameter.projectProperties` early, but for most cases `extra` is sufficient and explicit.
- You can choose any file path and keep it committed (e.g., under `gradle/config/`) to avoid adding a `gradle.properties` in the repo root.

### 2025-11-06T2343 — include mockito-kotlin to testImplementation

- Added Mockito-Kotlin to the `testImplementation` configuration of the Timefold spike module.
- File: `_spikes/timefold-spike/build.gradle.kts`
- Dependency added:

```kotlin
dependencies {
  // ...
  // Mockito Kotlin bindings for idiomatic Kotlin mocks
  testImplementation("org.mockito.kotlin:mockito-kotlin:5.4.0")
  // ...
}
```

Notes:
- Kept it as a direct coordinate (no version catalog alias) to keep the change minimal. Can be moved into `gradle/libs.versions.toml` later if desired.
- Works with JUnit 5 setup already present in the module.


### 2025-11-06T2352 — Parse BigDecimal list from string with regex

- Adjusted the regex `pattern` in `BigDecimalListConverter` to match integers and decimals (with optional leading minus):
  ```kotlin
  val pattern = """-?\d+(?:\.\d+)?""".toRegex()
  ```
- Implemented the converter to extract all numeric matches and map them to `BigDecimal`:
  ```kotlin
  override fun convert(source: Any?, context: ParameterContext): List<BigDecimal> {
    require(source is String) { "source is not a String: $source" }
    val numbers = pattern.findAll(source).map { it.value.toBigDecimal() }.toList()
    require(numbers.isNotEmpty()) { "no numeric values found in: $source" }
    return numbers
  }
  ```
- Where: `_spikes/timefold-spike/src/test/kotlin/taxes/ResolveTaxRatesTest.kt`
- Example inputs supported: `"[ 1.22, 9, 21.00 ]"`, `"1,2,3"`, `"-5, 0.75"` → `List<BigDecimal>` accordingly.


### 2025-11-06T2358 — Money amounts: enforce 2-decimal scale in converter

- Updated `BigDecimalListConverter` to always return amounts scaled to 2 decimal places (money format).
- Implementation detail: each parsed number is mapped via `setScale(2, RoundingMode.HALF_UP)`.
- Where: `_spikes/timefold-spike/src/test/kotlin/taxes/ResolveTaxRatesTest.kt`.

Code snippet:
```kotlin
val numbers = pattern.findAll(source)
  .map { it.value.toBigDecimal().setScale(2, java.math.RoundingMode.HALF_UP) }
  .toList()
```

Examples:
- Input: `[1, 2, 31.23]` → `[1.00, 2.00, 31.23]`
- Input: `"-3.1, 5.678"` → `[-3.10, 5.68]` (rounded HALF_UP)

Notes:
- Keeps the existing regex for integers/decimals with optional leading minus.
- BigDecimal equality is scale-sensitive; callers and tests should expect 2-decimal scale now.


### 2025-11-07T0030 — Configure Byte Buddy agent globally for Mockito inline mock-maker

- Problem: Running tests (e.g., `ResolveTaxRatesTest`) showed warnings that Mockito is self-attaching the inline-mock-maker via Byte Buddy, which will be disallowed by default in future JDK releases.
- Solution: Configure a Java agent globally in the root `build.gradle.kts` so all `Test` tasks run with a Java agent and Mockito doesn’t need to self-attach.

Where: `build.gradle.kts` (root)

Snippet:
```kotlin
allprojects {
  // Provide Byte Buddy agent for Mockito inline mock-maker to avoid JDK warnings and future breakage
  val byteBuddyAgent by configurations.creating
  dependencies {
    add("byteBuddyAgent", "net.bytebuddy:byte-buddy-agent:1.17.7")
  }

  tasks.withType<Test>().configureEach {
    // Add Byte Buddy as a Java agent so Mockito doesn't need to self-attach
    jvmArgs("-javaagent:${configurations.getByName("byteBuddyAgent").singleFile}")
  }
}
```

Notes:
- This applies to all subprojects’ `Test` tasks.
- Keeps repos and versions centralized via existing repository definitions.
- Eliminates the self-attach warnings and is forward-compatible with future JDK changes.
