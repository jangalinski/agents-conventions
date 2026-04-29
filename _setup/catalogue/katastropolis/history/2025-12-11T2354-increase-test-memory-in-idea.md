### Session 2025-12-11 23:54 — Temporarily increase memory for tests in IntelliJ IDEA

You can increase heap for tests without changing project files. Pick the option that matches how your tests run in IDEA:

- If tests run with IntelliJ (JUnit run configuration):
  1. Run any test once, then open Run/Debug Configurations (top-right dropdown → Edit Configurations…).
  2. Select the JUnit run configuration that runs `Day11Test` (or create one).
  3. In VM options add, for example: `-Xmx4g -Xms1g` (adjust values as needed).
  4. Apply and re-run.

- If tests run via Gradle (default in many Kotlin projects):
  Option A — per-run Gradle config:
  1. Open Run/Debug Configurations → select the Gradle configuration that runs `:advent-of-code:test`.
  2. Put `-Xmx4g -Xms1g` into the “Gradle VM options” field.
  3. Apply and re-run. If the Gradle daemon was already running with lower heap, stop it: Gradle tool window → “Stop” (or run `gradle --stop`). Then re-run tests.

  Option B — set env var only for this run config:
  1. In the same Gradle run configuration, add environment variable: `ORG_GRADLE_JVMARGS=-Xmx4g -Xms1g`.
  2. Apply and re-run (stopping the daemon may be required once).

- Quick toggle between runners:
  Settings/Preferences → Build, Execution, Deployment → Gradle → “Run tests using”:
  - Choose “IntelliJ IDEA” to use the JUnit run config VM options.
  - Choose “Gradle” to use the Gradle VM options / `ORG_GRADLE_JVMARGS`.

Notes:
- This is temporary and local to your IDE; it won’t modify `build.gradle.kts`.
- Start with `-Xmx3g` or `-Xmx4g`. If metaspace is an issue, add `-XX:MaxMetaspaceSize=512m`.
- If you later commit a permanent setting, the Gradle way is in `build.gradle.kts`:
  ```kotlin
  tasks.test { maxHeapSize = "4g" }
  ```

### Session 2025-12-11 23:57 — Set Gradle memory via gradle.properties

To raise memory for the Gradle daemon (and most Gradle-run tasks) at the project level, add this line to your project’s `gradle.properties` (root of the repo):

```
org.gradle.jvmargs=-Xms1g -Xmx4g -XX:MaxMetaspaceSize=512m -Dfile.encoding=UTF-8
```

Notes and tips:
- After changing `gradle.properties`, restart the Gradle daemon once so the new heap is used:
  - In IDEA: Gradle tool window → “Stop” (or rerun with “Reload All Gradle Projects”).
  - CLI: `./gradlew --stop` then rerun your task.
- You can also set this globally in `~/.gradle/gradle.properties` if you want it for all projects.
- If the OutOfMemoryError happens in the forked test JVM (not the Gradle daemon), set test heap in your build script instead of `gradle.properties`:
  - Kotlin DSL: `tasks.test { maxHeapSize = "4g" }`
  - Or per-test task if you have multiple test tasks.
- Equivalent environment variable for one-off runs: `ORG_GRADLE_JVMARGS="-Xms1g -Xmx4g -XX:MaxMetaspaceSize=512m"`.

Quick checklist:
- Project file edited: `gradle.properties` → add `org.gradle.jvmargs=...`
- Restart Gradle daemon once
- If still OOM during tests, add `tasks.test { maxHeapSize = "4g" }` in `build.gradle.kts`
