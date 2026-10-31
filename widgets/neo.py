"""Neubrutalist Tk surfaces and buttons with crisp ink borders and shadows."""

import tkinter as tk
import customtkinter as ctk

from theme import BG, BORDER_WIDTH, HOVER_TINT, INK, RADIUS, SHADOW_LARGE, SHADOW_NORMAL, SURFACE


class _HardShadow:
    """Add a solid offset rectangle behind a normal geometry-managed widget."""

    def _init_shadow(self, master, offset: int) -> None:
        self._shadow_offset = offset
        self._shadow_hidden = False
        self._shadow_widget = tk.Frame(master, bg=INK, bd=0, highlightthickness=0)
        self.bind("<Configure>", self._sync_shadow, add="+")
        self.bind("<Destroy>", self._destroy_shadow, add="+")

    def _sync_shadow(self, _event=None) -> None:
        try:
            if self._shadow_hidden or (isinstance(self, ctk.CTkButton) and self.cget("state") == "disabled"):
                self._shadow_widget.place_forget()
                return
            if not self.winfo_ismapped() or self.winfo_width() < 2 or self.winfo_height() < 2:
                self._shadow_widget.place_forget()
                return
            self._shadow_widget.place(
                x=self.winfo_x() + self._shadow_offset,
                y=self.winfo_y() + self._shadow_offset,
                width=self.winfo_width(), height=self.winfo_height(),
            )
            # Keep the offset shadow behind every sibling in its parent. If it
            # is only lowered below its owner, it can sit above unrelated
            # widgets and appear as a stray black patch after relayouts.
            self._shadow_widget.lower()
        except tk.TclError:
            pass

    def _destroy_shadow(self, event) -> None:
        if event.widget is self:
            try:
                self._shadow_widget.destroy()
            except tk.TclError:
                pass


class NeoSurface(_HardShadow, tk.Frame):
    """Square-cornered, outlined card suitable for normal Tk child widgets."""

    def __init__(self, master, *, fill=SURFACE, shadow=SHADOW_LARGE, **kwargs):
        # Accept old surface options while callers are migrated.
        kwargs.pop("radius", None)
        kwargs.pop("padding", None)
        kwargs.pop("mode", None)
        tk.Frame.__init__(self, master, bg=fill, bd=0, highlightthickness=BORDER_WIDTH,
                          highlightbackground=INK, highlightcolor=INK, **kwargs)
        self._init_shadow(master, shadow)


class NeoCard(NeoSurface):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("shadow", SHADOW_LARGE)
        super().__init__(master, **kwargs)


class NeoWell(NeoSurface):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("shadow", SHADOW_NORMAL)
        kwargs.setdefault("fill", SURFACE)
        super().__init__(master, **kwargs)


class NeoTile(NeoSurface):
    def __init__(self, master, *, fill=SURFACE, **kwargs):
        kwargs.setdefault("shadow", 5)
        super().__init__(master, fill=fill, **kwargs)


class NeoButton(_HardShadow, ctk.CTkButton):
    """CustomTkinter button styled as a bordered, hard-shadowed key."""

    def __init__(self, master, **kwargs):
        kwargs.update(
            corner_radius=RADIUS,
            border_width=BORDER_WIDTH,
            border_color=INK,
            text_color=INK,
        )
        kwargs.setdefault("fg_color", SURFACE)
        kwargs.setdefault("hover_color", HOVER_TINT)
        ctk.CTkButton.__init__(self, master, **kwargs)
        self._init_shadow(master, SHADOW_NORMAL)
        self.bind("<Enter>", self._lift_shadow, add="+")
        self.bind("<Leave>", self._restore_shadow, add="+")
        self.bind("<ButtonPress-1>", self._press_shadow, add="+")
        self.bind("<ButtonRelease-1>", self._release_shadow, add="+")

    def _lift_shadow(self, _event=None):
        if self.cget("state") != "disabled":
            self._shadow_offset = SHADOW_LARGE
            self._sync_shadow()

    def _restore_shadow(self, _event=None):
        self._shadow_hidden = False
        self._shadow_offset = SHADOW_NORMAL
        self._sync_shadow()

    def _press_shadow(self, _event=None):
        self._shadow_hidden = True
        self._sync_shadow()

    def _release_shadow(self, event=None):
        self._shadow_hidden = False
        if event and 0 <= event.x < self.winfo_width() and 0 <= event.y < self.winfo_height():
            self._shadow_offset = SHADOW_LARGE
        else:
            self._shadow_offset = SHADOW_NORMAL
        self._sync_shadow()

    def configure(self, require_redraw=False, **kwargs):
        state_changed = "state" in kwargs
        result = ctk.CTkButton.configure(self, require_redraw, **kwargs)
        if state_changed and hasattr(self, "_shadow_widget"):
            self.after_idle(self._sync_shadow)
        return result
