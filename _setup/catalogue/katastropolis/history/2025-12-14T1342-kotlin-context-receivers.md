### Session 2025-12-14T13:42

Q: what kotlin compiler arg do i have to add to use `context()` in kotlin?

A:
- The compiler flag is `-Xcontext-receivers`.
- You need this only on Kotlin versions where context receivers are still experimental (Kotlin 1.6.20–1.9.x). In Kotlin 2.0+ (K2), `context` receivers are stable and the flag is not required.

Gradle Kotlin DSL examples:

```kotlin
// For Kotlin < 2.0
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile>().configureEach {
    kotlinOptions.freeCompilerArgs += "-Xcontext-receivers"
}
```

For Kotlin Multiplatform:
```kotlin
kotlin {
    targets.configureEach {
        compilations.configureEach {
            compileTaskProvider.configure {
                kotlinOptions.freeCompilerArgs += "-Xcontext-receivers"
            }
        }
    }
}
```

No flag needed on Kotlin 2.0+; just use the `context(A, B)` syntax normally.
