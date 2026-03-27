local stringify = pandoc.utils.stringify

local function esc_html(s)
  s = s or ""
  s = s:gsub("&", "&amp;")
  s = s:gsub("<", "&lt;")
  s = s:gsub(">", "&gt;")
  s = s:gsub("\"", "&quot;")
  s = s:gsub("'", "&#39;")
  return s
end

local function kw(kwargs, key)
  local v = kwargs[key]
  if v == nil then
    return ""
  end
  return stringify(v)
end

local function split(str, sep)
  local t = {}
  if str == nil or str == "" then
    return t
  end
  sep = sep or "|"
  local pattern = "([^" .. sep .. "]+)"
  for part in str:gmatch(pattern) do
    table.insert(t, part)
  end
  return t
end

local function render_tags_panel(tags_param)
  -- tags_param format: "name:count|name:count|..."
  local pills = {}
  for _, item in ipairs(split(tags_param, "|")) do
    local name, count = item:match("^(.-):(.-)$")
    name = esc_html(name or item)
    count = esc_html(count or "")
    if count ~= "" then
      table.insert(pills,
        '<span class="tag-pill"><span class="tag-name">' .. name .. '</span><span class="tag-count">' .. count .. '</span></span>'
      )
    else
      table.insert(pills,
        '<span class="tag-pill"><span class="tag-name">' .. name .. '</span></span>'
      )
    end
  end

  local html = {}
  table.insert(html, '<aside class="tags-panel">')
  table.insert(html, '<div class="tags-panelTitle">Tags</div>')
  table.insert(html, '<div class="tag-pillWrap">' .. table.concat(pills, "\n") .. '</div>')
  table.insert(html, '</aside>')
  return table.concat(html, "\n")
end

local function render_project_card(kwargs)
  local href = esc_html(kw(kwargs, "href"))
  local thumb = esc_html(kw(kwargs, "thumb_src"))
  local title = esc_html(kw(kwargs, "title"))
  local meta = esc_html(kw(kwargs, "meta"))
  local org = esc_html(kw(kwargs, "org"))
  local excerpt = esc_html(kw(kwargs, "excerpt"))
  local tags_param = kw(kwargs, "tags")
  local pinned = kw(kwargs, "pinned")
  local variant = kw(kwargs, "variant")

  local classes = { "project-card" }
  if pinned == "true" then table.insert(classes, "is-pinned") end
  if variant == "hero" then table.insert(classes, "is-hero") end
  if variant == "fullwidth" then table.insert(classes, "is-fullwidth") end

  local tag_spans = {}
  for _, t in ipairs(split(tags_param, "|")) do
    table.insert(tag_spans, '<span class="project-tag">' .. esc_html(t) .. '</span>')
  end

  local html = {}
  table.insert(html, '<article class="' .. table.concat(classes, " ") .. '">')
  if thumb ~= "" then
    table.insert(html, '<a class="project-thumbLink" href="' .. href .. '"><img class="project-thumb" src="' .. thumb .. '" alt="' .. title .. ' thumbnail" loading="lazy" /></a>')
  end
  table.insert(html, '<div class="project-body">')
  table.insert(html, '<div class="project-head">')
  if pinned == "true" then table.insert(html, '<span class="project-badge">Pinned</span>') end
  table.insert(html, '<a class="project-title" href="' .. href .. '">' .. title .. '</a>')
  if meta ~= "" then table.insert(html, '<div class="project-meta">' .. meta .. '</div>') end
  if org ~= "" then table.insert(html, '<div class="project-org">' .. org .. '</div>') end
  table.insert(html, '</div>')
  if excerpt ~= "" then table.insert(html, '<p class="project-excerpt">' .. excerpt .. '</p>') end
  if #tag_spans > 0 then
    table.insert(html, '<div class="project-tags">' .. table.concat(tag_spans, "\n") .. '</div>')
  end
  table.insert(html, '</div>')
  table.insert(html, '</article>')
  return table.concat(html, "\n")
end

return {
  ["tags_panel"] = function(args, kwargs)
    local tags = kw(kwargs, "tags")
    return pandoc.RawBlock("html", render_tags_panel(tags))
  end,

  ["project_card"] = function(args, kwargs)
    return pandoc.RawBlock("html", render_project_card(kwargs))
  end
}

