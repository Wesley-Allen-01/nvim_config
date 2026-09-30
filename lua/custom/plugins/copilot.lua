-- Keep the editor usable without Node.js on a restricted Windows laptop.
-- Once Node is on PATH, restart Neovim to load Copilot.
if vim.fn.executable 'node' == 1 then
  vim.g.copilot_no_tab_map = true -- Blink owns <Tab>.
  vim.pack.add { 'https://github.com/github/copilot.vim' }
end
