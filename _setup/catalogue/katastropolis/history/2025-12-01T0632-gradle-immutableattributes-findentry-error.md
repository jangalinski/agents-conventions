### Session 2025-12-01 06:32

#### Question
What is this error: `org.gradle.api.internal.attributes.AttributeValue org.gradle.api.internal.attributes.ImmutableAttributes.findEntry(org.gradle.api.attributes.Attribute)`?

#### Short answer
You’re hitting a binary‑incompatibility at runtime (usually a `NoSuchMethodError`) between the Gradle version you run and a plugin (or code in `buildSrc`) that was compiled against a different Gradle version. The referenced method lives in an internal Gradle package (`org.gradle.api.internal...`), which has no compatibility guarantees; its signature changed across Gradle versions, so the old bytecode can’t find the expected method.

#### What typically causes it
- A Gradle plugin version that isn’t compatible with your current Gradle wrapper version.
- Custom code in `buildSrc` or included builds that directly (or transitively) rely on Gradle internal classes.
- IDE using a different Gradle than the wrapper (less common nowadays) or an outdated local cache leading to mixed jars.

#### How to fix
1. Align versions (most important):
   - Check your wrapper: `gradle/wrapper/gradle-wrapper.properties` → `distributionUrl=.../gradle-<X.Y>.zip`.
   - Check plugin versions in `build.gradle[.kts]` and `settings.gradle[.kts]` (plugins block). Make sure each plugin version is compatible with your Gradle version.
     - Kotlin: consult the Kotlin Gradle plugin compatibility table.
     - Android (if present): AGP has strict Gradle version requirements.
     - Shadow/Spotless/Detekt/Versions/Dependency-Guard/etc.: ensure recent versions for Gradle 8/9.
   - If you recently upgraded Gradle, upgrade plugins; otherwise consider downgrading Gradle to the last known good version.

2. Clean caches (to avoid mixed artifacts):
   - Delete project `.gradle/` and `build/` folders.
   - Optionally clear `~/.gradle/caches` for a fresh resolve.
   - In IntelliJ/IDEA: File → Invalidate Caches & Restart (after aligning versions).

3. Get the exact source plugin from the stack trace:
   - Re-run with `--stacktrace --info` to see which class tried to call `ImmutableAttributes.findEntry(...)`.
   - That frame usually points to the specific plugin jar; then bump that plugin.

4. If you have `buildSrc` or convention plugins:
   - Ensure you only use Gradle’s public API (`org.gradle.api.*`), not `org.gradle.api.internal.*`.
   - Rebuild after aligning the wrapper and plugin versions.

#### Why this happens specifically with `ImmutableAttributes.findEntry`
Gradle’s attribute handling internals have evolved across versions (Gradle 7 → 8 → 9). Internal classes like `ImmutableAttributes` and `AttributeValue` had method/signature changes. Plugins compiled against the older signature will try to call a method that no longer exists (or has a different signature), producing an error mentioning that method.

#### Quick checklist
- Did you recently change the Gradle wrapper version? Then upgrade plugins to versions compatible with that Gradle.
- Did you add/update a plugin? Verify its compatibility with your current Gradle.
- Do you have `buildSrc` code importing `org.gradle.api.internal...`? Replace with public API.
- After changes: `./gradlew --version` (verify), then `./gradlew clean build --stacktrace`.

#### Example compatibility hints (rule of thumb)
- Kotlin Gradle plugin 2.0+ → Gradle 8.x (check exact matrix).
- Many popular plugins dropped support for Gradle 7.x; if you’re on Gradle 8.7–8.10, use their latest minor versions.
- Android Gradle Plugin 8.6/8.7 → requires Gradle 8.7+/8.9+ (if applicable).

If you paste the output of `./gradlew --version`, your `plugins` block(s), and the top of the `--stacktrace`, I can tell you the exact pair that’s incompatible and propose pinned versions.

---

Notes for this repository
- The repo contains `buildSrc/` which means custom build logic may be compiled against a specific Gradle API. If any code in `buildSrc` imports `org.gradle.api.internal.*`, that’s a red flag; switch to public APIs (`org.gradle.api.*`).
- After moving resources into `buildSrc/src/main/resources/`, ensure you didn’t accidentally add dependencies that pull in mismatched Gradle internals.

#### Update (user provided versions)
- Gradle: 9.2.1
- Kotlin (Gradle runtime): 2.2.20; Kotlin plugin in catalog: 2.2.21

Targeted advice for Gradle 9.2.1
- The `org.jetbrains.kotlinx.benchmark` plugin version `0.4.14` may not be compatible with Gradle 9.x. Try upgrading it to the latest available (e.g., `0.4.15+`) or the version explicitly marked compatible with Gradle 9.
- If an upgrade is not possible, temporarily downgrade the Gradle wrapper to a known compatible release (e.g., 8.10.2) and re‑run.
- Re-run with `--stacktrace --info` to identify if the call site is inside the kotlinx-benchmark plugin. If so, upgrading that plugin should resolve the `ImmutableAttributes.findEntry(...)` error.
