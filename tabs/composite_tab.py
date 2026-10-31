"""Interactive stranded-conductor GMR calculator screen."""

import math

import customtkinter as ctk

from core.gmr import stranded_gmr, stranded_gmr_ratio
from core.units import to_metres
from theme import COLORS
from widgets.strand_diagram import StrandDiagram
from widgets.neo import NeoCard, NeoWell, NeoButton


STRAND_COUNTS = ("1", "3", "7", "19", "37", "61", "91", "Custom")
UNIT_OPTIONS = ("m", "cm", "mm", "in", "ft")


class CompositeConductorTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=4, uniform="composite")
        self.grid_columnconfigure(1, weight=5, uniform="composite")
        self.grid_rowconfigure(0, weight=1)
        self.strand_count = 7
        self.radius_unit = ctk.StringVar(value="cm")
        self.radius_value = ctk.StringVar(value="r")
        self.count_value = ctk.StringVar(value="7")
        self.custom_count_value = ctk.StringVar(value="2")
        self.show_distances = ctk.BooleanVar(value=False)

        self._build_controls()
        self._build_visual()
        self._update_result()

    def _build_controls(self) -> None:
        panel = NeoCard(self)
        panel.grid(row=0, column=0, sticky="nsew", padx=(8, 8), pady=8)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel, text="Stranded conductor GMR",
            font=ctk.CTkFont("Arial Black", 21, weight="bold"),
            text_color=COLORS["text"], wraplength=380, justify="left",
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(22, 5))
        ctk.CTkLabel(
            panel, text="Choose the strand pattern and enter one strand’s radius.",
            font=ctk.CTkFont("Segoe UI", 12), text_color=COLORS["muted"],
            wraplength=380, justify="left",
        ).grid(row=1, column=0, sticky="w", padx=22, pady=(0, 22))

        ctk.CTkLabel(
            panel, text="Number of strands", font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=2, column=0, sticky="w", padx=22, pady=(0, 10))
        self.strand_selector = ctk.CTkSegmentedButton(
            panel, values=list(STRAND_COUNTS), variable=self.count_value,
            command=self._on_count_changed, selected_color=COLORS["primary_2"],
            selected_hover_color=COLORS["primary"], unselected_color=COLORS["surface_2"],
            unselected_hover_color=COLORS["hover"], text_color=COLORS["text"],
            corner_radius=4, border_width=3, height=44,
        )
        self.strand_selector.grid(row=3, column=0, sticky="ew", padx=22, pady=(0, 24))

        self.custom_count_row = ctk.CTkFrame(panel, fg_color="transparent")
        self.custom_count_row.grid(row=4, column=0, sticky="ew", padx=22, pady=(0, 14))
        self.custom_count_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self.custom_count_row, text="Custom strand count (1–200)",
            font=ctk.CTkFont("Segoe UI", 12, weight="bold"), text_color=COLORS["text"],
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.custom_count_entry = ctk.CTkEntry(
            self.custom_count_row, textvariable=self.custom_count_value, width=100, height=44,
            fg_color=COLORS["surface"], border_color=COLORS["border"], border_width=3,
            corner_radius=4, text_color=COLORS["text"], font=ctk.CTkFont("Consolas", 13),
        )
        self.custom_count_entry.grid(row=1, column=0, sticky="w", padx=(0, 8))
        NeoButton(self.custom_count_row, text="APPLY COUNT", height=44,
                  fg_color=COLORS["yellow"], command=self._apply_custom_count).grid(
                      row=1, column=1, sticky="w")
        self.custom_count_row.grid_remove()

        ctk.CTkLabel(
            panel, text="Radius of each strand", font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=5, column=0, sticky="w", padx=22, pady=(0, 10))
        radius_row = ctk.CTkFrame(panel, fg_color="transparent")
        radius_row.grid(row=6, column=0, sticky="ew", padx=22)
        radius_row.grid_columnconfigure(0, weight=1)
        self.radius_entry = ctk.CTkEntry(
            radius_row, textvariable=self.radius_value, height=40,
            fg_color=COLORS["surface"], border_color=COLORS["border"], border_width=3, corner_radius=4,
            text_color=COLORS["text"], placeholder_text="e.g. 0.012 or r",
            font=ctk.CTkFont("Consolas", 13),
        )
        self.radius_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.unit_selector = ctk.CTkOptionMenu(
            radius_row, variable=self.radius_unit, values=list(UNIT_OPTIONS),
            width=74, height=44, fg_color=COLORS["surface_2"], corner_radius=4,
            button_color=COLORS["surface_2"], button_hover_color=COLORS["hover"],
            text_color=COLORS["text"], dropdown_fg_color=COLORS["surface"],
        )
        self.unit_selector.grid(row=0, column=1)
        self.radius_unit.trace_add("write", lambda *_: self._update_result())
        self.radius_value.trace_add("write", lambda *_: self._update_result())
        self.radius_entry.bind("<Return>", lambda _event: self._update_result())
        self.custom_count_entry.bind("<Return>", self._apply_custom_count)

        self.validation_message = ctk.CTkLabel(
            panel, text="Type r for a symbolic answer, or enter a positive radius.",
            font=ctk.CTkFont("Segoe UI", 12), text_color=COLORS["muted"],
            wraplength=380, justify="left",
        )
        self.validation_message.grid(row=7, column=0, sticky="w", padx=22, pady=(8, 20))

        result_card = NeoWell(panel, fill=COLORS["orange"])
        result_card.grid(row=8, column=0, sticky="ew", padx=16, pady=(0, 16))
        ctk.CTkLabel(
            result_card, text="Geometric mean radius", font=ctk.CTkFont("Segoe UI", 12, weight="bold"),
            text_color=COLORS["text"], bg_color=COLORS["orange"],
        ).pack(anchor="w", padx=18, pady=(15, 3))
        self.symbolic_result = ctk.CTkLabel(
            result_card, text="GMR = 2.1767 r", font=ctk.CTkFont("Consolas", 24, weight="bold"),
            text_color=COLORS["text"], bg_color=COLORS["orange"], wraplength=370, justify="left",
        )
        self.symbolic_result.pack(anchor="w", padx=18, pady=(0, 2))
        self.absolute_result = ctk.CTkLabel(
            result_card, text="", font=ctk.CTkFont("Consolas", 12),
            text_color=COLORS["text"], bg_color=COLORS["orange"], wraplength=370, justify="left",
        )
        self.absolute_result.pack(anchor="w", padx=18, pady=(0, 14))

        ctk.CTkLabel(
            panel, text="Why the factor?",
            font=ctk.CTkFont("Segoe UI", 13, weight="bold"), text_color=COLORS["text"],
        ).grid(row=9, column=0, sticky="w", padx=22, pady=(4, 4))
        self.explanation_label = ctk.CTkLabel(
            panel,
            text="The self-GMR of each strand and the distances between strand centers combine into one effective radius for the whole cable.",
            font=ctk.CTkFont("Segoe UI", 12), text_color=COLORS["muted"],
            wraplength=390, justify="left",
        )
        self.explanation_label.grid(row=10, column=0, sticky="w", padx=22, pady=(0, 18))

    def _build_visual(self) -> None:
        panel = NeoCard(self)
        panel.grid(row=0, column=1, sticky="nsew", padx=(8, 8), pady=8)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header, text="Inside the cable",
            font=ctk.CTkFont("Segoe UI", 16, weight="bold"), text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="w")
        self.distance_button = NeoButton(
            header, text="SHOW DISTANCES", width=150, height=42,
            fg_color=COLORS["surface_2"], hover_color=COLORS["hover"],
            text_color=COLORS["text"], border_width=3, border_color=COLORS["border"],
            command=self._toggle_distances,
        )
        self.distance_button.grid(row=0, column=1, sticky="e")

        diagram_well = NeoWell(panel)
        diagram_well.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        diagram_well.grid_columnconfigure(0, weight=1)
        diagram_well.grid_rowconfigure(0, weight=1)
        self.diagram = StrandDiagram(diagram_well, strand_count=7)
        self.diagram.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            panel, text="Hover over a strand to identify it. Each circle represents one wire.",
            font=ctk.CTkFont("Segoe UI", 12), text_color=COLORS["muted"],
            wraplength=500, justify="left",
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 16))

    def _on_count_changed(self, value: str) -> None:
        if value == "Custom":
            self.custom_count_row.grid()
            self.custom_count_entry.focus_set()
            return
        self.custom_count_row.grid_remove()
        self.strand_count = int(value)
        self.diagram.set_strand_count(self.strand_count)
        self._update_result()

    def _apply_custom_count(self, _event=None) -> None:
        try:
            count = int(self.custom_count_value.get().strip())
            if not 1 <= count <= 200:
                raise ValueError
        except (ValueError, TypeError):
            self.validation_message.configure(
                text="Enter a whole strand count from 1 to 200.", text_color=COLORS["error"],
            )
            return
        self.strand_count = count
        self.diagram.set_strand_count(count)
        self._update_result()

    def _toggle_distances(self) -> None:
        enabled = not self.show_distances.get()
        self.show_distances.set(enabled)
        self.diagram.set_show_distances(enabled)
        self.distance_button.configure(text="Hide distances" if enabled else "Show distances")

    def _update_result(self) -> None:
        ratio = stranded_gmr_ratio(self.strand_count)
        self.symbolic_result.configure(text=f"GMR = {ratio:.4f} r")
        if self.strand_count == 7:
            explanation = "For 7 strands, the center strand uses 0.7788r as its self-GMR. The distances between all seven strand centers combine to give 2.1767r for the complete cable."
        elif self.count_value.get() == "Custom":
            explanation = (f"Custom layout: {self.strand_count} strands are packed from the center outward. "
                           "An incomplete outer ring is filled in order, and GMR uses the distances in this diagram.")
        else:
            explanation = "The self-GMR of each strand and the distances between strand centers combine into one effective radius for the whole cable."
        self.explanation_label.configure(text=explanation)
        entry = self.radius_value.get().strip()
        if entry.lower() == "r":
            self.absolute_result.configure(text="Symbolic radius · absolute value not set")
            self.validation_message.configure(
                text="Symbolic mode: the GMR factor updates with the strand count.",
                text_color=COLORS["success"],
            )
            return
        try:
            radius = float(entry)
            if not math.isfinite(radius) or radius <= 0:
                raise ValueError
            radius_m = to_metres(radius, self.radius_unit.get())
            result_m = stranded_gmr(self.strand_count, radius_m)
            shown_value = result_m / to_metres(1.0, self.radius_unit.get())
            self.absolute_result.configure(text=f"GMR = {shown_value:.6g} {self.radius_unit.get()}")
            self.validation_message.configure(
                text=f"Using a strand radius of {radius:g} {self.radius_unit.get()}.",
                text_color=COLORS["success"],
            )
        except (ValueError, OverflowError):
            self.absolute_result.configure(text="")
            self.validation_message.configure(
                text="Enter a positive radius, or use r for a symbolic answer.",
                text_color=COLORS["error"],
            )
