-- Random artwork for the WesCode start screen.
--
-- Artworks live under lua/custom/art/gallery/h<rows>/<name>.txt, one
-- directory per height tier (see generate.py). Each file is:
--   line 1 : title
--   line 2 : artist / origin
--   rest   : the artwork, coloured with 24-bit ANSI escapes
--            (ESC[38;2;R;G;Bm ... ESC[0m). Uncoloured text is fine too.
local M = {}

M.dir = vim.fs.joinpath(vim.fn.stdpath 'config', 'lua', 'custom', 'art', 'gallery')

--- Available height tiers, ascending (e.g. { 12, 18, 24, 32, 40 }).
function M.tiers()
  local tiers = {}
  for name, kind in vim.fs.dir(M.dir) do
    local rows = name:match '^h(%d+)$'
    if kind == 'directory' and rows then
      tiers[#tiers + 1] = tonumber(rows)
    end
  end
  table.sort(tiers)
  return tiers
end

--- Largest tier whose height is <= `rows`; falls back to the smallest.
function M.tier_for(rows)
  local tiers = M.tiers()
  local best = tiers[1]
  for _, t in ipairs(tiers) do
    if t <= rows then
      best = t
    end
  end
  return best
end

--- Sorted artwork names in a tier (defaults to the smallest tier).
function M.list(tier)
  tier = tier or M.tiers()[1]
  local names = {}
  local dir = vim.fs.joinpath(M.dir, 'h' .. tier)
  for name, kind in vim.fs.dir(dir) do
    if (kind == 'file' or kind == 'link') and name:match '%.txt$' then
      names[#names + 1] = (name:gsub('%.txt$', ''))
    end
  end
  table.sort(names)
  return names
end

-- Split one ANSI-coloured line into { { text = ..., color = 'RRGGBB'|nil }, ... },
-- merging adjacent cells that share a colour.
local function parse_line(line)
  local runs, color, buf = {}, nil, {}
  local function flush()
    if #buf > 0 then
      runs[#runs + 1] = { text = table.concat(buf), color = color }
      buf = {}
    end
  end
  local i, n = 1, #line
  while i <= n do
    local r, g, b, esc_end = line:match('^\27%[38;2;(%d+);(%d+);(%d+)m()', i)
    if not esc_end then
      esc_end = line:match('^\27%[[0-9;]*m()', i)
      if esc_end then
        i = esc_end
      else
        -- One UTF-8 character (braille is 3 bytes).
        local ch = line:match('^[%z\1-\127\194-\244][\128-\191]*', i)
        buf[#buf + 1] = ch
        i = i + #ch
      end
    else
      local c = ('%02x%02x%02x'):format(tonumber(r), tonumber(g), tonumber(b))
      if c ~= color then
        flush()
        color = c
      end
      i = esc_end
    end
  end
  flush()
  return runs
end

--- Load one artwork. Returns nil if it does not exist.
---@return { name: string, title: string, artist: string, tier: integer,
---          lines: table[], plain: string[] }|nil
function M.load(name, tier)
  tier = tier or M.tiers()[1]
  local path = vim.fs.joinpath(M.dir, 'h' .. tier, name .. '.txt')
  if vim.fn.filereadable(path) ~= 1 then
    return nil
  end
  local raw = vim.fn.readfile(path)
  local title = table.remove(raw, 1) or name
  local artist = table.remove(raw, 1) or ''
  while raw[1] and raw[1]:match '^%s*$' do
    table.remove(raw, 1)
  end
  while raw[#raw] and raw[#raw]:match '^%s*$' do
    table.remove(raw)
  end
  local lines, plain = {}, {}
  for i, l in ipairs(raw) do
    lines[i] = parse_line(l)
    local parts = {}
    for _, run in ipairs(lines[i]) do
      parts[#parts + 1] = run.text
    end
    plain[i] = table.concat(parts)
  end
  return { name = name, title = title, artist = artist, tier = tier, lines = lines, plain = plain }
end

--- Random artwork from a tier. Returns nil when the gallery is empty.
function M.random(tier)
  local names = M.list(tier)
  if #names == 0 then
    return nil
  end
  return M.load(names[math.random(#names)], tier)
end

return M
