"""Central route registry — single source of truth for all screens.

This is the ONLY file that maps route keys to screen modules.
To add, remove, or rename a route edit only this file.

Gallery-visible screens carry display_name + description.  The order of
registration here is the order they appear in the gallery list.
Non-gallery screens (child screens pushed directly) omit display_name.
"""

from your_cli.tui.router import register

# ── Hub (not shown in gallery) ────────────────────────────────────────────────
register("gallery", "your_cli.tui.features.gallery.screen", "GalleryScreen")

# ── Gallery demos (registration order = gallery display order) ────────────────
register("inputs",
         "your_cli.tui.features.inputs.screen", "InputsDemoScreen",
         display_name="Inputs & Forms",
         description="Input, TextArea, Checkbox, Switch, Select, RadioSet, Button")

register("layout",
         "your_cli.tui.features.layout.screen", "LayoutDemoScreen",
         display_name="Layout & Navigation",
         description="Grid layout, Collapsible sections, Tree widget")

register("progress",
         "your_cli.tui.features.progress.screen", "ProgressDemoScreen",
         display_name="Progress & Feedback",
         description="ProgressBar, Digits, Sparkline, LoadingIndicator, Toast, Modal")

register("dashboard",
         "your_cli.tui.features.dashboard.screen", "DashboardScreen",
         display_name="Work Items Dashboard",
         description="The original two-pane dashboard with row drill-down")

register("files",
         "your_cli.tui.features.file_manager.screen", "FilesDemoScreen",
         display_name="File Manager",
         description="DirectoryTree navigation with file content preview")

register("apifiles",
         "your_cli.tui.features.api_files.screen", "ApiFilesDemoScreen",
         display_name="API File Browser",
         description="Tree populated from API calls with lazy loading")

register("live",
         "your_cli.tui.features.live_dashboard.screen", "LiveDashboardScreen",
         display_name="Live Dashboard",
         description="DataTable that auto-refreshes every 10 seconds via set_interval")

register("cmdpalette",
         "your_cli.tui.features.command_palette.screen", "CommandPaletteDemoScreen",
         display_name="Command Palette",
         description="Fuzzy-search overlay — filter and trigger any action with Ctrl+P")

register("logstream",
         "your_cli.tui.features.log_stream.screen", "LogStreamDemoScreen",
         display_name="Streaming Log",
         description="RichLog fed by an async worker — live scrolling log output")

register("wizard",
         "your_cli.tui.features.wizard.screen", "WizardDemoScreen",
         display_name="Multi-step Wizard",
         description="Step-by-step form with Back / Next / Submit and a review pane")

register("report",
         "your_cli.tui.features.report.screen", "ReportDemoScreen",
         display_name="Markdown Report",
         description="Report viewer with Markdown tables, code blocks, and callouts")

register("settings",
         "your_cli.tui.features.settings.screen", "SettingsDemoScreen",
         display_name="Settings Screen",
         description="Category sidebar with forms — resizable like other sidebars")

register("workers",
         "your_cli.tui.features.workers.screen", "WorkersDemoScreen",
         display_name="Concurrent Workers",
         description="Multiple @work tasks running in parallel with individual progress bars")

register("contextmenu",
         "your_cli.tui.features.context_menu.screen", "ContextMenuDemoScreen",
         display_name="Context Menu",
         description="Press Enter on a DataTable row to open a ModalScreen action menu")

register("inlineedit",
         "your_cli.tui.features.inline_edit.screen", "InlineEditDemoScreen",
         display_name="Inline Edit",
         description="Press E on a row to edit its fields in a panel below the table")

register("theme",
         "your_cli.tui.features.theme_toggle.screen", "ThemeToggleDemoScreen",
         display_name="Theme Toggle",
         description="Toggle dark / light mode at runtime with app.dark")

register("customwidget",
         "your_cli.tui.features.custom_widget.screen", "CustomWidgetDemoScreen",
         display_name="Custom Widgets",
         description="MetricCard and StatusBadge built from Widget with reactive render()")

register("formvalidation",
         "your_cli.tui.features.form_validation.screen", "FormValidationDemoScreen",
         display_name="Form Validation",
         description="Inline field errors with live re-validation after first submit")

register("pagination",
         "your_cli.tui.features.pagination.screen", "PaginationDemoScreen",
         display_name="Pagination",
         description="Browse 100 items in fixed-size pages with keyboard and button nav")

register("multiselect",
         "your_cli.tui.features.multiselect.screen", "MultiSelectDemoScreen",
         display_name="Multi-select Table",
         description="Space to toggle rows, A/D for all/none, bulk Run/Cancel actions")

register("contentswitcher",
         "your_cli.tui.features.content_switcher.screen", "ContentSwitcherDemoScreen",
         display_name="Content Switcher",
         description="Sidebar ListView driving ContentSwitcher panel swap without new screens")

register("helpkeys",
         "your_cli.tui.features.help_keys.screen", "HelpKeysDemoScreen",
         display_name="Help / Key Reference",
         description="Press ? to open a modal listing every active binding on the current screen")

register("optionlist",
         "your_cli.tui.features.option_list.screen", "OptionListDemoScreen",
         display_name="OptionList",
         description="OptionList with separators, highlight events, and selected-action feedback")

register("maskedinput",
         "your_cli.tui.features.masked_input.screen", "MaskedInputDemoScreen",
         display_name="Masked Input",
         description="MaskedInput with date, time, phone, job-ID, IPv4, and hex-color templates")

register("notifydrawer",
         "your_cli.tui.features.notification_drawer.screen", "NotificationDrawerDemoScreen",
         display_name="Notification Drawer",
         description="Accumulate notify() calls in a slide-in history panel with Clear")

register("autocomplete",
         "your_cli.tui.features.autocomplete.screen", "AutocompleteDemoScreen",
         display_name="Autocomplete Input",
         description="Input + SuggestFromList — Tab or → accepts the inline suggestion")

register("selectionlist",
         "your_cli.tui.features.selection_list.screen", "SelectionListDemoScreen",
         display_name="SelectionList",
         description="Checkbox-style multi-select with built-in state, pre-selection, and .selected")

register("togglebutton",
         "your_cli.tui.features.toggle_button.screen", "ToggleButtonDemoScreen",
         display_name="Toggle Button",
         description="Checkbox and RadioButton as standalone toggle widgets with Changed events")

register("rule",
         "your_cli.tui.features.rule.screen", "RuleDemoScreen",
         display_name="Rule",
         description="Horizontal and vertical dividers in every line style — solid, heavy, dashed, double")

register("tooltip",
         "your_cli.tui.features.tooltip.screen", "TooltipDemoScreen",
         display_name="Tooltip",
         description="widget.tooltip = text — hover any widget to see its tooltip")

register("pretty",
         "your_cli.tui.features.pretty.screen", "PrettyDemoScreen",
         display_name="Pretty",
         description="Pretty widget renders any Python object as syntax-highlighted formatted output")

register("link",
         "your_cli.tui.features.link.screen", "LinkDemoScreen",
         display_name="Link",
         description="Clickable Link widgets that open URLs via app.open_url()")

register("log",
         "your_cli.tui.features.log.screen", "LogDemoScreen",
         display_name="Log vs RichLog",
         description="Plain Log (no markup) side-by-side with RichLog — write, clear, max_lines")

register("tabs",
         "your_cli.tui.features.tabs.screen", "TabsDemoScreen",
         display_name="Tabs (standalone)",
         description="Tabs widget driving ContentSwitcher manually — dynamic add/remove at runtime")

register("masterdetail",
         "your_cli.tui.features.master_detail.screen", "MasterDetailDemoScreen",
         display_name="Master / Detail",
         description="Navigating a master DataTable populates a child step table in real time")

register("formtable",
         "your_cli.tui.features.form_table.screen", "FormTableDemoScreen",
         display_name="Form + Table",
         description="Selecting a row in the grid populates the edit form above it")

register("labelform",
         "your_cli.tui.features.label_form.screen", "LabelFormDemoScreen",
         display_name="Label Form",
         description="Each field on its own line — label on the left, input on the right")

register("searchgrid",
         "your_cli.tui.features.search_grid.screen", "SearchGridDemoScreen",
         display_name="Search → Grid → Edit",
         description="Filter bar, pageable results grid, row opens a full edit form")

register("cards",
         "your_cli.tui.features.cards.screen", "CardsDemoScreen",
         display_name="Card Patterns",
         description="Alert, Profile, Progress, Action, and Key-Value cards built with compose()")

register("cards2",
         "your_cli.tui.features.cards2.screen", "Cards2DemoScreen",
         display_name="Card Patterns II",
         description="Timeline, Pricing, Sparkline, Activity, and Comparison cards")

register("dicomnrrd",
         "your_cli.tui.features.dicom_nrrd.screen", "DicomNrrdDemoScreen",
         display_name="DICOM → NRRD",
         description="Batch conversion dashboard: progress, volume metadata, validation alerts, activity log")
