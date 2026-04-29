### Session 2025-11-09 16:17

#### Question
Why does the Kotlin notebook not import the `@file:DependsOn` libs I defined?

#### Answer
Short version: `@file:DependsOn` only adds the artifacts to the classpath; it does not add Kotlin `import` statements for you. In a Kotlin notebook (Jupyter/IntelliJ), you still have to import the classes/packages explicitly and make sure the cell with the dependency directives is executed by the Kotlin kernel before using the classes.

What to check:
- Kernel/language: Ensure the notebook kernel is Kotlin (not Python). In Jupyter, look in the top right; in IntelliJ, the file should be opened with the Kotlin Notebook plugin. If the kernel isn’t Kotlin, lines like `@file:DependsOn("...")` are ignored.
- Cell execution order: The cell with `@file:DependsOn(...)` must be executed before the cells that use the classes. After changing dependencies, Restart Kernel and Run All.
- Imports still required: You must add the imports that your code uses. From your snippet you are referencing `Chorus`, `Alba`, `EnUkDictionary`, `chorusConfig`, etc. Add imports for those, e.g.:

```kotlin
@file:Repository("https://repo1.maven.org/maven2")
@file:DependsOn("org.pitest.voices:chorus:0.0.8")
@file:DependsOn("org.pitest.voices:alba:0.0.8")
@file:DependsOn("org.pitest.voices:en_uk:0.0.8")
@file:DependsOn("com.microsoft.onnxruntime:onnxruntime:1.22.0")

import java.nio.file.Path
// The following package names are examples; use IDE completion to pick the correct ones:
import org.pitest.voices.chorus.Chorus
import org.pitest.voices.chorus.config.chorusConfig
import org.pitest.voices.alba.Alba
import org.pitest.voices.en_uk.EnUkDictionary

val config = chorusConfig(EnUkDictionary.en_uk())
val c = Chorus(config)
val alba = c.voice(Alba.albaMedium())
val audio = alba.say(
    """
        The term "London Times" is not the official name of the newspaper...
    """.trimIndent()
)
audio.save(Path("hello.wav"))
```

- Repository availability: If the artifacts aren’t on Maven Central, add a repository:
```kotlin
@file:Repository("https://repo1.maven.org/maven2")
// or a custom repo if required
```
- Network/Proxy: The kernel needs internet access to download jars the first time. Check proxy settings if you’re behind a proxy.
- Alternative magics: Kotlin Jupyter also supports magics like `%maven`:
```kotlin
%maven org.pitest.voices:chorus:0.0.8
%maven org.pitest.voices:alba:0.0.8
%maven org.pitest.voices:en_uk:0.0.8
%maven com.microsoft.onnxruntime:onnxruntime:1.22.0
```
You would still need `import` lines after this.

Why your current file likely fails:
- The `Voices.ipynb` snippet shows `@file:DependsOn` lines but no `import` statements. Without imports, symbols like `Chorus` and `Alba` remain unresolved even if the dependencies are present.
- If the notebook was accidentally opened under a non-Kotlin kernel, the `@file:DependsOn` directives won’t be processed at all.

Quick troubleshooting checklist:
1) Confirm Kotlin kernel is active.
2) Put `@file:DependsOn` (and optional `@file:Repository`) at the top of the first code cell, run it.
3) Add the necessary `import ...` statements for the classes you use.
4) Restart kernel and Run All after changing dependencies.
5) If resolution still fails, try `%maven` lines instead of `@file:DependsOn`, and watch the cell output for resolution logs.
6) If you’re offline or behind a proxy, configure the proxy for the notebook environment.

If you paste the exact error message from the notebook output, I can pinpoint whether it’s a missing import vs. dependency resolution issue and provide the exact import paths for the `voices` libraries.


#### Follow-up Q&A

Q: Can I import in one cell and use in another?

A: Yes. In Kotlin Jupyter/IntelliJ notebooks, `import` declarations are part of the notebook’s session state. Once the cell with the imports has been executed, those imports are available to subsequently executed cells in the same kernel session.

Caveats:
- You must execute the import cell first. Earlier cells won’t “see” later imports unless you re-run them after the import cell. 
- After a kernel restart, the notebook state is cleared. Re-run the cell with the imports (and any `@file:DependsOn`/`%maven` directives) before running cells that use them.
- `@file:DependsOn` (or `%maven`) adds artifacts to the session classpath for the duration of the session; imports still need to be executed once to bring symbols into scope for subsequent cells.


#### Fix note — NoClassDefFoundError: org/pitest/voices/g2p/util/Resource

That error means a required class from the `voices` G2P module isn’t on the notebook classpath. Add the missing artifact and re-run the kernel/session:

```kotlin
@file:Repository("https://repo1.maven.org/maven2")
@file:DependsOn("org.pitest.voices:chorus:0.0.8")
@file:DependsOn("org.pitest.voices:alba:0.0.8")
@file:DependsOn("org.pitest.voices:en_uk:0.0.8")
@file:DependsOn("org.pitest.voices:g2p:0.0.8")      // <-- provides org.pitest.voices.g2p.util.Resource
@file:DependsOn("com.microsoft.onnxruntime:onnxruntime:1.22.0")
```

Then imports as before, e.g.:
```kotlin
import java.nio.file.Path
import org.pitest.voices.chorus.Chorus
import org.pitest.voices.chorus.config.chorusConfig
import org.pitest.voices.alba.Alba
import org.pitest.voices.en_uk.EnUkDictionary
```

Tips:
- Keep the `org.pitest.voices:*` artifacts on the same version (0.0.8) to avoid binary mismatches.
- After adding `@file:DependsOn`, restart the kernel and Run All so the new jars are picked up.
- You can verify the fix quickly with:
```kotlin
Class.forName("org.pitest.voices.g2p.util.Resource")
```
If it returns a `Class` and not an exception, the classpath contains the G2P jar.

If this artifact is not in your default repo, ensure the repository is set with `@file:Repository(...)` or try the `%maven` magics to see resolution logs.


#### Follow-up — `%maven` unknown

The `%maven` magic is only available in the Kotlin Jupyter kernel (org.jetbrains.kotlinx:kotlin-jupyter). If your environment is IntelliJ’s Kotlin Notebook plugin, line magics like `%maven` aren’t supported — you must use `@file:DependsOn`/`@file:Repository` instead.

How to proceed:
- If you want to stay in IntelliJ Notebook: keep using `@file:DependsOn` and `@file:Repository`. That’s the correct/only way there.
- If you want to use `%maven`: open the notebook in JupyterLab/VS Code with the Kotlin Jupyter kernel installed, and select the "Kotlin" kernel (provided by kotlin-jupyter). Then `%maven ...` will work.

Quick checks:
- In IntelliJ: seeing gutter run icons and no `%` magics is expected.
- In Jupyter: Kernel menu should show "Kotlin"; running `%use kotlin` should print the Kotlin kernel banner. If `%maven` still fails there, you’re not on kotlin-jupyter.

Also, keep the fix for `NoClassDefFoundError` applied (add `org.pitest.voices:g2p:0.0.8`) when using either approach.


### Session 2025-11-09 17:06

#### Issue
`audio.play()` runs but there is no audible sound from speakers.

#### Diagnosis and fixes
- Likely cause: Java Sound (used under the hood) is outputting to a non-default/invalid mixer, or the environment has no accessible audio device (remote session/WSL/CI), or IntelliJ’s notebook process is not routed to your current output device.
- Goal: Verify audio is synthesized, then verify JVM can play sound, then adjust playback route.

##### 1) Verify the audio was synthesized (control path)
Run this in the notebook after creating `audio`:
```kotlin
import java.nio.file.Paths
val out = Paths.get("voices-test.wav")
audio.save(out)
println("Saved to: ${'$'}out (exists=${'$'}{java.nio.file.Files.exists(out)})")
```
Open the file with your OS player to confirm sound:
```kotlin
java.awt.Desktop.getDesktop().open(out.toFile()) // macOS/Windows/Linux (with desktop)
```
- If you hear it here: synthesis is fine; the issue is the in-JVM playback route (`audio.play()`).
- If you do not: the problem is earlier (imports/models/config). Share the cell output.

##### 2) List available Java Sound output devices (mixers)
```kotlin
import javax.sound.sampled.*
AudioSystem.getMixerInfo().forEach { info ->
    val mixer = AudioSystem.getMixer(info)
    val sources = mixer.sourceLineInfo.joinToString { it.lineClass.simpleName }
    println("- ${'$'}{info.name} | ${'$'}{info.description} | sources=[${'$'}sources]")
}
```
Look for devices that expose `SourceDataLine` or `Clip`.

##### 3) Minimal JVM playback test (independent of Voices)
```kotlin
import javax.sound.sampled.*
val format = AudioFormat(16000f, 16, 1, true, false)
val line = AudioSystem.getSourceDataLine(format)
line.open(format)
line.start()
val sr = 16000
val freq = 440.0
val samples = sr
val buf = ByteArray(samples * 2)
for (i in 0 until samples) {
    val s = kotlin.math.sin(2 * Math.PI * freq * i / sr)
    val v = (s * Short.MAX_VALUE).toInt()
    buf[i*2] = (v and 0xFF).toByte()
    buf[i*2+1] = ((v ushr 8) and 0xFF).toByte()
}
line.write(buf, 0, buf.size)
line.drain(); line.stop(); line.close()
println("Played 1s sine wave")
```
- If this is silent or throws: the JVM cannot output audio in this environment (no device, wrong default, or permissions). See step 5.
- If this works but `audio.play()` is silent: it’s likely selecting a different mixer.

##### 4) Workarounds if `audio.play()` stays silent
- Prefer file playback: `audio.save(...)` then `Desktop.open(...)` to use the system player.
- If the Voices API allows providing a mixer/line, select a specific `Mixer` by name (depends on the library; if not available, consider raising an issue upstream). Example vanilla Java Sound pattern:
```kotlin
val info = AudioSystem.getMixerInfo().first { it.name.contains("Built-in") }
val mixer = AudioSystem.getMixer(info)
val lineInfo = DataLine.Info(SourceDataLine::class.java, AudioFormat(16000f, 16, 1, true, false))
val line = mixer.getLine(lineInfo) as SourceDataLine
// write bytes as in the sine example
```

##### 5) Environment-specific notes
- macOS: Java uses the current system output device (System Settings > Sound). Ensure IntelliJ is running locally (not over SSH) and sound is not routed to inactive devices (AirPods disconnected, HDMI monitor muted).
- Windows: Check Output device in System > Sound; ensure IntelliJ is not muted in Volume Mixer.
- Linux: Ensure PulseAudio/PipeWire is running; verify default sink; playing from the system player will confirm routing.
- WSL/Remote/Docker/CI: No native audio sink. Use `audio.save(...)` and play on the host.

##### 6) Quick checklist
- Audio file saved and plays in an external player → synthesis OK.
- Java Sound sine test works → environment OK; issue is `audio.play()` routing.
- Both fail → environment/device problem.

##### 7) If still stuck
Please paste:
- Output of the mixers listing.
- Result of the sine test (any exception).
- Your OS and whether this is IntelliJ Notebook or Jupyter, local vs remote.

