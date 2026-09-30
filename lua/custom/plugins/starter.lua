-- Lightweight Windows start screen; no artwork files or terminal font needed.
local starter = require 'mini.starter'

starter.setup {
  header = 'Hi Wesley',
  footer = 'Neovim on Windows',
  items = {
    starter.sections.builtin_actions(),
    starter.sections.recent_files(5, false),
  },
  content_hooks = {
    starter.gen_hook.adding_bullet(),
    starter.gen_hook.aligning('center', 'center'),
  },
}
