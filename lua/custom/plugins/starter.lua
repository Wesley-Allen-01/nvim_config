-- WesCode start screen: a banner plus a randomly chosen work of art rendered
-- as coloured braille (see lua/custom/art/). Built on mini.starter, which
-- init.lua already installs as part of mini.nvim.
--
--   :WesArt            reshuffle the artwork on the current start screen
--   :WesArt <name>     show a specific artwork (tab-completes)
--   :WesArt list       list every artwork in the gallery
local starter = require 'mini.starter'
local art = require 'custom.art'

-- Seed once per session so each launch gets a different painting.
math.randomseed(os.time() + vim.fn.getpid())

local banner = {
  [[██╗    ██╗███████╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗]],
  [[██║    ██║██╔════╝██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝]],
  [[██║ █╗ ██║█████╗  ███████╗██║     ██║   ██║██║  ██║█████╗  ]],
  [[██║███╗██║██╔══╝  ╚════██║██║     ██║   ██║██║  ██║██╔══╝  ]],
  [[╚███╔███╔╝███████╗███████║╚██████╗╚██████╔╝██████╔╝███████╗]],
  [[ ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝]],
}

-- Fallback highlight for uncoloured artwork lines.
vim.api.nvim_set_hl(0, 'WesCodeArt', { link = 'Special', default = true })

-- Rows taken by everything other than the artwork: banner + blank, the
-- items block (section headers, items, blank separators), footer + blank,
-- plus the status line and command line.
local MENU_ROWS = 11
local function art_rows_available()
  return vim.o.lines - (#banner + 1) - MENU_ROWS - 2 - 2
end

-- mini.starter re-evaluates the header on every refresh (e.g. while typing a
-- query), so remember which artwork each start-screen buffer is showing.
local shown = {} ---@type table<integer, table|false>
local forced = nil ---@type string|nil

local function current_art()
  local buf = vim.api.nvim_get_current_buf()
  if shown[buf] == nil then
    local tier = art.tier_for(art_rows_available())
    local piece = forced and art.load(forced, tier) or nil
    forced = nil
    shown[buf] = piece or art.random(tier) or false
    vim.api.nvim_create_autocmd('BufWipeout', {
      buffer = buf,
      once = true,
      callback = function()
        shown[buf] = nil
      end,
    })
  end
  return shown[buf] or nil
end

local function header()
  local lines = vim.list_extend({}, banner)
  local piece = current_art()
  if piece then
    lines[#lines + 1] = ''
    vim.list_extend(lines, piece.plain)
  end
  return table.concat(lines, '\n')
end

local function footer()
  local piece = current_art()
  if not piece then
    return 'No artwork found in ' .. art.dir
  end
  return ('%s  ·  %s'):format(piece.title, piece.artist)
end

-- One highlight group per colour, created on demand.
local hl_cache = {}
local function color_hl(hex)
  local name = 'WesCodeArt_' .. hex
  if not hl_cache[name] then
    vim.api.nvim_set_hl(0, name, { fg = '#' .. hex })
    hl_cache[name] = true
  end
  return name
end

-- Content hook: header lines are emitted in order, so everything after the
-- banner (and its blank separator) is the artwork. Replace each of those
-- single-unit lines with one unit per coloured run.
local function colorize_art(content)
  local piece = current_art()
  local n = 0
  for _, line in ipairs(content) do
    for idx, unit in ipairs(line) do
      if unit.type == 'header' then
        n = n + 1
        local row = n - #banner - 1
        if row >= 1 and piece and piece.lines[row] then
          table.remove(line, idx)
          for j, run in ipairs(piece.lines[row]) do
            table.insert(line, idx + j - 1, {
              type = 'header',
              string = run.text,
              hl = run.color and color_hl(run.color) or 'WesCodeArt',
            })
          end
          break -- this line is done; its unit list was rebuilt
        end
      end
    end
  end
  return content
end

starter.setup {
  evaluate_single = true,
  header = header,
  footer = footer,
  items = {
    starter.sections.builtin_actions(),
    { name = 'Shuffle artwork', action = 'WesArt', section = 'Builtin actions' },
    starter.sections.recent_files(5, false),
  },
  content_hooks = {
    colorize_art,
    starter.gen_hook.adding_bullet(),
    starter.gen_hook.aligning('center', 'center'),
  },
}

vim.api.nvim_create_user_command('WesArt', function(opts)
  local arg = opts.args
  if arg == 'list' then
    local names = art.list()
    vim.notify(('%d artworks:\n%s'):format(#names, table.concat(names, '\n')))
    return
  end
  if arg ~= '' then
    if not art.load(arg) then
      vim.notify('No artwork named ' .. arg, vim.log.levels.ERROR)
      return
    end
    forced = arg
  end
  local buf = vim.api.nvim_get_current_buf()
  if vim.bo[buf].filetype == 'ministarter' then
    shown[buf] = nil
    starter.refresh(buf)
  else
    starter.open()
  end
end, {
  nargs = '?',
  complete = function(lead)
    return vim.tbl_filter(function(n)
      return n:find(lead, 1, true) == 1
    end, vim.list_extend({ 'list' }, art.list()))
  end,
  desc = 'Show a random (or named) artwork on the WesCode start screen',
})
