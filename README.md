# Wesley's Neovim config

My Neovim setup, based on [kickstart.nvim](https://github.com/nvim-lua/kickstart.nvim). The main configuration lives in `init.lua`; personal plugins and mappings live under `lua/custom/plugins/`. The leader key is **Space**.

## Getting started

This config uses `vim.pack`, so use Neovim 0.12 or newer. Clone the repo into `~/.config/nvim` (or your Neovim config directory) and start `nvim`. `vim.pack` installs the declared plugins and uses the committed `nvim-pack-lock.json` to select their revisions. A Nerd Font is enabled in the config; turn off `vim.g.have_nerd_font` in `init.lua` if you do not use one.

For the full experience, install `git`, `ripgrep` (for live grep), `make` and a C compiler (for Telescope's optional native FZF matcher), and the language toolchains you use. Mason manages the configured language servers and Stylua. GitHub Copilot needs Node.js and a Copilot account; run `:Copilot setup` once to authenticate, then `:Copilot status` to check it.

Use `:checkhealth` for general diagnostics, `:Mason` for language tools, and `:lua vim.pack.update()` when you want to update plugins. Update and commit `nvim-pack-lock.json` with intentional plugin upgrades.

## What's installed

| Area | Plugins and behavior |
| --- | --- |
| Interface | Tokyo Night (`tokyonight-night`), which-key hints, mini.statusline, mini.icons, and automatic indentation detection with guess-indent. |
| Start screen | mini.starter with a rotating colored artwork gallery in `lua/custom/art/`. `:WesArt` reshuffles it, `:WesArt <name>` picks a piece, and `:WesArt list` shows names. |
| Files and search | mini.files for browsing; Telescope for files, buffers, grep, help, keymaps, diagnostics, and LSP results. Telescope UI select and the native FZF matcher are enabled when available. |
| Editing | mini.ai text objects, mini.surround, mini.comment, Tree-sitter highlighting and indentation, and todo-comments. mini.comment toggles **line** comments across a visual selection, using the filetype's comment syntax. |
| Git | gitsigns for signs, hunk actions, blame, and diff views. |
| Languages | Neovim LSP with Mason, mason-lspconfig, nvim-lspconfig, and fidget status messages. Configured servers: `clangd`, `rust_analyzer`, `ty`, `ruff`, `ts_ls`, and `lua_ls`; Mason also installs `stylua`. |
| Formatting | conform.nvim runs Ruff fixes, formatting, and import organization on Python save. `<leader>f` formats on demand. Other filetypes use LSP formatting when a server supports it. |
| Completion | blink.cmp supplies LSP, path, and LuaSnip completion. GitHub's `copilot.vim` shows inline suggestions. Blink owns `<Tab>`: it accepts a visible Copilot suggestion first, then a Blink completion, then advances a snippet, then inserts a tab. |

Tree-sitter installs a base set of parsers (`bash`, `c`, `diff`, `html`, `lua`, `luadoc`, `markdown`, `markdown_inline`, `query`, `vim`, `vimdoc`) and can install others when their filetype is opened. `clangd` works best with a project `compile_commands.json`.

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
| `<C-l>` | Insert | Accept the next word of a Copilot suggestion. |
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
- `lua/custom/art/`: start screen gallery and its generator.
- `lua/kickstart/plugins/`: optional upstream examples; only `gitsigns.lua` is currently loaded.
- `CUSTOMIZATION.md`: older ideas and notes; use this README and the Lua source for current behavior.

The `upstream` Git remote points to kickstart.nvim for updates. Personal mappings are kept in `lua/custom/plugins/keymaps.lua` so they are easier to preserve when pulling upstream changes.
