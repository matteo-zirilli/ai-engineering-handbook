--[[
deep.lua — "deep dive" blocks for the Essentials / Full reading modes.

Authoring syntax (inside any .qmd file):

  ::: {.deep}                          a deep dive (technical detail, history, extra code)
  ## Title of the deep dive            optional first header = title shown on the bar
  ...content...
  :::

  ::: {.deep kind="proof"}             a proof
  ## Proof of @thm-something
  ...
  :::

Whole sections are marked on their heading instead:  ## Heading {.deep}
(handled in the browser by styles/deep-mode.html).

The filter runs BEFORE Quarto's own filters, so the title header is removed
here (it must not become a numbered section) while its inlines keep their
cross-references and citations, which Quarto resolves afterwards.
]]

local counter = 0

local function title_from_attr(text)
  local doc = pandoc.read(text, "markdown")
  if #doc.blocks > 0 and doc.blocks[1].content then
    return doc.blocks[1].content
  end
  return pandoc.Inlines(text)
end

function Div(el)
  if not el.classes:includes("deep") then
    return nil
  end
  counter = counter + 1
  local kind = el.attributes["kind"] or "deep"
  local blocks = el.content
  local title
  if #blocks > 0 and blocks[1].t == "Header" then
    title = blocks[1].content
    blocks = pandoc.Blocks({ table.unpack(blocks, 2) })
  elseif el.attributes["title"] then
    title = title_from_attr(el.attributes["title"])
  else
    title = pandoc.Inlines(kind == "proof" and "Proof" or "Deep dive")
  end

  local id = el.identifier
  if id == nil or id == "" then
    id = "deep-" .. counter
  end

  local summary = pandoc.Div({ pandoc.Plain(title) }, pandoc.Attr("", { "deep-summary" }))
  local body = pandoc.Div(blocks, pandoc.Attr("", { "deep-body" }))
  local attrs = { ["data-kind"] = kind }
  return pandoc.Div({ summary, body }, pandoc.Attr(id, { "deep", "deep-" .. kind }, attrs))
end
