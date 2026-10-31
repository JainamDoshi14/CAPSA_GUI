"""Root window for Transmission Line Studio."""

import customtkinter as ctk
import tkinter as tk

from theme import COLORS
from tabs.composite_tab import CompositeConductorTab
from tabs.line_tab import LineParametersTab
from tabs.home import HomeTab
from widgets.neo import NeoButton

ctk.set_appearance_mode("light")


class TransmissionLineStudio(ctk.CTk):
    """Root window for the Transmission Line Studio desktop app."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Transmission Line Studio")
        self.geometry("1200x720")
        self.minsize(960, 640)
        self.configure(fg_color=COLORS["bg"])
        self._window_icon = tk.PhotoImage(width=32, height=32)
        self._window_icon.put(COLORS["surface"], to=(0, 0, 32, 32))
        for x, color in ((8, COLORS["primary"]), (15, COLORS["sky"]), (22, COLORS["pink"])):
            for y in range(7, 26):
                self._window_icon.put(color, to=(x, y, x + 3, y + 3))
        self.iconphoto(True, self._window_icon)

        # Keep the workspace hidden until all tabs have been constructed and
        # Tk has had a chance to paint their first frame.
        self.withdraw()
        self._show_loading_screen()
        self.after(80, self._build_workspace)

    def _show_loading_screen(self) -> None:
        self._splash = ctk.CTkToplevel(self)
        self._splash.title("Loading Transmission Line Studio")
        self._splash.geometry("440x230")
        self._splash.resizable(False, False)
        self._splash.overrideredirect(True)
        self._splash.configure(fg_color=COLORS["bg"])
        self._splash.update_idletasks()
        x = (self._splash.winfo_screenwidth() - 440) // 2
        y = (self._splash.winfo_screenheight() - 230) // 2
        self._splash.geometry(f"440x230+{x}+{y}")

        panel = ctk.CTkFrame(self._splash, fg_color=COLORS["surface"],
                             border_width=3, border_color=COLORS["text"], corner_radius=8)
        panel.pack(fill="both", expand=True, padx=8, pady=8)
        ctk.CTkLabel(panel, text="TRANSMISSION LINE STUDIO",
                     font=ctk.CTkFont("Arial Black", 21, weight="bold"),
                     text_color=COLORS["text"]).pack(pady=(38, 7))
        ctk.CTkLabel(panel, text="Getting your workspace ready…",
                     font=ctk.CTkFont("Segoe UI", 14),
                     text_color=COLORS["muted"]).pack(pady=(0, 20))
        self._loading_bar = ctk.CTkProgressBar(panel, width=300,
                                               progress_color=COLORS["primary"])
        self._loading_bar.pack()
        self._loading_bar.start()
        self._splash.deiconify()
        self._splash.lift()

    def _build_workspace(self) -> None:
        try:
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

            self.content = ctk.CTkFrame(self, fg_color="transparent")
            self.content.grid(row=0, column=0, sticky="nsew", padx=32, pady=16)
            self.content.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                self.content, text="TRANSMISSION LINE STUDIO",
                font=ctk.CTkFont(family="Arial Black", size=28, weight="bold"),
                text_color=COLORS["text"],
            ).grid(row=0, column=0, sticky="w", pady=(0, 8))
            NeoButton(
                self.content, text="ABOUT", width=90, height=42,
                fg_color=COLORS["surface_2"], hover_color=COLORS["hover"],
                text_color=COLORS["text"], command=self._show_about,
            ).grid(row=0, column=1, sticky="e", pady=(0, 8))
            self.tabs = ctk.CTkTabview(
                self.content, fg_color=COLORS["surface"],
                segmented_button_fg_color=COLORS["surface_2"],
                segmented_button_selected_color=COLORS["primary_2"],
                segmented_button_selected_hover_color=COLORS["primary"],
                segmented_button_unselected_color=COLORS["surface_2"],
                segmented_button_unselected_hover_color=COLORS["hover"],
                text_color=COLORS["text"], corner_radius=4, border_width=3,
                border_color=COLORS["border"], command=self._view_changed,
            )
            self.tabs.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
            self.content.grid_rowconfigure(1, weight=1)

            home_tab = self.tabs.add("Home")
            self.home = HomeTab(home_tab, on_action=self._home_action)
            self.home.pack(fill="both", expand=True)
            self.composite_tab = self.tabs.add("Stranded wire GMR")
            self.line_tab = self.tabs.add("Line parameters")
            self.after(50, self._build_composite_tab)
        except Exception:
            self._finish_loading(show_main=True)
            raise

    def _build_composite_tab(self) -> None:
        try:
            CompositeConductorTab(self.composite_tab).pack(fill="both", expand=True)
            self.after(50, self._build_line_tab)
        except Exception:
            self._finish_loading(show_main=True)
            raise

    def _build_line_tab(self) -> None:
        try:
            self.line_parameters_tab = LineParametersTab(self.line_tab, on_result=self._record_result)
            self.line_parameters_tab.pack(fill="both", expand=True)
            self.bind("<Configure>", self._on_window_resize, add="+")
            self.bind_all("<Control-Return>", self._compute_shortcut)
            self.after(120, self._finish_loading)
        except Exception:
            self._finish_loading(show_main=True)
            raise

    def _finish_loading(self, show_main: bool = False) -> None:
        if hasattr(self, "_loading_bar"):
            self._loading_bar.stop()
        if show_main or self.winfo_exists():
            self.deiconify()
            self.update_idletasks()
        if hasattr(self, "_splash"):
            try:
                self._splash.destroy()
            except tk.TclError:
                pass

    def _home_action(self, action: str) -> None:
        if action == "gmr":
            self.tabs.set("Stranded wire GMR")
        elif action in {"build", "example"}:
            self.tabs.set("Line parameters")
            self.after(100, self.line_parameters_tab._layout_panels)
            if action == "example":
                self.line_parameters_tab.select_preset("Q2")
                self.line_parameters_tab.load_preset()

    def _view_changed(self) -> None:
        if self.tabs.get() == "Line parameters":
            self.after(100, self.line_parameters_tab._layout_panels)

    def _on_window_resize(self, event) -> None:
        if event.widget is self and self.line_parameters_tab is not None:
            self.after(100, self.line_parameters_tab._layout_panels)

    def _record_result(self, model) -> None:
        self.home.add_recent(model.name)

    def _compute_shortcut(self, _event=None):
        if self.tabs.get() == "Line parameters":
            self.line_parameters_tab.compute()
            return "break"
        if self.tabs.get() == "Home":
            self.tabs.set("Line parameters")
            self.line_parameters_tab.compute()
            return "break"
        return None

    def _show_about(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("About Transmission Line Studio")
        dialog.geometry("390x230")
        dialog.resizable(False, False)
        dialog.transient(self)
        ctk.CTkLabel(
            dialog, text="Transmission Line Studio", text_color=COLORS["text"],
            font=ctk.CTkFont("Segoe UI", 20, weight="bold"),
        ).pack(padx=24, pady=(28, 8))
        ctk.CTkLabel(
            dialog, text="Version 1.0\nA desktop workspace for transmission-line calculations.\nBuilt with Python and CustomTkinter.",
            text_color=COLORS["muted"], justify="center", font=ctk.CTkFont("Segoe UI", 12),
        ).pack(padx=24, pady=8)
        NeoButton(dialog, text="Close", command=dialog.destroy).pack(pady=(10, 22))
