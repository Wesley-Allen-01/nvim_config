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

vim.keymap.set('i', 'jj', '<esc>', { desc = 'Return to normal mode from insert' })

-- Accept Copilot ghost text one word at a time; <Tab> accepts the full suggestion.
if vim.fn.executable 'node' == 1 then
  vim.keymap.set('i', '<C-l>', '<Plug>(copilot-accept-word)', { desc = 'Copilot: Accept next word' })
end

-- Return to the previous location after a jump, such as `gd`.
vim.keymap.set('n', 'gb', '<C-o>', { desc = '[G]o [B]ack' })

-- Window creation and navigation. `splitright` is enabled in init.lua, so
-- `:vnew` consistently opens the new empty window on the right.
vim.keymap.set('n', '<leader>wn', '<cmd>vnew<CR>', { desc = 'Window: New on right' })
vim.keymap.set('n', '<leader>wd', '<cmd>close<CR>', { desc = 'Window: Close current' })
vim.keymap.set('n', '<leader>wh', '<C-w>h', { desc = 'Window: Focus left' })
vim.keymap.set('n', '<leader>wj', '<C-w>j', { desc = 'Window: Focus below' })
vim.keymap.set('n', '<leader>wk', '<C-w>k', { desc = 'Window: Focus above' })
vim.keymap.set('n', '<leader>wl', '<C-w>l', { desc = 'Window: Focus right' })

require('which-key').add {
  { '<leader>w', group = '[W]indows' },
}
