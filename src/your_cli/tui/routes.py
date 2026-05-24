"""Central route registry.

This is the ONLY file that maps route keys to screen modules.
To add, remove, or rename a route edit only this file.
"""

from your_cli.tui.router import register

# ── Hub ──────────────────────────────────────────────────────────────────────
register("gallery",               "your_cli.tui.features.gallery.screen",               "GalleryScreen")

# ── Non-demo screens ──────────────────────────────────────────────────────────
register("dashboard",             "your_cli.tui.features.dashboard.screen",             "DashboardScreen")

# ── Demo screens (alphabetical within each group) ────────────────────────────
register("apifiles",              "your_cli.tui.features.api_files.screen",             "ApiFilesDemoScreen")
register("autocomplete",          "your_cli.tui.features.autocomplete.screen",          "AutocompleteDemoScreen")
register("cards",                 "your_cli.tui.features.cards.screen",                 "CardsDemoScreen")
register("cards2",                "your_cli.tui.features.cards2.screen",                "Cards2DemoScreen")
register("cmdpalette",            "your_cli.tui.features.command_palette.screen",       "CommandPaletteDemoScreen")
register("contentswitcher",       "your_cli.tui.features.content_switcher.screen",      "ContentSwitcherDemoScreen")
register("contextmenu",           "your_cli.tui.features.context_menu.screen",          "ContextMenuDemoScreen")
register("customwidget",          "your_cli.tui.features.custom_widget.screen",         "CustomWidgetDemoScreen")
register("data",                  "your_cli.tui.features.data_display.screen",          "DataDemoScreen")
register("dicomnrrd",             "your_cli.tui.features.dicom_nrrd.screen",            "DicomNrrdDemoScreen")
register("files",                 "your_cli.tui.features.file_manager.screen",          "FilesDemoScreen")
register("formtable",             "your_cli.tui.features.form_table.screen",            "FormTableDemoScreen")
register("formvalidation",        "your_cli.tui.features.form_validation.screen",       "FormValidationDemoScreen")
register("helpkeys",              "your_cli.tui.features.help_keys.screen",             "HelpKeysDemoScreen")
register("inlineedit",            "your_cli.tui.features.inline_edit.screen",           "InlineEditDemoScreen")
register("inputs",                "your_cli.tui.features.inputs.screen",                "InputsDemoScreen")
register("labelform",             "your_cli.tui.features.label_form.screen",            "LabelFormDemoScreen")
register("layout",                "your_cli.tui.features.layout.screen",                "LayoutDemoScreen")
register("link",                  "your_cli.tui.features.link.screen",                  "LinkDemoScreen")
register("live",                  "your_cli.tui.features.live_dashboard.screen",        "LiveDashboardScreen")
register("log",                   "your_cli.tui.features.log.screen",                   "LogDemoScreen")
register("logstream",             "your_cli.tui.features.log_stream.screen",            "LogStreamDemoScreen")
register("maskedinput",           "your_cli.tui.features.masked_input.screen",          "MaskedInputDemoScreen")
register("masterdetail",          "your_cli.tui.features.master_detail.screen",         "MasterDetailDemoScreen")
register("masterdetailvertical",  "your_cli.tui.features.master_detail_vertical.screen","MasterDetailVerticalScreen")
register("multiselect",           "your_cli.tui.features.multiselect.screen",           "MultiSelectDemoScreen")
register("notifydrawer",          "your_cli.tui.features.notification_drawer.screen",   "NotificationDrawerDemoScreen")
register("optionlist",            "your_cli.tui.features.option_list.screen",           "OptionListDemoScreen")
register("pagination",            "your_cli.tui.features.pagination.screen",            "PaginationDemoScreen")
register("pretty",                "your_cli.tui.features.pretty.screen",                "PrettyDemoScreen")
register("progress",              "your_cli.tui.features.progress.screen",              "ProgressDemoScreen")
register("report",                "your_cli.tui.features.report.screen",                "ReportDemoScreen")
register("rule",                  "your_cli.tui.features.rule.screen",                  "RuleDemoScreen")
register("searchfilter",          "your_cli.tui.features.search_filter.screen",         "SearchFilterDemoScreen")
register("searchgrid",            "your_cli.tui.features.search_grid.screen",           "SearchGridDemoScreen")
register("selectionlist",         "your_cli.tui.features.selection_list.screen",        "SelectionListDemoScreen")
register("settings",              "your_cli.tui.features.settings.screen",              "SettingsDemoScreen")
register("tabs",                  "your_cli.tui.features.tabs.screen",                  "TabsDemoScreen")
register("theme",                 "your_cli.tui.features.theme_toggle.screen",          "ThemeToggleDemoScreen")
register("togglebutton",          "your_cli.tui.features.toggle_button.screen",         "ToggleButtonDemoScreen")
register("tooltip",               "your_cli.tui.features.tooltip.screen",               "TooltipDemoScreen")
register("wizard",                "your_cli.tui.features.wizard.screen",                "WizardDemoScreen")
register("workers",               "your_cli.tui.features.workers.screen",               "WorkersDemoScreen")
