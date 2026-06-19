# ROADMAP.md – editor‑flyte

## Vision
Deliver a **lightweight, high‑performance code editor** that feels instant, stays out of the way, and never freezes—giving developers a reliable alternative to heavyweight IDEs.

---

## Milestones Overview

| Milestone | Target Release | Core Theme | MVP‑Critical Items* |
|-----------|----------------|------------|----------------------|
| **MVP**   | **2026‑09‑30** | **Speed & Stability** | ✅ Core editor engine  <br>✅ File system integration (open/save) <br>✅ Syntax highlighting for top 10 languages <br>✅ Minimal UI (tabs, status bar) <br>✅ Persistent settings (theme, font) <br>✅ Crash‑free start‑up & exit |
| **v1.0**  | 2026‑12‑15 | **Productivity Boost** | ✅ Multi‑cursor editing <br>✅ Search / Replace (regex) <br>✅ Integrated terminal <br>✅ Extension API (first‑party plugins) <br>✅ Theme marketplace (dark/light) |
| **v2.0**  | 2027‑04‑01 | **Collaboration & Extensibility** | ✅ Real‑time pair programming (WebSocket) <br>✅ Workspace/project view <br>✅ LSP integration for diagnostics & autocomplete <br>✅ Plugin marketplace (community) <br>✅ Performance telemetry dashboard |

\*Items marked **MVP‑Critical** must be shipped for the initial launch; any missing item will block the MVP release.

---

## Detailed Roadmap

### 1️⃣ MVP – “Flyte Core” (Target: 2026‑09‑30)

| Epic | User Story | Acceptance Criteria | Owner |
|------|------------|----------------------|-------|
| **Editor Engine** | As a developer, I want a **blazingly fast text buffer** so that typing never lags. | • 0 ms latency for inserts/deletes up to 10 k lines.<br>• Memory usage ≤ 30 MiB for a 5 MB file.<br>• Built on `vLLM`‑style zero‑copy data structures. | Lead Engineer |
| **File I/O** | Open and save files without UI freezes. | • Open ≤ 50 ms for 5 MB file.<br>• Save ≤ 30 ms.<br>• Auto‑detect encoding, preserve line endings. | Engineer |
| **Syntax Highlighting** | Highlight code for the most common languages. | • Support: JavaScript, Python, Go, Rust, Java, C/C++, TypeScript, HTML, CSS, JSON.<br>• Theme‑aware (light/dark). | Engineer |
| **UI Skeleton** | Provide a minimal, distraction‑free interface. | • Tab bar, status bar (line/col, file size, encoding).<br>• Keyboard‑driven navigation (Ctrl+P, Ctrl+Shift+F). | UI/UX |
| **Settings Persistence** | Remember user preferences across sessions. | • Store theme, font family/size, tab width in a JSON config in `$XDG_CONFIG_HOME/editor-flyte`. | Engineer |
| **Stability** | Ensure the editor never crashes on normal usage. | • 0 crash reports in automated stress suite (10 k random edits, 1 k open/close cycles).<br>• Graceful error handling for I/O failures. | QA |
| **CI/CD & Release** | Automate builds and publish binaries for macOS, Linux, Windows. | • GitHub Actions pipeline with static analysis, unit tests, and signed artifacts.<br>• Versioned releases on GitHub. | DevOps |

**MVP Success Metric:** ≥ 95 % of surveyed beta users report “no noticeable lag” and “no crashes” after 1 week of daily use.

---

### 2️⃣ v1.0 – “Flyte Productivity Suite” (Target: 2026‑12‑15)

| Epic | Feature | Description | MVP‑Critical? |
|------|---------|-------------|---------------|
| **Multi‑Cursor** | Simultaneous editing at multiple locations. | Mirrors VS Code’s multi‑cursor with column selection. | No |
| **Search / Replace** | Powerful find/replace with regex, case‑sensitivity, whole‑word options. | UI panel, incremental results, “replace all”. | No |
| **Integrated Terminal** | Embedded shell (bash/zsh/pwsh) inside the editor. | Toggle with `Ctrl+``. Supports copy/paste to/from editor. | No |
| **Extension API** | First‑party plugin system (JS/TS). | Allows adding commands, custom themes, file watchers. | No |
| **Theme Marketplace** | Curated set of dark/light themes. | UI to switch instantly; themes stored as JSON. | No |
| **Performance Dashboard** | Real‑time metrics (CPU, memory, latency) in a hidden panel. | Helps power users tune settings. | No |

**v1 Success Metric:** ≥ 70 % of MVP users adopt at least one new productivity feature within 30 days.

---

### 3️⃣ v2.0 – “Flyte Collaboration & Ecosystem” (Target: 2027‑04‑01)

| Epic | Feature | Description | MVP‑Critical? |
|------|---------|-------------|---------------|
| **Live Collaboration** | Real‑time pair programming (multiple cursors, chat). | Peer‑to‑peer via WebSocket; optional server relay for NAT traversal. | No |
| **Workspace/Project View** | Tree view of folders, git status overlay. | Drag‑and‑drop, multi‑root workspaces. | No |
| **Language Server Protocol (LSP) Integration** | Plug‑and‑play language features (diagnostics, autocomplete, go‑to‑definition). | Auto‑detect LSP servers, fallback to built‑in diagnostics. | No |
| **Plugin Marketplace** | Community‑driven extensions (npm‑style). | Search, install, auto‑update from within editor. | No |
| **Telemetry & Opt‑in Analytics** | Anonymous performance & usage data to guide future optimizations. | Dashboard for maintainers; privacy‑first defaults. | No |
| **Cross‑Platform Sync** | Sync settings & extensions via encrypted cloud store. | Optional, OAuth‑based. | No |

**v2 Success Metric:** ≥ 30 % of active users enable live collaboration; marketplace hosts ≥ 50 community plugins within 6 months of launch.

---

## Release Process

1. **Feature Freeze** – 2 weeks before each target date.  
2. **Beta Ramp‑Up** – Invite existing MVP users to test upcoming features.  
3. **Automated Regression Suite** – 10 k+ unit + integration tests run on every PR.  
4. **Performance Gate** – No new feature may increase average keystroke latency > 5 ms.  
5. **Final QA Sign‑off** – Manual exploratory testing + crash‑report audit.  

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Performance regression** | Core promise broken | Continuous latency monitoring; performance budget enforced in CI. |
| **Extension security** | Malicious plugins could compromise system | Sandbox plugin runtime (Node VM with limited globals). |
| **Cross‑platform UI inconsistencies** | Poor user experience | Use a single rendering layer (Electron‑lite or Tauri) with native widgets abstracted. |
| **Collaboration latency** | Real‑time editing feels laggy | Peer‑to‑peer fallback, adaptive sync interval, QoS monitoring. |

---

## Metrics Dashboard (post‑launch)

| KPI | Target (MVP) | Target (v1) | Target (v2) |
|-----|--------------|-------------|-------------|
| Avg. keystroke latency | ≤ 5 ms | ≤ 4 ms | ≤ 3 ms |
| Crash rate (per 10 k sessions) | 0 | ≤ 1 | ≤ 0.5 |
| Daily Active Users (DAU) | 5 k | 12 k | 25 k |
| Feature adoption (multi‑cursor, LSP) | N/A | ≥ 40 % | ≥ 60 % |
| Marketplace extensions installed | N/A | N/A | ≥ 2 k total installs |

--- 

*Prepared by the editor‑flyte product team, 2026‑06‑19.*
