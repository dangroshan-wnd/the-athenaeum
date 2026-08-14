# Local LLM experiment

These files preserve an early Ollama prompt experiment named Gwen:

- [`Modelfile`](Modelfile) defines the local model profile.
- [`system-prompt.txt`](system-prompt.txt) preserves the standalone prompt text.

From this directory, rebuild and run the profile with:

```powershell
ollama create gwen-beta -f .\Modelfile
ollama run gwen-beta
```

The old machine-specific prompt synchronization helper was not published here because it wrote to a user-local editor configuration and embedded absolute paths.
