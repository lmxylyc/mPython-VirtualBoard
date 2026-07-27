"""
mPython Virtual Board - 现代主题系统
提供深色/浅色主题、统一配色、现代化控件样式
"""

import tkinter as tk
from tkinter import ttk


# ========== 深色主题配色 ==========
class DarkTheme:
    BG = "#1e1e2e"
    BG_PANEL = "#282838"
    BG_CARD = "#333344"
    BG_INPUT = "#191925"
    BG_HOVER = "#3d3d54"

    FG = "#cdd6f4"
    FG_MUTED = "#a6adc8"
    FG_DIM = "#6c7086"
    FG_ACCENT = "#89b4fa"

    ACCENT = "#89b4fa"
    ACCENT_HOVER = "#b4befe"
    ACCENT_DIM = "#585b70"

    SUCCESS = "#a6e3a1"
    WARNING = "#f9e2af"
    ERROR = "#f38ba8"
    INFO = "#89dceb"

    OLED_BG = "#0a0a1a"
    OLED_FG = "#a6e3a1"
    OLED_FRAME = "#111122"
    OLED_GLOW = "#a6e3a1"

    RGB_OFF = "#313244"
    RGB_OUTLINE = "#45475a"

    BORDER = "#45475a"
    BORDER_LIGHT = "#585b70"

    BUTTON_BG = "#313244"
    BUTTON_HOVER = "#45475a"
    BUTTON_FG = "#cdd6f4"

    EDITOR_BG = "#181825"
    EDITOR_FG = "#cdd6f4"
    EDITOR_LINE = "#313244"

    OUTPUT_BG = "#11111b"
    OUTPUT_FG = "#bac2de"

    TREE_BG = "#1e1e2e"
    TREE_HEAD = "#313244"

    FONT_MAIN = ("Segoe UI", 10)
    FONT_MONO = ("Consolas", 10)
    FONT_TITLE = ("Segoe UI", 13, "bold")
    FONT_SMALL = ("Segoe UI", 8)
    FONT_TINY = ("Segoe UI", 7)
    FONT_BTN = ("Segoe UI", 9)


# ========== 浅色主题配色 ==========
class LightTheme:
    BG = "#eff1f5"
    BG_PANEL = "#e6e9ef"
    BG_CARD = "#dce0e8"
    BG_INPUT = "#ffffff"
    BG_HOVER = "#ccd0da"

    FG = "#4c4f69"
    FG_MUTED = "#6c6f85"
    FG_DIM = "#9ca0b0"
    FG_ACCENT = "#1e66f5"

    ACCENT = "#1e66f5"
    ACCENT_HOVER = "#2a6cf5"
    ACCENT_DIM = "#bcc0cc"

    SUCCESS = "#40a02b"
    WARNING = "#df8e1d"
    ERROR = "#d20f39"
    INFO = "#179299"

    OLED_BG = "#11111b"
    OLED_FG = "#90d17d"
    OLED_FRAME = "#181825"
    OLED_GLOW = "#90d17d"

    RGB_OFF = "#ccd0da"
    RGB_OUTLINE = "#bcc0cc"

    BORDER = "#bcc0cc"
    BORDER_LIGHT = "#e6e9ef"

    BUTTON_BG = "#ccd0da"
    BUTTON_HOVER = "#bcc0cc"
    BUTTON_FG = "#4c4f69"

    EDITOR_BG = "#ffffff"
    EDITOR_FG = "#4c4f69"
    EDITOR_LINE = "#e6e9ef"

    OUTPUT_BG = "#ffffff"
    OUTPUT_FG = "#4c4f69"

    TREE_BG = "#ffffff"
    TREE_HEAD = "#e6e9ef"

    FONT_MAIN = ("Segoe UI", 10)
    FONT_MONO = ("Consolas", 10)
    FONT_TITLE = ("Segoe UI", 13, "bold")
    FONT_SMALL = ("Segoe UI", 8)
    FONT_TINY = ("Segoe UI", 7)
    FONT_BTN = ("Segoe UI", 9)


def apply_theme(root, theme_class=DarkTheme):
    """将主题应用到 Tk 根窗口"""
    t = theme_class()

    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    root.configure(bg=t.BG)

    style.configure('TFrame', background=t.BG)
    style.configure('TLabel', background=t.BG, foreground=t.FG, font=t.FONT_MAIN)
    style.configure('TLabelframe', background=t.BG, foreground=t.FG, font=t.FONT_MAIN, borderwidth=1)
    style.configure('TLabelframe.Label', background=t.BG, foreground=t.FG_ACCENT,
                    font=("Segoe UI", 10, "bold"))

    style.configure('TButton',
                    background=t.BUTTON_BG,
                    foreground=t.BUTTON_FG,
                    font=t.FONT_BTN,
                    padding=(12, 6),
                    borderwidth=0,
                    focusthickness=0)
    style.map('TButton',
              background=[('active', t.BUTTON_HOVER), ('pressed', t.ACCENT_DIM)],
              foreground=[('disabled', t.FG_DIM)])

    style.configure('Accent.TButton',
                    background=t.ACCENT,
                    foreground=t.BG,
                    font=("Segoe UI", 10, "bold"),
                    padding=(14, 7),
                    borderwidth=0)
    style.map('Accent.TButton',
              background=[('active', t.ACCENT_HOVER), ('pressed', t.ACCENT_DIM)])

    style.configure('Success.TButton',
                    background=t.SUCCESS,
                    foreground=t.BG,
                    font=("Segoe UI", 9, "bold"),
                    padding=(10, 6),
                    borderwidth=0)
    style.map('Success.TButton',
              background=[('active', t.ACCENT_HOVER)])

    style.configure('Danger.TButton',
                    background=t.ERROR,
                    foreground=t.BG,
                    font=("Segoe UI", 9, "bold"),
                    padding=(10, 6),
                    borderwidth=0)

    style.configure('TNotebook', background=t.BG, borderwidth=0)
    style.configure('TNotebook.Tab',
                    background=t.BUTTON_BG,
                    foreground=t.FG,
                    padding=(16, 8),
                    font=t.FONT_BTN)
    style.map('TNotebook.Tab',
              background=[('selected', t.ACCENT), ('active', t.BUTTON_HOVER)],
              foreground=[('selected', t.BG)])

    style.configure('TEntry',
                    fieldbackground=t.BG_INPUT,
                    foreground=t.FG,
                    insertcolor=t.FG,
                    borderwidth=1)
    style.map('TEntry',
              fieldbackground=[('focus', t.BG_INPUT)],
              bordercolor=[('focus', t.ACCENT)])

    style.configure('TCombobox',
                    fieldbackground=t.BG_INPUT,
                    background=t.BUTTON_BG,
                    foreground=t.FG,
                    arrowcolor=t.FG)

    style.configure('TScrollbar',
                    background=t.BUTTON_BG,
                    troughcolor=t.BG_INPUT,
                    arrowcolor=t.FG,
                    borderwidth=0)
    style.configure('TScrollbar.vertical', width=10)
    style.configure('TScrollbar.horizontal', height=10)

    style.configure('TScale',
                    background=t.BG,
                    troughcolor=t.ACCENT_DIM,
                    sliderthickness=14)

    style.configure('TCheckbutton',
                    background=t.BG,
                    foreground=t.FG,
                    font=t.FONT_MAIN)

    style.configure('TRadiobutton',
                    background=t.BG,
                    foreground=t.FG,
                    font=t.FONT_MAIN)

    style.configure('TSeparator',
                    background=t.BORDER)

    style.configure('Horizontal.TProgressbar',
                    background=t.ACCENT,
                    troughcolor=t.BG_INPUT,
                    borderwidth=0,
                    thickness=6)

    style.configure('Treeview',
                    background=t.TREE_BG,
                    foreground=t.FG,
                    fieldbackground=t.TREE_BG,
                    rowheight=26,
                    borderwidth=0,
                    font=t.FONT_MAIN)
    style.configure('Treeview.Heading',
                    background=t.TREE_HEAD,
                    foreground=t.FG,
                    font=("Segoe UI", 9, "bold"),
                    borderwidth=0)
    style.map('Treeview',
              background=[('selected', t.ACCENT_DIM)],
              foreground=[('selected', t.FG)])

    style.configure('Vertical.PanedWindow',
                    background=t.BG,
                    sashwidth=4,
                    sashrelief='flat')

    style.configure('Horizontal.PanedWindow',
                    background=t.BG,
                    sashwidth=4,
                    sashrelief='flat')

    style.configure('Menu',
                    background=t.BG_PANEL,
                    foreground=t.FG,
                    borderwidth=0,
                    tearoff=False)

    style.configure('MenuItem',
                    background=t.BG_PANEL,
                    foreground=t.FG)

    root.option_add('*Menu*background', t.BG_PANEL)
    root.option_add('*Menu*foreground', t.FG)
    root.option_add('*Menu*selectColor', t.BG)
    root.option_add('*Menu*selectBackground', t.ACCENT)

    return t
