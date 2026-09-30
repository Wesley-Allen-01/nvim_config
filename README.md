# Wesley's Neovim config

This is the **Windows-compatible branch** of my [kickstart.nvim](https://github.com/nvim-lua/kickstart.nvim) setup. Start with [WINDOWS.md](WINDOWS.md) for a native Windows installation and a list of differences from `master`. The main configuration lives in `init.lua`; personal plugins and mappings live under `lua/custom/plugins/`. The leader key is **Space**.

## Getting started

Use Neovim 0.12 or newer. Clone this branch into `%LOCALAPPDATA%\nvim` and start `nvim` in PowerShell; see [WINDOWS.md](WINDOWS.md) for portable-tool and administrator-install options. `vim.pack` installs plugins from GitHub using Git and the committed `nvim-pack-lock.json`.

The editor starts without a Nerd Font, C compiler, Tree-sitter CLI, or Mason language tools. Install the optional tools you need later. `:checkhealth`, `:Mason`, `:Telescope keymaps`, and `:lua vim.pack.update()` are useful maintenance commands.

## What's installed

| Area | Plugins and behavior |
| --- | --- |
| Interface | Tokyo Night (`tokyonight-night`), which-key hints, mini.statusline, and automatic indentation detection with guess-indent. Nerd Font icons are disabled by default. |
| Start screen | mini.starter with a lightweight **Hi Wesley** greeting and recent files. The artwork gallery is omitted from this branch. |
| Files and search | mini.files for browsing; Telescope for files, buffers, grep, help, keymaps, diagnostics, and LSP results. Telescope UI select is enabled; the native FZF extension is omitted on Windows. |
| Editing | mini.ai text objects, mini.surround, mini.comment, and todo-comments. Installed Tree-sitter parsers provide enhanced highlighting and indentation; parser installation is manual on this branch. mini.comment toggles **line** comments across a visual selection, using the filetype's comment syntax. |
| Git | gitsigns for signs, hunk actions, blame, and diff views. |
| Languages | Neovim LSP with Mason, mason-lspconfig, nvim-lspconfig, and fidget status messages. Configured servers: `clangd`, `rust_analyzer`, `ty`, `ruff`, `ts_ls`, and `lua_ls`; Mason can install these tools and `stylua` on request; automatic tool installation on startup is disabled. |
| Formatting | conform.nvim runs Ruff fixes, formatting, and import organization on Python save. `<leader>f` formats on demand. Other filetypes use LSP formatting when a server supports it. |
| Completion | blink.cmp supplies LSP, path, and LuaSnip completion. GitHub's `copilot.vim` shows inline suggestions when Node.js is on PATH; it is skipped otherwise. Blink owns `<Tab>`: it accepts a visible Copilot suggestion first, then a Blink completion, then advances a snippet, then inserts a tab. |

Tree-sitter uses parsers already installed in your Neovim data directory. Install or update parsers manually once the Tree-sitter CLI and a C compiler are available. `clangd` works best with a project `compile_commands.json`.

## Keymaps

`<leader>` means **Space**. The tables cover the custom and kickstart mappings used most often; `:Telescope keymaps` (Space `sk`) and which-key show the full active list. Some LSP and Git mappings appear only when their server or buffer is active.

| Keys | Mode | Action |
| --- | --- | --- |
| `<leader>e` | Normal | Open mini.files at the current file. |
| `<leader>/` | Normal | Fuzzy search the current buffer. |
| `<leader>/` | Visual | Toggle line comments on the selected lines. `gc` also works in Visual mode; `gcc` toggles the current line. |
| `<leader><leader>` | Normal | Find open buffers. |
| `<leader>sf` / `<leader>sg` | Normal | Find files / live grep the project. |
| `<leader>sw` | Normal, Visual | Search the word or selection. |
| `<leader>sh` / `<leader>sk` / `<leader>sc` | Normal | Search help / keymaps / commands. |
| `<leader>sd` / `<leader>sr` / `<leader>s.` | Normal | Search diagnostics / resume search / recent files. |
| `<leader>s/` / `<leader>sn` | Normal | Grep open files / find Neovim config files. |
| `<leader>f` | Normal, Visual | Format with conform.nvim. |
| `<leader>cf` / `<leader>ci` | Normal, Python | Apply Ruff fixes / organize imports. |
| `<leader>wn` / `<leader>wd` | Normal | Open a new right split / close the current window. |
| `<leader>wh`, `wj`, `wk`, `wl` | Normal | Focus the left, lower, upper, or right window. |
| `<C-h>`, `<C-j>`, `<C-k>`, `<C-l>` | Normal | Focus splits in the same four directions. |
| `jj` | Insert | Return to Normal mode. |
| `<Tab>` | Insert | Accept Copilot, Blink completion, or next snippet placeholder; otherwise insert a tab. |
| `<C-l>` | Insert, with Node.js | Accept the next word of a Copilot suggestion. |
| `<Esc><Esc>` | Terminal | Return to Normal mode. |

| Keys | Mode | Action |
| --- | --- | --- |
| `gd` / `grd` | Normal, LSP | Go to definition. |
| `gb` | Normal | Go back to the previous jump location. |
| `grD` / `gri` / `grt` | Normal, LSP | Go to declaration / implementation / type definition. |
| `grr` / `grn` / `gra` | Normal, LSP | Find references / rename / code action. |
| `gO` / `gW` | Normal, LSP | Find document / workspace symbols. |
| `<leader>th` | Normal, LSP | Toggle inlay hints when supported. |
| `]c` / `[c` | Normal, Git buffer | Next / previous changed hunk. |
| `<leader>hs` / `<leader>hr` | Normal, Visual, Git buffer | Stage / reset a hunk or selection. |
| `<leader>hS` / `<leader>hR` | Normal, Git buffer | Stage / reset all changes in the buffer. |
| `<leader>hp` / `<leader>hi` | Normal, Git buffer | Preview hunk / inline preview. |
| `<leader>hb` / `<leader>hd` / `<leader>hD` | Normal, Git buffer | Blame line / diff against index / diff against last commit. |
| `<leader>hq` / `<leader>hQ` | Normal, Git buffer | Quickfix changes in this file / all files. |
| `<leader>tb` / `<leader>tw` | Normal, Git buffer | Toggle line blame / word diff. |

## Files and customization

- `init.lua`: editor options and the main plugin setup.
- `lua/custom/plugins/init.lua`: loads each `.lua` file in that directory. `keymaps.lua` holds personal shortcuts, `copilot.lua` configures Copilot, and `starter.lua` defines the start screen.
- `lua/kickstart/plugins/`: optional upstream examples; only `gitsigns.lua` is currently loaded.

The `master` branch keeps the full artwork setup. The `upstream` Git remote points to kickstart.nvim for updates. Personal mappings are kept in `lua/custom/plugins/keymaps.lua` so they are easier to preserve when pulling upstream changes.
