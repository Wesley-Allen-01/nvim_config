# Kickstart Customization Notes

Reference list of common modifications to this config. Apart from the three items marked
**DONE** in §1, nothing here is applied — this is a menu to work through once you've used
the setup and found what actually bothers you.

Environment verified 2026-09-03: Neovim 0.12.5, Ghostty, `JetBrainsMono Nerd Font`
installed, and `rg` / `fd` / `make` / `cc` / `node` / `npm` / `python3` all present.
No missing external dependencies.

Line numbers refer to `init.lua` as of the stock upstream checkout and will drift once
you start editing.

---

## 1. Decisions kickstart leaves explicitly open

These are marked in the source as "change this yourself." Everything else in this
document is optional; this section is the config asking you a direct question.

| Line | Setting | Current | Notes |
|------|---------|---------|-------|
| `102` | `vim.g.have_nerd_font` | **DONE** — `true` | JetBrainsMono Nerd Font is installed; Ghostty also has symbol fallback built in. Drives icons in mini.icons, which-key, telescope, gitsigns. |
| `694` | `servers` table | **DONE** — see §2 | `clangd`, `rust_analyzer`, `pyright`, `ruff`, `ts_ls`, `lua_ls`. `gopls` left commented. |
| `972-977` | Optional kickstart modules | all commented | Six opt-in plugin modules. See §3. |
| `992` | `require 'custom.plugins'` | **DONE** — enabled | The auto-loader in `lua/custom/plugins/init.lua` now runs, so any `.lua` file you drop in that directory is picked up automatically. It was silently ignored before. |
| `785` | `format_on_save` | disabled | `enabled_filetypes` is empty, so nothing formats on save. See §4. |
| `801` | `formatters_by_ft` | empty | External formatters (prettier, black, rustfmt). See §4. |
| `396` | Colorscheme | `tokyonight-night` | Variants already available: `-storm`, `-moon`, `-day`. |
| `910` | Treesitter parsers | 9 base parsers | Low priority — others auto-install on first FileType. |

Lower-stakes toggles in the same category:

| Line | Setting | Current | Notes |
|------|---------|---------|-------|
| `113` | `relativenumber` | commented | Worth trying if you use `5j` / `12k` style motions. |
| `198` | `virtual_lines` | `false` | Diagnostics below the line instead of at end-of-line. Nice for long Rust/TS errors. Common approach is a keymap to toggle between the two. |
| `923` | Treesitter folds | commented | Only enable if you actually fold. Also set `vim.o.foldlevel = 99` or every file opens collapsed. |
| `173` | `confirm` | `true` | Prompts to save on `:q` instead of erroring. Some people find this annoying. |
| `830` | `friendly-snippets` | commented | Large premade snippet library for LuaSnip. |

---

## 2. Language servers

**Currently enabled** in the `servers` table at `init.lua:694`, covering Python, Rust,
C/C++, JavaScript and TypeScript:

| Server | Language | Note |
|--------|----------|------|
| `clangd` | C / C++ | Wants a `compile_commands.json` in the project root — see below. |
| `rust_analyzer` | Rust | Swap for `rustaceanvim` if you want inlay hints and macro expansion. Never both. |
| `pyright` | Python | Type checking. |
| `ruff` | Python | Linting; can also format via conform. |
| `ts_ls` | JS / TS | `typescript-tools.nvim` is faster on large projects. |
| `lua_ls` | Lua | Configured by kickstart, formatting delegated to stylua. |

**clangd needs a compile database.** Without `compile_commands.json` it falls back to
guessing flags and will report bogus missing-include errors. Generate it with:

```sh
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B build   # CMake
bear -- make                                        # plain Make (brew install bear)
```

Symlink it to the project root if CMake put it in `build/`. This is the single most
common cause of "clangd is broken."

Others worth adding later:

```lua
gopls = {}, jsonls = {}, yamlls = {}, bashls = {},
html = {}, cssls = {}, taplo = {}, marksman = {},
```

**Gotcha:** everything in this table is passed to `vim.lsp.config()` and `vim.lsp.enable()`
at `init.lua:770`. Upstream puts `stylua` (a formatter, not a server) in here purely so
`mason-tool-installer` picks it up via `vim.tbl_keys(servers)`. It's harmless because it
has no `filetypes` and never attaches — but don't follow that pattern. Put formatters and
linters in the `vim.list_extend(ensure_installed, {...})` list at `init.lua:764` instead:

```lua
vim.list_extend(ensure_installed, {
  'prettierd', 'black', 'isort', 'shfmt', 'eslint_d',
})
```

Verify with `:Mason`, `:LspInfo`, and `:checkhealth vim.lsp`.

---

## 3. The six optional modules

Uncomment at `init.lua:972-977`. Each is a self-contained file in `lua/kickstart/plugins/`.

| Module | What it adds | Recommendation |
|--------|--------------|----------------|
| `gitsigns` | Hunk navigation/stage/reset keymaps under `<leader>h` | **Enable.** The plugin is already loaded at line 353; this only adds keymaps. |
| `lint` | nvim-lint, linters that aren't language servers | **Enable** if you write JS/Python/shell. |
| `autopairs` | nvim-autopairs | Enable, or use `mini.pairs` (§5) since mini is already downloaded. |
| `indent_line` | indent-blankline guides | Taste. Some find it visual noise. |
| `neo-tree` | Sidebar file tree | **Skip.** Telescope plus `mini.files` (§5) covers this better and lighter. |
| `debug` | nvim-dap + UI + adapters | Only if you'll actually step-debug. Heaviest of the six. |

---

## 4. Formatting

Two independent decisions.

**A. Which external formatters** — `formatters_by_ft` at `init.lua:801`:

```lua
formatters_by_ft = {
  lua = { 'stylua' },
  python = { 'ruff_format' },          -- or { 'isort', 'black' } sequentially
  javascript = { 'prettierd', 'prettier', stop_after_first = true },
  typescript = { 'prettierd', 'prettier', stop_after_first = true },
  rust = { 'rustfmt' },
  go = { 'gofmt' },
  sh = { 'shfmt' },
},
```

**B. Format on save, and for what** — `init.lua:785`. Currently opt-in per filetype:

```lua
local enabled_filetypes = { lua = true, python = true, rust = true, go = true }
```

Formatting on save in a shared repo without a committed formatter config will produce
noisy diffs. Safer default: leave save-formatting off and use the existing `<leader>f`
keymap manually until you know a project's conventions.

A common addition is a toggle command so you can disable it per-buffer:

```lua
vim.api.nvim_create_user_command('FormatToggle', function()
  vim.b.disable_autoformat = not vim.b.disable_autoformat
end, {})
```

(and check `vim.b.disable_autoformat` inside the `format_on_save` function).

---

## 5. Free wins — mini.nvim modules already downloaded

`mini.nvim` is installed in full at `init.lua:404`, but only `icons`, `ai`, `surround`,
and `statusline` are set up. These cost one line each, no new downloads:

```lua
require('mini.files').setup()      -- file explorer; replaces neo-tree
require('mini.diff').setup()       -- inline diff hunks in the gutter
require('mini.bufremove').setup()  -- close a buffer without killing its window
require('mini.pairs').setup()      -- autopairs
require('mini.move').setup()       -- move lines/selections with alt+hjkl
require('mini.splitjoin').setup()  -- toggle one-line <-> multi-line args
require('mini.trailspace').setup() -- highlight/trim trailing whitespace
```

Add near the other mini setups around `init.lua:433`. Browse with `:h mini.nvim`.

---

## 6. Plugin categories kickstart deliberately omits

Pick from these only when you hit the need. This is where most "my config grew to 40
plugins" comes from, so be skeptical of each one.

**Git**
- `tpope/vim-fugitive` — the classic; `:G` for everything.
- `NeogitOrg/neogit` — magit-style UI.
- `sindrets/diffview.nvim` — reviewing branch diffs and merge conflicts.
- You already have `lazygit` on PATH; a simple float terminal binding may be all you need.

**Navigation / motion**
- `folke/flash.nvim` — jump to any visible location with 2 chars. High value.
- `ThePrimeagen/harpoon` (branch `harpoon2`) — pin 4-5 files, jump by index.
- `stevearc/oil.nvim` — edit the filesystem as a buffer. Alternative to mini.files.

**Session / project**
- `folke/persistence.nvim` — restore buffers and layout per directory.
- `rmagatti/auto-session` — heavier alternative.

**Editing**
- `mbbill/undotree` — visualize the undo history. `undofile` is already on at `init.lua:120`, so the data already exists.
- `windwp/nvim-ts-autotag` — auto-close HTML/JSX tags.
- `folke/trouble.nvim` — better diagnostics/quickfix list.

**Terminal**
- `akinsho/toggleterm.nvim` — persistent floating/split terminals.

**AI**
- `coder/claudecode.nvim` — Claude Code inside Neovim.
- `olimorris/codecompanion.nvim` — general chat/inline-edit.
- `zbirenbaum/copilot.lua` (+ a bridge plugin for blink.cmp).

**Language-specific**
- `mrcjkb/rustaceanvim` — replaces `rust_analyzer` config entirely; do not configure both.
- `pmizio/typescript-tools.nvim` — faster than `ts_ls` on large projects.

**Alternative pickers** (only if telescope frustrates you)
- `ibhagwan/fzf-lua` — faster on huge repos.
- `folke/snacks.nvim` picker — modern, bundles many small utilities.

---

## 7. Keymaps kickstart intentionally doesn't ship

Stock keymaps are: window nav `<C-hjkl>`, `<Esc>` to clear search highlight, `<Esc><Esc>`
to leave terminal mode, `<leader>q` diagnostics, `<leader>f` format, plus the telescope
and LSP sets. Commonly added:

```lua
-- Buffers
vim.keymap.set('n', '<S-h>', '<cmd>bprevious<CR>', { desc = 'Previous buffer' })
vim.keymap.set('n', '<S-l>', '<cmd>bnext<CR>', { desc = 'Next buffer' })

-- Save
vim.keymap.set({ 'n', 'i', 'v' }, '<C-s>', '<cmd>w<CR><Esc>', { desc = 'Save file' })

-- Keep the cursor centered
vim.keymap.set('n', '<C-d>', '<C-d>zz')
vim.keymap.set('n', '<C-u>', '<C-u>zz')
vim.keymap.set('n', 'n', 'nzzzv')
vim.keymap.set('n', 'N', 'Nzzzv')

-- Move selected lines
vim.keymap.set('v', 'J', ":m '>+1<CR>gv=gv", { desc = 'Move selection down' })
vim.keymap.set('v', 'K', ":m '<-2<CR>gv=gv", { desc = 'Move selection up' })

-- Paste over a selection without clobbering the register
vim.keymap.set('x', '<leader>p', [["_dP]], { desc = 'Paste without yanking' })

-- Stay in indent mode
vim.keymap.set('v', '<', '<gv')
vim.keymap.set('v', '>', '>gv')

-- Resize windows
vim.keymap.set('n', '<C-Up>', '<cmd>resize +2<CR>')
vim.keymap.set('n', '<C-Down>', '<cmd>resize -2<CR>')
```

Add these to the Section 2 block around `init.lua:180-230`.

---

## 8. Options commonly added

Not in stock kickstart, appended to the Section 1 block near `init.lua:170`:

```lua
vim.o.wrap = false           -- kickstart leaves wrap on
vim.o.colorcolumn = '100'    -- visual line-length guide
vim.o.tabstop = 2            -- guess-indent handles existing files, not new ones
vim.o.shiftwidth = 2
vim.o.expandtab = true
vim.o.pumheight = 10         -- cap completion popup height
vim.o.winborder = 'rounded'  -- 0.11+: rounded borders on all floats
```

Spellcheck for prose filetypes only:

```lua
vim.api.nvim_create_autocmd('FileType', {
  pattern = { 'markdown', 'gitcommit', 'text' },
  callback = function()
    vim.opt_local.spell = true
    vim.opt_local.wrap = true
  end,
})
```

---

## 9. Repository hygiene

- **DONE** — remotes are already set up the right way:
  ```
  origin    https://github.com/Wesley-Allen-01/nvim_config.git
  upstream  https://github.com/nvim-lua/kickstart.nvim.git
  ```
  `master` tracks `origin/master`. Pull in later kickstart changes with
  `git fetch upstream && git diff HEAD upstream/master -- init.lua` to review before
  merging — upstream rewrites `init.lua` freely, so expect conflicts once you've
  customized it.

- `.gitignore:11` ignores `nvim-pack-lock.json`. That's there so the *upstream* repo
  avoids merge conflicts. In your own fork, un-ignore and commit it — it's what makes
  plugin versions reproducible across machines. See `:h vim.pack-lockfile`.

- `.github/` (issue templates, PR template, stylua workflow) and `doc/kickstart.txt` are
  upstream's, not yours. Safe to delete once you've forked.

---

## 10. Diagnosing things before changing them

- `:checkhealth` — the single best starting point.
- This config uses `vim.pack`, not lazy.nvim. See `:h vim.pack`; inspect state with
  `:lua =vim.pack.get()`, update with `:lua vim.pack.update()`.
- `:LspInfo` / `:checkhealth vim.lsp` — which server attached, and why one didn't.
- `:Mason` — installed servers/formatters; `g?` for help inside it.
- `:ConformInfo` — which formatter conform would run for this buffer.
- `:Telescope keymaps` — search every keymap that's actually bound.
- `:Telescope help_tags` — search all documentation.
- `:messages` — errors that scrolled past on startup.
- `nvim --startuptime /tmp/st.log` — if startup feels slow.
- `:verbose set <option>?` — find which file set an option you didn't expect.
- `<leader>sk`, `<leader>sh`, `<leader>sf` — the stock telescope keymap/help/file pickers.
