local weekdays = { "日", "一", "二", "三", "四", "五", "六" }

local date_formats = {
  datetime = {
    { type = "date", format = "%Y-%m-%d %H:%M:%S" },
  },
  date = {
    { type = "date", format = "%Y-%m-%d" },
    { type = "date", format = "%Y.%m.%d" },
    { type = "date", format = "%Y/%m/%d" },
    { type = "date", format = "%Y年%m月%d日" },
    { type = "date", format = "%Y%m%d" },
    { type = "date", format = "%m-%d-%Y" },
  },
  time = {
    { type = "time", format = "%H:%M" },
    { type = "time", format = "%Y%m%d%H%M%S" },
    { type = "time", format = "%H:%M:%S" },
    { type = "time", format = "%H%M%S" },
  },
  month = {
    { type = "month", format = "%B" },
    { type = "month", format = "%b", comment = "缩写" },
  },
}

local function yield_formatted_candidates(input, seg)
  local formats = date_formats[input]
  if not formats then
    return false
  end

  for _, item in ipairs(formats) do
    yield(Candidate(item.type, seg.start, seg._end, os.date(item.format), item.comment or ""))
  end
  return true
end

local function yield_week_candidates(seg)
  local weekday = weekdays[tonumber(os.date("%w")) + 1]

  yield(Candidate("week", seg.start, seg._end, "周" .. weekday, ""))
  yield(Candidate("week", seg.start, seg._end, "星期" .. weekday, ""))
  yield(Candidate("week", seg.start, seg._end, os.date("%A"), ""))
  yield(Candidate("week", seg.start, seg._end, os.date("%a"), "缩写"))
  yield(Candidate("week", seg.start, seg._end, os.date("%W"), "周数"))
end

local function rime_datetime_translator(input, seg)
  if yield_formatted_candidates(input, seg) then
    return
  end

  if input == "week" then
    yield_week_candidates(seg)
  end
end

return rime_datetime_translator
