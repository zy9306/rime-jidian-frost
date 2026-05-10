local kNoop = 2

local punct_inputs = {
  ["!"] = true,
  ['"'] = true,
  ["#"] = true,
  ["$"] = true,
  ["%"] = true,
  ["&"] = true,
  ["'"] = true,
  ["("] = true,
  [")"] = true,
  ["*"] = true,
  ["+"] = true,
  [","] = true,
  ["-"] = true,
  ["."] = true,
  ["/"] = true,
  [":"] = true,
  [";"] = true,
  ["<"] = true,
  ["="] = true,
  [">"] = true,
  ["?"] = true,
  ["@"] = true,
  ["["] = true,
  ["\\"] = true,
  ["]"] = true,
  ["^"] = true,
  ["_"] = true,
  ["`"] = true,
  ["{"] = true,
  ["|"] = true,
  ["}"] = true,
  ["~"] = true,
}

local function is_letter_key(key)
  local repr = key:repr()
  return repr ~= nil and repr:match("^[A-Za-z]$") ~= nil
end

local function punct_auto_commit_processor(key, env)
  if not is_letter_key(key) then
    return kNoop
  end

  local context = env.engine.context
  if not context:is_composing() or not punct_inputs[context.input] then
    return kNoop
  end

  local composition = context.composition
  if composition:empty() then
    return kNoop
  end

  local segment = composition:back()
  local candidate = segment:get_selected_candidate()
  if candidate == nil then
    return kNoop
  end

  env.engine:commit_text(candidate.text)
  context:clear()
  return kNoop
end

return punct_auto_commit_processor
