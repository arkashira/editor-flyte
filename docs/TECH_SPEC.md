# TECH_SPEC.md – editor‑flyte  

**Product:** editor‑flyte – a lightweight, high‑performance code editor built for speed, reliability, and extensibility.  
**Target Users:** Professional developers and power‑users who need a fast, responsive editing experience without the memory‑heavy bloat of traditional IDEs (e.g., VS Code, JetBrains).  
**Version:** 1.0.0 (initial production release)  
**Repository:** `arkashira/editor-flyte`  

---  

## 1. Architecture Overview  

```
+-------------------+          +-------------------+          +-------------------+
|   UI Layer (Web)  | <------> |   Core Engine     | <------> |   Plugin System   |
|  (React + Tauri) |          |  (Rust + WASM)    |          |  (Dynamic Rust)   |
+-------------------+          +-------------------+          +-------------------+
          ^                               ^                               ^
          |                               |                               |
          |                               |                               |
          |                               |                               |
+-------------------+          +-------------------+          +-------------------+
|   File System     | <------> |   Language Server | <------> |   Extension API   |
|   (Native FS)    |          |   (LSP Bridge)    |          |   (JSON‑RPC)      |
+-------------------+          +-------------------+          +-------------------+
```

* **UI Layer** – Cross‑platform desktop UI built with **React** (TypeScript) bundled via **Tauri** (Rust‑based native wrapper).  
* **Core Engine** – High‑throughput text buffer, syntax highlighting, and diff engine written in **Rust**, compiled to **WebAssembly** for the UI and also used natively in the Tauri process.  
* **Plugin System** – Dynamically loadable Rust crates compiled to shared libraries (`.so/.dylib/.dll`). Plugins expose a **JSON‑RPC** interface that the Core Engine forwards to the UI.  
* **Language Server Bridge** – Integrated LSP client that forwards editor events to external language servers (e.g., `pyright`, `tsserver`) via the **vLLM**‑compatible async runtime.  
* **File System Layer** – Direct native file I/O through Rust’s `std::fs` with optional **watcher** (notify crate) for external changes.  

---  

## 2. Core Components  

| Component | Language | Description | Key Interfaces |
|-----------|----------|-------------|----------------|
| **UI (frontend)** | TypeScript (React) | Render editor panes, tabs, status bar, settings UI. | `window.editorAPI` (Tauri bridge) |
| **Renderer** | Rust → WASM | Fast line‑by‑line rendering, token‑based syntax highlighting using **tree‑sitter** grammars. | `render(bufferId, viewport)` |
| **Buffer Manager** | Rust | Immutable rope data structure (`xi‑rope`) for O(log n) edits, undo/redo stacks. | `createBuffer(path)`, `applyEdit(edit)`, `snapshot()` |
| **LSP Bridge** | Rust (async‑std) | Manages LSP client lifecycles, forwards diagnostics, completions, hover, etc. | `request(method, params)`, `notify(event)` |
| **Plugin Loader** | Rust (dlopen) | Loads compiled plugins at runtime, registers RPC methods. | `loadPlugin(path)`, `unloadPlugin(id)` |
| **Settings Service** | Rust + TOML | Persists user preferences, theme, keymaps. | `get(key)`, `set(key, value)` |
| **File Watcher** | Rust (`notify` crate) | Detects external file changes, triggers reload prompts. | `watch(path)`, `unwatch(path)` |
| **Update Manager** | Rust | Self‑update via GitHub releases (delta patches). | `checkForUpdates()`, `applyUpdate()` |

---  

## 3. Data Model  

### 3.1 Buffer  

```ts
type BufferId = string; // UUID v4
interface Buffer {
  id: BufferId;
  path: string;          // absolute filesystem path
  rope: Rope;            // internal immutable rope (xi-rope)
  languageId: string;   // e.g., "rust", "python"
  version: number;      // incremented on each edit
  dirty: boolean;
}
```

### 3.2 Edit  

```ts
interface TextEdit {
  start: Position;   // { line: number, character: number }
  end: Position;
  newText: string;
}
```

### 3.3 LSP Diagnostic  

```ts
interface Diagnostic {
  range: Range;
  severity: 1|2|3|4;
  code?: string | number;
  source?: string;
  message: string;
}
```

### 3.4 Plugin Manifest  

```toml
name = "my-plugin"
version = "0.1.0"
description = "Adds custom command palette entries"
entrypoint = "libmy_plugin.so"
rpc_methods = ["myCommand"]
```

---  

## 4. Key APIs / Interfaces  

### 4.1 Tauri Bridge (Rust ↔︎ JS)

| JS Call | Rust Handler | Description |
|---------|--------------|-------------|
| `editorAPI.openFile(path: string)` | `open_file` | Loads file into a new buffer, returns `BufferId`. |
| `editorAPI.applyEdits(bufferId, edits[])` | `apply_edits` | Applies batch edits atomically. |
| `editorAPI.getDiagnostics(bufferId)` | `get_diagnostics` | Returns latest LSP diagnostics. |
| `editorAPI.invokePlugin(method, params)` | `invoke_plugin` | Calls a plugin RPC method. |
| `editorAPI.updateSettings(key, value)` | `set_setting` | Persists user preference. |

### 4.2 Plugin JSON‑RPC  

All plugins communicate over a **JSON‑RPC 2.0** channel. Example request:

```json
{
  "jsonrpc": "2.0",
  "id": "1234",
  "method": "myCommand",
  "params": { "bufferId": "abcd-1234", "selection": {...} }
}
```

Responses follow the standard JSON‑RPC schema.

### 4.3 LSP Bridge (internal)

```rust
pub async fn request<T: DeserializeOwned>(
    method: &str,
    params: impl Serialize,
) -> Result<T>;
```

Supported methods: `textDocument/completion`, `textDocument/hover`, `textDocument/diagnostic`, `workspace/symbol`, etc.

---  

## 5. Technology Stack  

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **UI** | React 18 + TypeScript, TailwindCSS | Declarative UI, fast dev cycles, small bundle size. |
| **Desktop Shell** | Tauri 1.6 (Rust) | Minimal runtime (~3 MB), native OS integration, security sandbox. |
| **Core Engine** | Rust 1.73, `xi-rope`, `tree-sitter`, `serde_json` | Zero‑cost abstractions, memory safety, proven performance. |
| **WASM** | `wasm-bindgen`, `wasm-pack` | Allows the same engine to run in the UI process for hot‑reload. |
| **Async Runtime** | `async-std` (via vLLM compatibility layer) | Uniform async model across LSP bridge and plugin loading. |
| **Plugin System** | `libloading` (dlopen), `jsonrpc-core` | Dynamic extensibility without recompiling the editor. |
| **File Watching** | `notify` crate (cross‑platform) | Efficient OS‑level change notifications. |
| **Packaging** | Cargo + `tauri-bundler`, GitHub Releases (delta patches) | Reproducible builds, easy self‑update. |
| **Testing** | `cargo test`, `jest` (frontend), `playwright` (e2e) | Full stack coverage. |
| **CI/CD** | GitHub Actions, `cargo-audit`, `cargo-deny` | Security scanning, reproducible pipelines. |

---  

## 6. Dependencies  

| Dependency | Version | License |
|------------|---------|---------|
| `tauri` | 1.6.0 | MIT / Apache‑2.0 |
| `react` | 18.2.0 | MIT |
| `tree-sitter` | 0.20.8 | MIT |
| `xi-rope` | 0.3.0 | MIT |
| `async-std` | 1.12.0 | MIT |
| `serde` / `serde_json` | 1.0.188 | MIT/Apache‑2.0 |
| `libloading` | 0.8.0 | MIT |
| `notify` | 6.1.1 | MIT |
| `jsonrpc-core` | 18.0.0 | MIT |
| `vllm‑compatible-runtime` (internal) | 0.1.0 | Apache‑2.0 |
| `tailwindcss` | 3.3.2 | MIT |

All dependencies are vetted for CVE‑free status via `cargo-audit` in CI.

---  

## 7. Deployment & Distribution  

1. **Build Pipeline** (GitHub Actions)  
   - `cargo build --release` (core + plugins)  
   - `wasm-pack build --target web` (renderer)  
   - `npm ci && npm run build` (React UI)  
   - `tauri build` → platform‑specific installers (`.exe`, `.dmg`, `.AppImage`).  

2. **Self‑Update Mechanism**  
   - On startup, `Update Manager` queries `https://github.com/arkashira/editor-flyte/releases/latest`.  
   - If a newer semver is found, downloads the delta patch (`.bsdiff`) and applies it atomically.  

3. **Packaging**  
   - **Windows**: MSI (MSI‑based installer) + portable ZIP.  
   - **macOS**: `.dmg` with code signing (Apple Developer ID).  
   - **Linux**: `.AppImage` and `.deb` (community repo).  

4. **Runtime Requirements**  
   - No external runtime; all native code bundled.  
   - Optional: User can install external LSP servers; editor‑flyte will auto‑detect via `$PATH` or `settings.lspPath`.  

---  

## 8. Security & Privacy  

| Concern | Mitigation |
|---------|------------|
| **Plugin Isolation** | Plugins run in the same process but communicate only via JSON‑RPC; all inputs validated against a schema. Future version may sandbox via `wasmtime`. |
| **File Access** | Explicit user consent required for each opened file; no background scanning. |
| **Update Integrity** | Releases signed with GPG; binary signature verified before applying patches. |
| **Telemetry** | Disabled by default; opt‑in via `settings.telemetry = true`. Data collected is anonymized (editor events only). |
| **Dependency Audits** | `cargo-deny` checks licenses and CVEs on every PR. |

---  

## 9. Testing Strategy  

| Test Type | Scope | Tools |
|-----------|-------|-------|
| Unit | Core engine (rope ops, syntax highlighting, LSP bridge) | `cargo test`, `criterion` for benchmarks |
| Integration | UI ↔︎ Core bridge, plugin loading, file watcher | `tauri-driver`, `jest` |
| End‑to‑End | Full editor workflow (open → edit → save → diagnostics) | `playwright` (Chromium headless) |
| Performance | Startup time < 500 ms, edit latency < 2 ms per operation on typical 10 k LOC file | Custom benchmark harness, record via `perf` |
| Security | Dependency scanning, fuzzing of JSON‑RPC | `cargo fuzz`, `npm audit` |

All CI jobs must pass ≥ 90 % code coverage before merge.

---  

## 10. Future Enhancements (Post‑v1.0)  

| Feature | Priority | Notes |
|---------|----------|-------|
| **Sandboxed Plugin Runtime** | High | Use `wasmtime` to run plugins in WASM sandbox. |
| **Collaborative Editing** | Medium | CRDT layer (e.g., `automerge`) over rope. |
| **Native Terminal Pane** | Medium | Embed `zellij` or `alacritty` via PTY. |
| **AI‑assisted Code Completion** | Low | Integrate with `vLLM` inference server for local LLM completions. |
| **Theme Marketplace** | Low | UI‑driven plugin for theme distribution. |

---  

## 11. Glossary  

- **Rope** – A balanced tree data structure optimized for large text buffers and frequent edits.  
- **LSP** – Language Server Protocol, a standardized way for editors to communicate with language analysis services.  
- **Tauri** – A framework for building tiny, secure desktop applications with a Rust backend and any web frontend.  
- **JSON‑RPC** – Remote Procedure Call protocol encoded in JSON, version 2.0.  

---  

*Prepared by:* Senior Product/Engineering Lead – editor‑flyte  
*Date:* 2026‑06‑19  

---
