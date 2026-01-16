-- Wezterm configuration example

local wezterm = require 'wezterm'
local config = wezterm.config_builder()

-- Colors (Tomorrow Night theme)
config.colors = {
  foreground = "#c5c8c6",
  background = "#1d1f21",
  cursor_bg = "#c5c8c6",
  cursor_fg = "#1d1f21",
  selection_bg = "#373b41",
  selection_fg = "#c5c8c6",
  ansi = { "#1d1f21", "#cc6666", "#b5bd68", "#f0c674", "#81a2be", "#b294bb", "#8abeb7", "#c5c8c6" },
  brights = { "#969896", "#cc6666", "#b5bd68", "#f0c674", "#81a2be", "#b294bb", "#8abeb7", "#ffffff" },
}

-- Font
config.font = wezterm.font("JetBrains Mono")
config.font_size = 14.0
config.line_height = 1.1

-- Cursor
config.default_cursor_style = "BlinkingBlock"
config.cursor_blink_rate = 500

-- Window
config.initial_cols = 120
config.initial_rows = 40
config.window_background_opacity = 0.95
config.window_padding = {
  left = 10,
  right = 10,
  top = 10,
  bottom = 10,
}
config.window_decorations = "FULL"

-- Behavior
config.default_prog = { "/bin/zsh" }
config.scrollback_lines = 10000
config.audible_bell = "Disabled"
config.visual_bell = {
  fade_in_function = "EaseIn",
  fade_in_duration_ms = 50,
  fade_out_function = "EaseOut",
  fade_out_duration_ms = 50,
}

-- Key bindings
config.keys = {
  { key = "c", mods = "CTRL|SHIFT", action = wezterm.action.CopyTo("Clipboard") },
  { key = "v", mods = "CTRL|SHIFT", action = wezterm.action.PasteFrom("Clipboard") },
  { key = "t", mods = "CTRL|SHIFT", action = wezterm.action.SpawnTab("CurrentPaneDomain") },
}

return config
