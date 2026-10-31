"""Small input dialogs for adding conductors and bundles."""

from math import cos, pi, sin, sqrt

import customtkinter as ctk

from core.models import Conductor
from core.units import to_metres
from theme import COLORS
from .neo import NeoButton


class _ConductorDialog(ctk.CTkToplevel):
    def __init__(self, master, *, unit: str, on_add, title: str):
        super().__init__(master)
        self.unit = unit
        self.on_add = on_add
        self.title(title)
        self.geometry("430x620")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.transient(master.winfo_toplevel())
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.form = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=COLORS["surface_2"],
            scrollbar_button_hover_color=COLORS["hover"],
        )
        self.form.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 0))
        self.form.grid_columnconfigure(0, weight=1)
        self.vars = {}
        self.message = None

    def _header(self, title: str, subtitle: str) -> None:
        ctk.CTkLabel(self.form, text=title.upper(), font=ctk.CTkFont("Arial Black", 20, weight="bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", padx=22, pady=(20, 3))
        ctk.CTkLabel(self.form, text=subtitle, font=ctk.CTkFont("Segoe UI", 12),
                     text_color=COLORS["muted"], wraplength=340, justify="left").grid(
                         row=1, column=0, sticky="w", padx=22, pady=(0, 14))

    def _field(self, row: int, label: str, key: str, default: str) -> None:
        ctk.CTkLabel(self.form, text=label, text_color=COLORS["muted"],
                     font=ctk.CTkFont("Segoe UI", 12)).grid(row=row, column=0, sticky="w", padx=22, pady=(5, 2))
        variable = ctk.StringVar(value=default)
        self.vars[key] = variable
        ctk.CTkEntry(self.form, textvariable=variable, height=44, fg_color=COLORS["surface"],
                     border_width=3, corner_radius=4, border_color=COLORS["border"], text_color=COLORS["text"]).grid(
                         row=row + 1, column=0, sticky="ew", padx=22, pady=(0, 3))

    def _select(self, row: int, label: str, key: str, values: tuple[str, ...], default: str) -> None:
        ctk.CTkLabel(self.form, text=label, text_color=COLORS["muted"],
                     font=ctk.CTkFont("Segoe UI", 12)).grid(row=row, column=0, sticky="w", padx=22, pady=(5, 2))
        variable = ctk.StringVar(value=default)
        self.vars[key] = variable
        ctk.CTkOptionMenu(self.form, variable=variable, values=list(values), height=44, corner_radius=4,
                          fg_color=COLORS["surface_2"], button_color=COLORS["surface_2"],
                          button_hover_color=COLORS["hover"], text_color=COLORS["text"]).grid(
                              row=row + 1, column=0, sticky="ew", padx=22, pady=(0, 3))

    def _buttons(self, _row: int) -> None:
        footer = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        footer.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        footer.grid_columnconfigure(0, weight=1)
        self.message = ctk.CTkLabel(
            footer, text="", text_color=COLORS["error"], font=ctk.CTkFont("Segoe UI", 12),
            wraplength=360, justify="left",
        )
        self.message.grid(row=0, column=0, sticky="w", padx=14, pady=(3, 2))
        actions = ctk.CTkFrame(footer, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="e", padx=14, pady=(2, 10))
        NeoButton(actions, text="CANCEL", height=40,
                      fg_color=COLORS["surface_2"], hover_color=COLORS["hover"],
                      text_color=COLORS["text"], command=self.destroy).pack(side="left", padx=(0, 8))
        NeoButton(actions, text="ADD", height=40,
                      fg_color=COLORS["primary_2"], hover_color=COLORS["primary"],
                      text_color=COLORS["text"], command=self._submit).pack(side="left")

    def _float(self, key: str) -> float:
        value = float(self.vars[key].get())
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError
        return value

    def _make_conductors(self) -> list[Conductor]:
        raise NotImplementedError

    def _submit(self) -> None:
        try:
            conductors = self._make_conductors()
        except (ValueError, TypeError, OverflowError, KeyError):
            self.message.configure(text="Check the entries. Coordinates can be any number; radius and GMR must be positive.")
            return
        self.on_add(conductors)
        self.destroy()


class AddConductorDialog(_ConductorDialog):
    def __init__(self, master, *, unit: str, on_add, default_phase: str = "A", default_x: float = 0):
        super().__init__(master, unit=unit, on_add=on_add, title="Add conductor")
        self._header("Add a conductor", "Enter its position and physical radius. Self GMR defaults to 0.7788 × radius.")
        self._select(2, "Phase", "phase", ("A", "B", "C"), default_phase)
        self._field(4, f"X position ({unit})", "x", f"{default_x:g}")
        self._field(6, f"Y position ({unit})", "y", "0")
        self._field(8, f"Outer radius ({unit})", "radius", "0.01")
        self._field(10, f"Self GMR ({unit}) · blank uses 0.7788r", "gmr", "")
        self._buttons(12)

    def _make_conductors(self) -> list[Conductor]:
        radius = self._float("radius")
        gmr = self._float("gmr") if self.vars["gmr"].get().strip() else radius * 0.7788
        return [Conductor(
            self.vars["phase"].get(), to_metres(self._float("x"), self.unit),
            to_metres(self._float("y"), self.unit), to_metres(radius, self.unit),
            to_metres(gmr, self.unit),
        )]


class AddBundleDialog(_ConductorDialog):
    def __init__(self, master, *, unit: str, on_add, default_phase: str = "A", default_x: float = 0):
        super().__init__(master, unit=unit, on_add=on_add, title="Add bundle")
        self._header("Add a bundle", "Place 2, 3, or 4 equal sub-conductors around one phase center.")
        self._select(2, "Phase", "phase", ("A", "B", "C"), default_phase)
        self._select(4, "Sub-conductors", "count", ("2", "3", "4"), "2")
        self._select(6, "Orientation", "orientation", ("Horizontal", "Vertical"), "Horizontal")
        self._field(8, f"Center X ({unit})", "x", f"{default_x:g}")
        self._field(10, f"Center Y ({unit})", "y", "0")
        self._field(12, f"Sub-conductor spacing ({unit})", "spacing", "0.3")
        self._field(14, f"Outer radius per sub-conductor ({unit})", "radius", "0.01")
        self._field(16, f"Self GMR ({unit}) · blank uses 0.7788r", "gmr", "")
        self._buttons(18)

    def _make_conductors(self) -> list[Conductor]:
        count = int(self.vars["count"].get())
        spacing = self._float("spacing")
        radius = self._float("radius")
        if count not in (2, 3, 4) or spacing <= 0 or radius <= 0:
            raise ValueError
        gmr = self._float("gmr") if self.vars["gmr"].get().strip() else radius * 0.7788
        if gmr <= 0:
            raise ValueError
        cx, cy = self._float("x"), self._float("y")
        orientation = 0.0 if self.vars["orientation"].get() == "Horizontal" else pi / 2
        if count == 2:
            offsets = [(-spacing / 2, 0), (spacing / 2, 0)] if orientation == 0 else [(0, -spacing / 2), (0, spacing / 2)]
        else:
            circumradius = spacing / sqrt(3) if count == 3 else spacing / sqrt(2)
            angle_offset = -pi / 2 if count == 3 else pi / 4
            offsets = [(circumradius * cos(angle_offset + orientation + 2 * pi * i / count),
                        circumradius * sin(angle_offset + orientation + 2 * pi * i / count))
                       for i in range(count)]
        return [Conductor(
            self.vars["phase"].get(), to_metres(cx + dx, self.unit), to_metres(cy + dy, self.unit),
            to_metres(radius, self.unit), to_metres(gmr, self.unit),
        ) for dx, dy in offsets]
