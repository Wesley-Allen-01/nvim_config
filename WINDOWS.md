# Native Windows setup

This guide installs the `codex/windows-compatible` branch on Windows without WSL. It is designed to start as a usable editor with Neovim and Git alone, then add search, language tools, Copilot, and Tree-sitter as the laptop permits. Use only software sources and installation methods allowed by your workplace.

## 1. Get Neovim and Git

**No administrator rights:** Download the Windows ZIP from [Neovim releases](https://github.com/neovim/neovim/releases) and the x64 or ARM64 **Portable Git** package from [Git for Windows](https://git-scm.com/downloads/win). Extract both under a user-writable folder such as `%USERPROFILE%\Tools`. The Neovim ZIP needs no installer. Portable Git is a self-extracting archive; use its normal extraction flow so its setup finishes. The examples below assume `%USERPROFILE%\Tools\nvim-win64` and `%USERPROFILE%\Tools\PortableGit`; adjust them if you chose different folders.

In PowerShell, for the current session:

```powershell
$tools = Join-Path $env:USERPROFILE 'Tools'
$env:Path = "$(Join-Path $tools 'nvim-win64\bin');$(Join-Path $tools 'PortableGit\cmd');$env:Path"
nvim --version
git --version
```

For a lasting setup, add those two folders to your **user** PATH in Windows Environment Variables. The ZIP or portable package can be removed later without touching system installation folders.

**If administrator installation is approved:** Install [Neovim](https://github.com/neovim/neovim/blob/master/INSTALL.md#windows) and [Git for Windows](https://git-scm.com/downloads/win) with your organization's normal process. `winget install --id Neovim.Neovim -e` and `winget install --id Git.Git -e` are possible when winget and your policy allow them. Open a new PowerShell window and check `nvim --version` and `git --version`.

## 2. Clone this branch

Neovim reads its configuration from `%LOCALAPPDATA%\nvim`. Back up any existing folder there first. In PowerShell:

```powershell
git clone --branch codex/windows-compatible --single-branch https://github.com/Wesley-Allen-01/nvim_config.git (Join-Path $env:LOCALAPPDATA 'nvim')
nvim
```

On first launch, `vim.pack` uses Git to download plugins from GitHub. The committed `nvim-pack-lock.json` pins their revisions. If GitHub is blocked, ask for an approved mirror or approved pre-provisioned Neovim plugin directory. A ZIP of this config alone cannot supply its plugins.

## 3. Add optional tools

| Want | Add | What happens without it |
| --- | --- | --- |
| Project-wide live grep (`Space sg`) | [ripgrep](https://github.com/BurntSushi/ripgrep/releases): extract its Windows ZIP and put the folder containing `rg.exe` on PATH. | File and buffer search still work; Telescope live grep does not. |
| LSP diagnostics, navigation, and Ruff formatting | Mason's [Windows requirements](https://github.com/mason-org/mason.nvim#requirements): PowerShell, Git, GNU tar, and an archive tool such as 7-Zip. Some servers also need their language runtime (for example, Node.js for TypeScript). | Editing, comments, files, Git signs, and local search still work. LSP features and Python format-on-save depend on installed servers and Ruff. |
| Inline Copilot suggestions | Approved [Node.js](https://nodejs.org/en/download) installation or ZIP on PATH, GitHub Copilot access, then restart Neovim and run `:Copilot setup`. | Blink's local completion and snippets still work; `<Tab>` skips the Copilot step. |
| Tree-sitter parser highlighting and indentation | [tree-sitter CLI](https://github.com/tree-sitter/tree-sitter/releases), a C compiler, `tar`, and `curl`; see [nvim-treesitter requirements](https://github.com/nvim-treesitter/nvim-treesitter#requirements). | Neovim's built-in syntax and indentation remain. The config does not attempt parser compilation at startup. |
| Nerd Font icons | Install a Nerd Font, select it in your terminal, and change `vim.g.have_nerd_font` to `true` in `init.lua`. | Text UI works; icon glyphs are disabled by default. |

For Mason, Portable Git includes GNU tools, but its `usr\bin` folder may need to be on PATH for `tar.exe`; 7-Zip also needs its executable folder on PATH. Run `:checkhealth mason` to see what your actual machine is missing. Then open `:Mason` to install only the language tools you use, or run `:MasonToolsInstall` to attempt all configured tools. Automatic installation at startup is intentionally off. If a tool fails, check its Mason details and the required runtime rather than reinstalling the whole config.

After the Tree-sitter CLI and compiler are available, use `:TSInstall lua` (and other languages you want) and `:TSUpdate` after plugin upgrades. Tree-sitter parsers are optional; no parser builds run automatically.

If Node.js is on PATH when Neovim starts, use `:Copilot setup` and `:Copilot status`. Blink controls `<Tab>` so it accepts a visible Copilot suggestion first, then a Blink completion, then advances a snippet or inserts a tab.

## What differs from `master`

- The artwork gallery and `:WesArt` command are removed. The start screen says **Hi Wesley** and still shows recent files.
- Nerd Font icons are off by default.
- The native Telescope FZF matcher is excluded on Windows; Telescope's normal search remains.
- Tree-sitter parser installs and updates are manual, so no C compiler is needed for first startup.
- Mason language-tool installation is manual, avoiding background downloads and install errors on a restricted laptop.
- LuaSnip's optional `jsregexp` native extension is not built on Windows. The configured snippets and core completion still work.

The editor still needs GitHub access for first-run plugin downloads. Some language tools, Copilot, and clipboard integration also depend on the laptop's available runtimes, network, and terminal. Run `:checkhealth` after setup; use `:checkhealth vim.lsp`, `:checkhealth mason`, and `:Copilot status` for focused checks. If a terminal does not send a particular Ctrl key combination, use `:Telescope keymaps` to find an alternate action or adjust that mapping in `lua/custom/plugins/keymaps.lua`.
