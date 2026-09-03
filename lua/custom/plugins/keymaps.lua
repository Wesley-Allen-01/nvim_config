-- Your own keymaps. Loaded last (see the `require 'custom.plugins'` at the end
-- of init.lua), so anything set here wins over plugin defaults.
--
-- Upstream kickstart never touches this directory, so keymaps kept here survive
-- a `git merge upstream/master` without conflicts.

-- Open mini.files at the current file, falling back to the cwd for scratch
-- buffers. `g?` inside the explorer lists every mapping.
vim.keymap.set('n', '<leader>e', function()
  local name = vim.api.nvim_buf_get_name(0)
  MiniFiles.open(vim.fn.filereadable(name) == 1 and name or nil)
end, { desc = '[E]xplore files' })

vim.keymap.set('i', 'jj', '<esc>', {desc = 'return to normal mode from insert'})
