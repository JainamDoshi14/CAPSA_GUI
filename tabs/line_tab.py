"""Editable transmission-line layout, live geometry, and parameter results."""

import math
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

from core.models import LineModel, Result
from core.parameters import calculate_line
from core.presets import PRESETS
from core.working import generate_working_markdown, generate_working_text
from core.units import from_metres
from theme import COLORS, PRIMARY_TEXT, TYPE_L, TYPE_C, TYPE_GMD, TYPE_GMR, INK, FONT_DISPLAY, FONT_BODY, FONT_BUTTON, FONT_MONO
from widgets.dialogs import AddBundleDialog, AddConductorDialog
from widgets.editable_table import EditableConductorTable
from widgets.geometry_canvas import GeometryCanvas
from widgets.explain_sheet import ExplainSheet
from widgets.story_cards import StoryCards
from widgets.glossary import GlossaryTooltip
from widgets.neo import NeoCard, NeoTile, NeoWell, NeoButton


UNITS = ("m", "ft", "in", "cm", "mil", "cmil")


class LineParametersTab(ctk.CTkFrame):
    def __init__(self, master, on_result=None):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.body = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=COLORS["surface_2"],
            scrollbar_button_hover_color=COLORS["hover"],
        )
        self.body.grid(row=0, column=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=5, uniform="line")
        self.body.grid_columnconfigure(1, weight=6, uniform="line")
        self.unit = tk.StringVar(value="m")
        self.next_phase = tk.StringVar(value="A")
        self.preset_key = tk.StringVar(value="Q2")
        self.preset_display = tk.StringVar(value=PRESETS["Q2"].title)
        self._preset_titles = {preset.title: key for key, preset in PRESETS.items()}
        self.length_value = tk.StringVar(value="1")
        self.frequency_value = tk.StringVar(value="60")
        self.show_distances = False
        self.reduce_motion = tk.BooleanVar(value=False)
        self.precision = tk.StringVar(value="5")
        self._model: LineModel | None = None
        self._animation_ids: list[str] = []
        self._toast: ctk.CTkLabel | None = None
        self._toast_generation = 0
        self.on_result = on_result or (lambda _model: None)
        self.result: Result | None = None
        self._tiles: dict[str, tuple[ctk.CTkLabel, ctk.CTkLabel]] = {}

        self._build_input_panel()
        self._build_results_panel()
        self._layout_mode = "wide"
        self.bind("<Configure>", self._on_resize, add="+")
        self._set_empty_results()

    def _card(self, parent, **kwargs):
        return NeoCard(parent, **kwargs)

    def _build_input_panel(self) -> None:
        panel = self._card(self.body)
        panel.grid(row=0, column=0, sticky="nsew", padx=(8, 7), pady=8)
        self.input_panel = panel
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(panel, text="YOUR CONDUCTORS", text_color=COLORS["text"],
                     font=ctk.CTkFont("Arial Black", 18, weight="bold")).grid(
                         row=0, column=0, sticky="w", padx=16, pady=(14, 1))
        ctk.CTkLabel(panel, text="Edit any cell, load an example, or build a layout.",
                     text_color=COLORS["muted"], font=ctk.CTkFont("Segoe UI", 12)).grid(
                         row=1, column=0, sticky="w", padx=16, pady=(0, 7))

        preset_row = ctk.CTkFrame(panel, fg_color="transparent")
        preset_row.grid(row=2, column=0, sticky="ew", padx=14, pady=(1, 4))
        preset_row.grid_columnconfigure(0, weight=1)
        self.preset_menu = ctk.CTkOptionMenu(
            preset_row, variable=self.preset_display,
            values=list(self._preset_titles), height=40, fg_color=COLORS["surface_2"],
            button_color=COLORS["surface_2"], button_hover_color=COLORS["hover"],
            text_color=COLORS["text"], dropdown_fg_color=COLORS["surface"], corner_radius=4,
            command=self._preset_selected,
        )
        self.preset_menu.grid(row=0, column=0, sticky="ew", padx=(0, 7))
        NeoButton(
            preset_row, text="LOAD EXAMPLE", width=130, height=44,
            fg_color=COLORS["surface_2"], hover_color=COLORS["hover"],
            text_color=COLORS["text"], border_width=1, border_color=COLORS["border"],
            command=self.load_preset,
        ).grid(row=0, column=1)

        options = ctk.CTkFrame(panel, fg_color="transparent")
        options.grid(row=3, column=0, sticky="ew", padx=14, pady=(1, 4))
        options.grid_columnconfigure(0, weight=1)
        phase_chips = ctk.CTkFrame(options, fg_color="transparent")
        phase_chips.grid(row=0, column=0, sticky="w")
        self.phase_chip_buttons = {}
        for phase, color in (("A", COLORS["pink"]), ("B", COLORS["amber"]), ("C", COLORS["sky"])):
            button = NeoButton(
                phase_chips, text=phase, width=44, height=44,
                fg_color=color, hover_color=COLORS["hover"],
                text_color=COLORS["text"], border_width=3, border_color=COLORS["border"],
                command=lambda selected=phase: self._select_phase(selected),
            )
            button.pack(side="left", padx=(0, 5))
            self.phase_chip_buttons[phase] = button
        self._select_phase("A")
        self.unit_menu = ctk.CTkOptionMenu(
            options, variable=self.unit, values=list(UNITS), width=88, height=40, corner_radius=4,
            fg_color=COLORS["surface_2"], button_color=COLORS["surface_2"],
            button_hover_color=COLORS["hover"], text_color=COLORS["text"],
            dropdown_fg_color=COLORS["surface"],
            command=self._unit_changed,
        )
        self.unit_menu.grid(row=0, column=1, sticky="e")

        table_wrap = NeoWell(panel)
        table_wrap.grid(row=4, column=0, sticky="nsew", padx=12, pady=(2, 5))
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)
        self.table = EditableConductorTable(
            table_wrap, unit=self.unit.get(), on_change=self._model_changed,
            on_error=self.show_error,
        )
        self.table.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        self.table_empty_hint = ctk.CTkLabel(
            table_wrap, text="Nothing here yet. Load an example or add conductors.",
            text_color=COLORS["muted"], font=ctk.CTkFont("Segoe UI", 12),
        )
        self.table_empty_hint.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        actions = ctk.CTkFrame(panel, fg_color="transparent")
        actions.grid(row=5, column=0, sticky="ew", padx=12, pady=(2, 5))
        for column in range(4):
            actions.grid_columnconfigure(column, weight=1, uniform="action")
        for column, (label, command) in enumerate((
            ("+ Conductor", self.add_conductor),
            ("+ Bundle", self.add_bundle),
            ("Remove", self.remove_selected),
            ("Clear all", self.clear_all),
        )):
            NeoButton(
                actions, text=label.upper(), height=40,
                fg_color=COLORS["surface_2"], hover_color=COLORS["hover"],
                text_color=INK, border_width=3, border_color=INK,
                font=ctk.CTkFont(FONT_BUTTON, 12, weight="bold"), command=command,
            ).grid(row=0, column=column, sticky="ew", padx=2)

        setup = ctk.CTkFrame(panel, fg_color="transparent")
        setup.grid(row=6, column=0, sticky="ew", padx=12, pady=(1, 4))
        setup.grid_columnconfigure((0, 1), weight=1)
        self._number_field(setup, "Line length", "km", self.length_value, 0)
        self._number_field(setup, "Frequency", "Hz", self.frequency_value, 1)
        self.length_value.trace_add("write", lambda *_: self._mark_stale())
        self.frequency_value.trace_add("write", lambda *_: self._mark_stale())

        self.compute_button = NeoButton(
            panel, text="CALCULATE", height=48,
            fg_color=COLORS["primary_2"], hover_color=COLORS["primary"],
            text_color=INK, border_width=3, border_color=INK, font=ctk.CTkFont(FONT_BUTTON, 13, weight="bold"),
            command=self.compute,
        )
        self.compute_button.grid(row=7, column=0, sticky="ew", padx=12, pady=(2, 4))
        self.error_label = ctk.CTkLabel(
            panel, text="", text_color=COLORS["error"], font=ctk.CTkFont("Segoe UI", 12),
            wraplength=450, justify="left",
        )
        self.error_label.grid(row=8, column=0, sticky="w", padx=15, pady=(0, 8))

    def _number_field(self, parent, title: str, suffix: str, variable, column: int) -> None:
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        cell.grid(row=0, column=column, sticky="ew", padx=3)
        cell.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(cell, text=title, text_color=COLORS["muted"],
                     font=ctk.CTkFont("Segoe UI", 12)).grid(row=0, column=0, sticky="w")
        row = ctk.CTkFrame(cell, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew")
        row.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(row, textvariable=variable, height=44, fg_color=COLORS["surface"],
                     border_width=3, corner_radius=4, border_color=COLORS["border"], text_color=COLORS["text"],
                     font=ctk.CTkFont("Consolas", 12)).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(row, text=suffix, text_color=COLORS["muted"],
                     font=ctk.CTkFont("Segoe UI", 12)).grid(row=0, column=1)

    def _build_results_panel(self) -> None:
        panel = self._card(self.body)
        panel.grid(row=0, column=1, sticky="nsew", padx=(7, 8), pady=8)
        self.results_panel = panel
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_rowconfigure(1, minsize=150)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(6, 2))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Your line", text_color=COLORS["text"],
                     font=ctk.CTkFont("Segoe UI", 16, weight="bold")).grid(row=0, column=0, sticky="w")
        self.distance_button = NeoButton(
            header, text="SHOW DISTANCES", width=146, height=42,
            fg_color=COLORS["surface_2"], hover_color=COLORS["hover"],
            text_color=COLORS["text"], border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont("Segoe UI", 12), command=self._toggle_distances,
        )
        self.distance_button.grid(row=0, column=1, sticky="e")
        self.working_button = NeoButton(
            header, text="SHOW WORKING", width=138, height=42,
            fg_color=COLORS["primary_2"], hover_color=COLORS["primary"],
            text_color=PRIMARY_TEXT, font=ctk.CTkFont("Segoe UI", 12),
            command=self.show_working, state="disabled",
        )
        self.working_button.grid(row=0, column=2, sticky="e", padx=(6, 0))
        self.precision_menu = ctk.CTkSegmentedButton(
            header, values=["4", "5"], variable=self.precision, width=88, height=40,
            corner_radius=4, border_width=3, selected_color=COLORS["yellow"],
            selected_hover_color=COLORS["hover"], unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["hover"], text_color=INK,
            command=self._precision_changed,
        )
        self.precision_menu.grid(row=0, column=3, sticky="e", padx=(7, 0))
        ctk.CTkLabel(header, text="sig figs", text_color=COLORS["muted"],
                     font=ctk.CTkFont(FONT_BODY, 12)).grid(row=1, column=3, sticky="e")
        ctk.CTkCheckBox(
            header, text="Reduce motion", variable=self.reduce_motion, height=22,
            font=ctk.CTkFont(FONT_BODY, 12), text_color=COLORS["muted"],
            checkbox_width=20, checkbox_height=20, command=self._motion_changed,
        ).grid(row=1, column=2, sticky="e", padx=(0, 6))

        geometry_well = NeoWell(panel)
        geometry_well.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 7))
        geometry_well.grid_columnconfigure(0, weight=1)
        geometry_well.grid_rowconfigure(0, weight=1)
        self.geometry = GeometryCanvas(geometry_well, height=184, on_drag=self._conductor_dragged)
        self.geometry.grid(row=0, column=0, sticky="nsew")

        results = ctk.CTkFrame(panel, fg_color="transparent")
        results.grid(row=2, column=0, sticky="ew", padx=10, pady=1)
        for column in range(3):
            results.grid_columnconfigure(column, weight=1, uniform="kpi")
        tile_specs = (
            ("gmd", "GMD", "m"), ("gmr_l", "GMR · L", "m"), ("gmr_c", "GMR · C", "m"),
            ("inductance", "Inductance", "mH/km"), ("capacitance", "Capacitance", "μF/km"),
            ("reactance", "Xₗ / X꜀", "Ω/km"),
        )
        for index, (key, title, units) in enumerate(tile_specs):
            row, column = divmod(index, 3)
            self._make_tile(results, key, title, units, row, column)

        details = NeoWell(panel)
        details.grid(row=3, column=0, sticky="ew", padx=12, pady=(4, 3))
        details.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(details, text="Phase details", text_color=COLORS["text"],
                     font=ctk.CTkFont("Segoe UI", 12, weight="bold")).grid(
                         row=0, column=0, sticky="w", padx=12, pady=(8, 2))
        NeoButton(details, text="💡 Explain it to me", height=40,
                      fg_color=COLORS["surface_2"], hover_color=COLORS["hover"],
                      text_color=COLORS["text"], command=self.show_story
                      ).grid(row=0, column=1, sticky="e", padx=10, pady=(6, 2))
        self.details_label = ctk.CTkLabel(
            details, text="Add conductors or load an example, then calculate.",
            text_color=COLORS["muted"], font=ctk.CTkFont("Consolas", 12),
            wraplength=510, justify="left",
        )
        self.details_label.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 3))
        self.hint_label = ctk.CTkLabel(details, text="", text_color=COLORS["muted"],
                                       font=ctk.CTkFont("Segoe UI", 12), justify="left", anchor="w",
                                       wraplength=510)
        self.hint_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 7))

    def _on_resize(self, event) -> None:
        if event.widget is self:
            self.after(100, self._layout_panels)

    def _layout_panels(self) -> None:
        if not self.winfo_exists() or self.winfo_width() <= 1:
            return
        scale = self._get_widget_scaling()
        mode = "stacked" if self.winfo_width() / scale < 1000 else "wide"
        if mode == self._layout_mode:
            return
        self._layout_mode = mode
        if mode == "stacked":
            self.body.grid_columnconfigure(0, weight=1, uniform="line")
            self.body.grid_columnconfigure(1, weight=0, uniform="line")
            self.body.grid_rowconfigure(0, weight=0)
            self.body.grid_rowconfigure(1, weight=0)
            self.input_panel.grid_configure(row=0, column=0, columnspan=2, padx=8)
            self.results_panel.grid_configure(row=1, column=0, columnspan=2, padx=8)
        else:
            self.body.grid_columnconfigure(0, weight=5, uniform="line")
            self.body.grid_columnconfigure(1, weight=6, uniform="line")
            self.body.grid_rowconfigure(0, weight=0)
            self.body.grid_rowconfigure(1, weight=0)
            self.input_panel.grid_configure(row=0, column=0, columnspan=1, padx=(8, 7))
            self.results_panel.grid_configure(row=0, column=1, columnspan=1, padx=(7, 8))

    def _make_tile(self, parent, key: str, title: str, units: str, row: int, column: int) -> None:
        type_color = (TYPE_L if key == "inductance" else TYPE_C if key == "capacitance"
                      else TYPE_GMD if key == "gmd" else TYPE_GMR)
        card = NeoTile(parent, fill=type_color)
        card.grid(row=row, column=column, sticky="nsew", padx=3, pady=3)
        card.grid_columnconfigure(0, weight=1)
        title_row = ctk.CTkFrame(card, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", padx=8, pady=(5, 0))
        title_row.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(title_row, text=title.upper(), text_color=INK,
                                   font=ctk.CTkFont(FONT_BUTTON, 12, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w")
        NeoButton(title_row, text="?", width=32, height=32,
                      fg_color=COLORS["lavender"], hover_color=COLORS["hover"],
                      text_color=INK, font=ctk.CTkFont(FONT_BUTTON, 12, weight="bold"),
                      command=lambda metric=key: self.explain_metric(metric)
                      ).grid(row=0, column=1, sticky="e")
        terms = {"gmd": "GMD: average phase-to-phase spacing.",
                 "gmr_l": "GMR: effective conductor radius for inductance.",
                 "gmr_c": "GMR: effective conductor radius for capacitance.",
                 "inductance": "Inductance: magnetic energy stored per phase.",
                 "capacitance": "Capacitance: electric charge stored per phase.",
                 "reactance": "Reactance: AC opposition from inductance and capacitance."}
        GlossaryTooltip(title_label, terms[key])
        value = ctk.CTkLabel(card, text="—", text_color=COLORS["text"],
                             font=ctk.CTkFont("Consolas", 30, weight="bold"), anchor="w")
        value.grid(row=1, column=0, sticky="w", padx=9)
        ctk.CTkFrame(card, height=3, corner_radius=2, fg_color=type_color).grid(
            row=2, column=0, sticky="ew", padx=9, pady=(1, 2))
        unit_label = ctk.CTkLabel(card, text=units, text_color=COLORS["muted"],
                                  font=ctk.CTkFont(FONT_BODY, 12))
        unit_label.grid(row=3, column=0, sticky="w", padx=9, pady=(0, 6))
        self._tiles[key] = (value, unit_label)

    def _unit_changed(self, value: str) -> None:
        self.table.set_unit(value)
        self._model_changed()

    def _dialog_x(self) -> float:
        try:
            existing = self.table.get_conductors()
        except (ValueError, TypeError):
            existing = []
        if not existing:
            return 0.0
        return from_metres(max(item.x for item in existing) + 0.5, self.unit.get())

    def add_conductor(self) -> None:
        AddConductorDialog(self, unit=self.unit.get(), on_add=self.table.add_conductors,
                           default_phase=self.next_phase.get(), default_x=self._dialog_x())

    def add_bundle(self) -> None:
        AddBundleDialog(self, unit=self.unit.get(), on_add=self.table.add_conductors,
                        default_phase=self.next_phase.get(), default_x=self._dialog_x())

    def _select_phase(self, phase: str) -> None:
        self.next_phase.set(phase)
        colors = {"A": COLORS["pink"], "B": COLORS["amber"], "C": COLORS["sky"]}
        for name, button in self.phase_chip_buttons.items():
            selected = name == phase
            button.configure(fg_color=colors[name], text_color=INK,
                             border_width=4 if selected else 3, border_color=INK)

    def _conductor_dragged(self, index, conductor) -> None:
        conductors = self.table.get_conductors()
        if 0 <= index < len(conductors):
            conductors[index] = conductor
            self.table.set_conductors(conductors)
            self._model_changed()

    def remove_selected(self) -> None:
        if self.table.remove_selected() == 0:
            self.show_error("Select one or more rows to remove.")

    def clear_all(self) -> None:
        self.table.clear()
        self.show_error("")

    def load_preset(self) -> None:
        preset = PRESETS.get(self.preset_key.get())
        if preset is None:
            self.show_error("Choose one of the available textbook examples.")
            return
        self.length_value.set(f"{preset.model.length_km:g}")
        self.frequency_value.set(f"{preset.model.freq_hz:g}")
        self.table.set_conductors(preset.model.conductors)
        self.show_error("")
        self._model_changed()

    def _preset_selected(self, title: str) -> None:
        self.preset_key.set(self._preset_titles.get(title, ""))

    def select_preset(self, key: str) -> None:
        """Select a preset by its internal key for existing app workflows."""
        preset = PRESETS.get(key)
        if preset is None:
            self.preset_key.set("")
            self.preset_display.set("Choose a textbook example")
            return
        self.preset_key.set(key)
        self.preset_display.set(preset.title)

    def _toggle_distances(self) -> None:
        self.show_distances = not self.show_distances
        self.geometry.set_model(self._conductors_or_empty(), self.show_distances)
        self.distance_button.configure(text="Hide distances" if self.show_distances else "Show distances")

    def _conductors_or_empty(self):
        try:
            return self.table.get_conductors()
        except (ValueError, TypeError, OverflowError):
            return []

    def _model_changed(self) -> None:
        conductors = self._conductors_or_empty()
        if hasattr(self, "table_empty_hint"):
            if conductors:
                self.table_empty_hint.grid_remove()
            else:
                self.table_empty_hint.grid()
        self.geometry.set_model(conductors, self.show_distances)
        self._set_empty_results()
        if self.result is not None:
            self.details_label.configure(text="Layout changed. Calculate again to refresh the results.")
        self.result = None

    def _mark_stale(self) -> None:
        if self.result is not None:
            self.result = None
            self._set_empty_results()
            self.details_label.configure(text="Line settings changed. Calculate again to refresh the results.")

    def _set_empty_results(self) -> None:
        self._cancel_animations()
        if hasattr(self, "working_button"):
            self.working_button.configure(state="disabled")
        for value, unit in self._tiles.values():
            value.configure(text="—")
        self._tiles["inductance"][1].configure(text="mH/km · total — mH")
        self._tiles["capacitance"][1].configure(text="μF/km · total — μF")
        self._tiles["reactance"][1].configure(text="Ω/km · X꜀ shown below")

    def show_error(self, message: str) -> None:
        self.error_label.configure(text=message, text_color=COLORS["error"] if message else COLORS["muted"])

    def compute(self) -> None:
        try:
            length = float(self.length_value.get())
            frequency = float(self.frequency_value.get())
            if not math.isfinite(length) or length <= 0:
                raise ValueError("Line length must be greater than zero km.")
            if not math.isfinite(frequency) or frequency <= 0:
                raise ValueError("Frequency must be greater than zero Hz.")
            conductors = self.table.get_conductors()
            preset = PRESETS.get(self.preset_key.get())
            preset_matches = (
                preset is not None
                and len(conductors) == len(preset.model.conductors)
                and all(
                    actual.phase == expected.phase
                    and all(math.isclose(a, b, rel_tol=2e-6, abs_tol=1e-12) for a, b in zip(
                        (actual.x, actual.y, actual.r, actual.gmr_s),
                        (expected.x, expected.y, expected.r, expected.gmr_s),
                    ))
                    for actual, expected in zip(conductors, preset.model.conductors)
                )
                and length == preset.model.length_km
                and frequency == preset.model.freq_hz
            )
            model = LineModel(
                conductors, length_km=length, freq_hz=frequency,
                name=preset.title if preset_matches else "Custom line",
            )
            result = calculate_line(model)
        except ValueError as exc:
            message = str(exc)
            if "could not convert" in message.lower() or "invalid literal" in message.lower():
                message = "Check the entries: coordinates, radii, GMR, length, and frequency need valid numbers."
            self.show_error(message)
            return
        except (TypeError, OverflowError):
            self.show_error("Check the entries and try again.")
            return

        self.result = result
        self._model = model
        self.show_error("")
        self._render_result(result, length)
        self.working_button.configure(state="normal")
        self._show_toast("Calculation complete")
        self._update_hint(model)
        self.on_result(model)

    def _render_result(self, result: Result, length_km: float) -> None:
        self._cancel_animations()
        digits = int(self.precision.get())
        self._set_tile_value("gmd", result.gmd, digits)
        self._set_tile_value("gmr_l", result.gmr_l, digits)
        self._set_tile_value("gmr_c", result.gmr_c, digits)
        self._set_tile_value("inductance", result.L_mH_per_km, digits)
        self._tiles["inductance"][1].configure(text=f"mH/km · total {result.L_total_mH:.{digits}g} mH ({length_km:g} km)")
        self._set_tile_value("capacitance", result.C_uF_per_km, digits)
        self._tiles["capacitance"][1].configure(text=f"μF/km · total {result.C_total_uF:.{digits}g} μF ({length_km:g} km)")
        self._set_tile_value("reactance", result.X_L_ohm_per_km, digits)
        self._tiles["reactance"][1].configure(text=f"Xₗ /km · X꜀ {result.X_C_ohm_per_km:.{digits}g} Ω/km")
        phases = result.per_phase
        counts = [phases[phase].n for phase in "ABC"]
        lines = [
            f"D_AB {result.gmd_ab:.{digits}g} m   D_BC {result.gmd_bc:.{digits}g} m   D_CA {result.gmd_ca:.{digits}g} m",
            f"Phase A: n={phases['A'].n} · GMR_L {phases['A'].gmr_l:.{digits}g} m · GMR_C {phases['A'].gmr_c:.{digits}g} m",
            f"Phase B: n={phases['B'].n} · GMR_L {phases['B'].gmr_l:.{digits}g} m · GMR_C {phases['B'].gmr_c:.{digits}g} m",
            f"Phase C: n={phases['C'].n} · GMR_L {phases['C'].gmr_l:.{digits}g} m · GMR_C {phases['C'].gmr_c:.{digits}g} m",
        ]
        if len(set(counts)) != 1:
            lines.append("Heads up: phases have different conductor counts. Check that this is intended.")
        self.details_label.configure(text="\n".join(lines))

    def _cancel_animations(self) -> None:
        for after_id in self._animation_ids:
            try:
                self.after_cancel(after_id)
            except tk.TclError:
                pass
        self._animation_ids.clear()

    def _set_tile_value(self, key: str, target: float, digits: int) -> None:
        label = self._tiles[key][0]
        if self.reduce_motion.get():
            label.configure(text=f"{target:.{digits}g}")
            return
        frames = 14
        def step(index: int = 1) -> None:
            fraction = index / frames
            label.configure(text=f"{target * fraction:.{digits}g}")
            if index < frames:
                self._animation_ids.append(self.after(18, step, index + 1))
        step()

    def _precision_changed(self, _value: str) -> None:
        if self.result is not None:
            self._render_result(self.result, self._model.length_km)

    def _motion_changed(self) -> None:
        if self.reduce_motion.get():
            self._cancel_animations()
        if self.result is not None:
            self._render_result(self.result, self._model.length_km)

    def _show_toast(self, message: str) -> None:
        self._toast_generation += 1
        generation = self._toast_generation
        if self._toast is not None:
            try:
                self._toast.destroy()
            except tk.TclError:
                pass
        self._toast = ctk.CTkLabel(
            self, text=message, fg_color=COLORS["success"], text_color=COLORS["bg"],
            corner_radius=18, padx=16, pady=9, font=ctk.CTkFont("Segoe UI", 12, weight="bold"),
        )
        self._toast.place(relx=1.04 if not self.reduce_motion.get() else 0.98,
                          rely=0.97, anchor="se")
        toast = self._toast
        if not self.reduce_motion.get():
            def slide(step=1):
                if generation != self._toast_generation or not toast.winfo_exists():
                    return
                toast.place_configure(relx=1.04 - 0.06 * min(step / 10, 1))
                if step < 10:
                    self.after(18, slide, step + 1)
            self.after(18, slide)
        self.after(4000, lambda: toast.destroy() if generation == self._toast_generation and toast.winfo_exists() else None)

    def _update_hint(self, model: LineModel) -> None:
        counts = [sum(item.phase == phase for item in model.conductors) for phase in "ABC"]
        if len(set(counts)) > 1:
            self.hint_label.configure(
                text=f"Heads up: phase A/B/C have {counts[0]}/{counts[1]}/{counts[2]} conductors. Is that intended?",
                text_color=COLORS["amber"],
            )
        else:
            self.hint_label.configure(
                text=f"Looks good: {len(model.conductors)} conductors across three phases ✓",
                text_color=COLORS["success"],
            )

    def explain_metric(self, metric: str) -> None:
        if self._model is None or self.result is None:
            self.show_error("Calculate the line first, then tap ? to explore a result.")
            return
        ExplainSheet(self, metric, self._model, self.result, int(self.precision.get()))

    def show_story(self) -> None:
        if self._model is None or self.result is None:
            self.show_error("Calculate the line first to open the guided explanation.")
            return
        StoryCards(self, self._model, self.result, int(self.precision.get()))

    def show_working(self) -> None:
        if self._model is None or self.result is None:
            return
        window = ctk.CTkToplevel(self)
        window.title("Calculation working")
        window.geometry("780x650")
        window.minsize(620, 480)
        window.transient(self.winfo_toplevel())
        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(0, weight=1)
        report = ctk.CTkTextbox(window, wrap="word", font=ctk.CTkFont("Consolas", 12))
        report.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 6))
        report.insert("1.0", generate_working_text(self._model, self.result, int(self.precision.get())))
        report.configure(state="disabled")
        actions = ctk.CTkFrame(window, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="ew", padx=12, pady=(4, 12))
        actions.grid_columnconfigure(0, weight=1)
        NeoButton(actions, text="Copy all", command=lambda: self._copy_working()).grid(row=0, column=1, padx=4)
        NeoButton(actions, text="Export .md", command=lambda: self._export_working("md")).grid(row=0, column=2, padx=4)
        NeoButton(actions, text="Export .txt", command=lambda: self._export_working("txt")).grid(row=0, column=3, padx=4)
        NeoButton(actions, text="Close", command=window.destroy).grid(row=0, column=4, padx=(4, 0))
        self._working_window = window
        self._working_text = report

    def _copy_working(self) -> None:
        if not self._model or not self.result:
            return
        self.clipboard_clear()
        self.clipboard_append(generate_working_markdown(self._model, self.result, int(self.precision.get())))
        self._show_toast("Working copied")

    def _export_working(self, extension: str) -> None:
        if not self._model or not self.result:
            return
        path = filedialog.asksaveasfilename(
            parent=self, title="Export calculation working",
            defaultextension=f".{extension}", filetypes=[(f"{extension.upper()} files", f"*.{extension}")],
            initialfile="line-calculation-working",
        )
        if not path:
            return
        content = (generate_working_markdown if extension == "md" else generate_working_text)(
            self._model, self.result, int(self.precision.get())
        )
        try:
            with open(path, "w", encoding="utf-8", newline="\n") as output:
                output.write(content)
        except OSError as exc:
            self.show_error(f"Could not export the report: {exc}")
            return
        self._show_toast(f"Saved {path.split('/')[-1].split(chr(92))[-1]}")
