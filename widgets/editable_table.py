"""Editable phase/coordinate/radius table backed by SI conductor models."""

from collections.abc import Callable, Sequence
import tkinter as tk
from tkinter import ttk

from core.models import Conductor
from core.units import from_metres, to_metres
from theme import COLORS, INK, SURFACE, ALT_SURFACE, YELLOW, FONT_BODY, FONT_MONO


class EditableConductorTable(ttk.Frame):
    COLUMNS = ("phase", "x", "y", "r", "gmr_s")

    def __init__(self, master, *, unit: str = "m", on_change: Callable | None = None,
                 on_error: Callable[[str], None] | None = None):
        super().__init__(master)
        self.unit = unit
        self.on_change = on_change or (lambda: None)
        self.on_error = on_error or (lambda _message: None)
        self._editor = None

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=SURFACE)
        style.configure("Conductor.Treeview", background=SURFACE,
                        fieldbackground=SURFACE, foreground=INK,
                        rowheight=44, borderwidth=0, font=(FONT_MONO, 12))
        style.configure("Conductor.Treeview.Heading", background=INK,
                        foreground=SURFACE, relief="flat", font=(FONT_BODY, 12, "bold"))
        style.map("Conductor.Treeview", background=[("selected", YELLOW)],
                  foreground=[("selected", INK)])

        self.tree = ttk.Treeview(self, columns=self.COLUMNS, show="headings", height=6,
                                 selectmode="extended", style="Conductor.Treeview")
        self.tree.heading("phase", text="Phase")
        self.tree.column("phase", width=58, minwidth=48, anchor="center", stretch=False)
        self.tree.heading("x", text="X (m)")
        self.tree.heading("y", text="Y (m)")
        self.tree.heading("r", text="Radius r (m)")
        self.tree.heading("gmr_s", text="Self GMR (m)")
        for name, width in (("x", 75), ("y", 75), ("r", 90), ("gmr_s", 95)):
            self.tree.column(name, width=width, minwidth=64, anchor="e", stretch=True)
        style.configure("Conductor.Vertical.TScrollbar", background=YELLOW,
                        troughcolor=SURFACE, bordercolor=INK, arrowcolor=INK, width=14)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview,
                                  style="Conductor.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree.tag_configure("even", background=SURFACE)
        self.tree.tag_configure("odd", background=ALT_SURFACE)
        self.tree.bind("<Double-1>", self._begin_edit)
        self.set_unit(unit)

    def set_unit(self, unit: str) -> None:
        conductors = []
        try:
            conductors = self.get_conductors()
        except (ValueError, TypeError, OverflowError):
            pass
        self.unit = unit
        self.tree.heading("x", text=f"X ({unit})")
        self.tree.heading("y", text=f"Y ({unit})")
        self.tree.heading("r", text=f"Radius r ({unit})")
        self.tree.heading("gmr_s", text=f"Self GMR ({unit})")
        if conductors:
            self.set_conductors(conductors)

    def set_conductors(self, conductors: Sequence[Conductor]) -> None:
        self._cancel_edit()
        self.tree.delete(*self.tree.get_children())
        for item in conductors:
            self.tree.insert("", "end", values=self._display_values(item),
                             tags=("even" if len(self.tree.get_children()) % 2 == 0 else "odd",))

    def get_conductors(self) -> list[Conductor]:
        return [self._parse_values(self.tree.item(iid, "values"))
                for iid in self.tree.get_children()]

    def add_conductors(self, conductors: Sequence[Conductor]) -> None:
        for item in conductors:
            row_index = len(self.tree.get_children())
            self.tree.insert("", "end", values=self._display_values(item),
                             tags=("even" if row_index % 2 == 0 else "odd",))
        self.on_change()

    def remove_selected(self) -> int:
        selected = self.tree.selection()
        if selected:
            self._cancel_edit()
        for iid in selected:
            self.tree.delete(iid)
        if selected:
            self.on_change()
        return len(selected)

    def clear(self) -> None:
        self._cancel_edit()
        self.tree.delete(*self.tree.get_children())
        self.on_change()

    def _display_values(self, item: Conductor) -> tuple[str, ...]:
        return (
            item.phase,
            f"{from_metres(item.x, self.unit):.6g}",
            f"{from_metres(item.y, self.unit):.6g}",
            f"{from_metres(item.r, self.unit):.6g}",
            f"{from_metres(item.gmr_s, self.unit):.6g}",
        )

    def _parse_values(self, values) -> Conductor:
        phase, x, y, radius, gmr_s = values
        return Conductor(phase, to_metres(float(x), self.unit), to_metres(float(y), self.unit),
                         to_metres(float(radius), self.unit), to_metres(float(gmr_s), self.unit))

    def _refresh_values(self) -> None:
        for index, iid in enumerate(self.tree.get_children()):
            values = self.tree.item(iid, "values")
            try:
                model = self._parse_values(values)
            except (ValueError, TypeError):
                continue
            self.tree.item(iid, values=self._display_values(model),
                           tags=("even" if index % 2 == 0 else "odd",))

    def _begin_edit(self, event) -> None:
        row_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        if not row_id or not column_id:
            return
        column_index = int(column_id[1:]) - 1
        if not 0 <= column_index < len(self.COLUMNS):
            return
        bbox = self.tree.bbox(row_id, column_id)
        if not bbox:
            return
        x, y, width, height = bbox
        values = list(self.tree.item(row_id, "values"))
        if column_index == 0:
            editor = ttk.Combobox(self.tree, values=("A", "B", "C"), state="readonly")
            editor.set(values[column_index])
        else:
            editor = ttk.Entry(self.tree, justify="right")
            editor.insert(0, values[column_index])
            editor.select_range(0, "end")
        self._editor = editor
        editor.place(x=x, y=y, width=width, height=height)
        editor.focus_set()
        editor.bind("<Return>", lambda _event: self._commit_edit(row_id, column_index, editor))
        editor.bind("<Escape>", lambda _event: self._cancel_edit())
        editor.bind("<FocusOut>", lambda _event: self._commit_edit(row_id, column_index, editor))

    def _commit_edit(self, row_id: str, column_index: int, editor) -> None:
        if editor is not self._editor:
            return
        # Mark the edit complete before destroying the Entry. Destroying a
        # focused editor can also produce FocusOut, so its second callback
        # must become a no-op.
        self._editor = None
        try:
            if not editor.winfo_exists() or not self.tree.exists(row_id):
                if editor.winfo_exists():
                    editor.destroy()
                return
            values = list(self.tree.item(row_id, "values"))
            values[column_index] = editor.get().strip()
            model = self._parse_values(values)
            self.tree.item(row_id, values=self._display_values(model))
        except (ValueError, TypeError, OverflowError):
            if editor.winfo_exists():
                editor.destroy()
            self.on_error("Enter a phase A/B/C and valid coordinates, radius, and self GMR. Radius and GMR must be positive.")
            return
        except tk.TclError:
            # The row or Entry can disappear during a focus change (for
            # example, when Remove or Clear all is clicked).
            if editor.winfo_exists():
                editor.destroy()
            return
        if editor.winfo_exists():
            editor.destroy()
        self.on_change()

    def _cancel_edit(self) -> None:
        editor, self._editor = self._editor, None
        if editor is not None:
            try:
                if editor.winfo_exists():
                    editor.destroy()
            except tk.TclError:
                pass
