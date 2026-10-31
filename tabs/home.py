"""Friendly starting screen for choosing a transmission-line workflow."""

import customtkinter as ctk

from theme import COLORS, BLUE, MINT, YELLOW
from widgets.neo import NeoButton, NeoCard


class HomeTab(ctk.CTkFrame):
    CARDS = (
        ("🧩", "BUILD IT YOURSELF", "Add conductors one by one", "build", BLUE),
        ("⚡", "TRY AN EXAMPLE", "Textbook problems 4.2 to 4.6", "example", YELLOW),
        ("🔬", "STRANDED WIRE GMR", "Find the effective radius", "gmr", MINT),
    )

    def __init__(self, master, *, on_action):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure((0, 1), weight=1, uniform="home")
        self.grid_rowconfigure((2, 3), weight=1)
        self.grid_rowconfigure(0, minsize=48)
        self.grid_rowconfigure(1, minsize=42)
        self.grid_rowconfigure(4, minsize=52)
        ctk.CTkLabel(
            self, text="HI! WHAT ARE WE SOLVING TODAY?", text_color=COLORS["text"],
            font=ctk.CTkFont("Arial Black", 24, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(22, 8))
        ctk.CTkLabel(
            self, text="Pick a starting point. You can change every value before calculating.",
            text_color=COLORS["muted"], font=ctk.CTkFont("Segoe UI", 14),
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 18))
        for index, (icon, title, subtitle, key, fill) in enumerate(self.CARDS):
            row, column = divmod(index, 2)
            card = NeoCard(self, fill=fill)
            card.grid(row=row + 2, column=column, columnspan=2 if index == 2 else 1,
                      sticky="nsew", padx=14, pady=14)
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont("Segoe UI Emoji", 27),
                         text_color=COLORS["text"], bg_color=fill).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 1))
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont("Arial Black", 18, weight="bold"),
                         text_color=COLORS["text"], bg_color=fill).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 1))
            ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont("Segoe UI", 14),
                         text_color=COLORS["muted"], bg_color=fill).grid(row=2, column=0, sticky="w", padx=18)
            NeoButton(card, text="OPEN →", height=42,
                          fg_color=COLORS["surface"], hover_color=COLORS["hover"],
                          command=lambda selected=key: on_action(selected)
                          ).grid(row=3, column=0, sticky="w", padx=18, pady=(9, 14))
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(8, 14))
        bottom.grid_columnconfigure(0, weight=1)
        self.recent = ctk.CTkFrame(bottom, fg_color="transparent")
        self.recent.grid(row=0, column=0, sticky="w")
        self.recent_label = ctk.CTkLabel(self.recent, text="Recent: no calculations yet",
                                         text_color=COLORS["muted"], font=ctk.CTkFont("Segoe UI", 13),
                                         wraplength=820, justify="left")
        self.recent_label.pack(side="left")

    def add_recent(self, title: str) -> None:
        previous = self.recent_label.cget("text").replace("Recent: ", "")
        entries = [] if previous == "no calculations yet" else previous.split(" · ")
        entries.insert(0, title)
        self.recent_label.configure(text="Recent: " + " · ".join(entries[:5]))
