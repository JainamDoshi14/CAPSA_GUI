"""Responsive canvas diagram for hex-packed stranded conductors."""

from math import sqrt
import tkinter as tk

from core.gmr import stranded_layout
from theme import COLORS, INK, GRID, BLUE, YELLOW, FONT_BODY, FONT_MONO, BORDER_WIDTH


class StrandDiagram(tk.Canvas):
    def __init__(self, master, strand_count: int = 7, **kwargs):
        super().__init__(
            master,
            background=COLORS["surface"],
            highlightthickness=0,
            **kwargs,
        )
        self.strand_count = strand_count
        self.show_distances = False
        self.points: list[tuple[float, float]] = []
        self._screen_points: list[tuple[float, float, float]] = []
        self._hover_item: int | None = None
        self.bind("<Configure>", lambda _event: self.redraw())
        self.bind("<Motion>", self._on_motion)
        self.bind("<Leave>", self._on_leave)
        self.redraw()

    def set_strand_count(self, strand_count: int) -> None:
        self.strand_count = strand_count
        self.redraw()

    def set_show_distances(self, enabled: bool) -> None:
        self.show_distances = enabled
        self.redraw()

    def redraw(self) -> None:
        self.delete("all")
        width, height = max(self.winfo_width(), 300), max(self.winfo_height(), 240)
        self._draw_grid(width, height)
        self.points = self._packed_points(self.strand_count)
        x_values = [point[0] for point in self.points]
        y_values = [point[1] for point in self.points]
        span_x = max(max(x_values) - min(x_values), 2.0)
        span_y = max(max(y_values) - min(y_values), 2.0)
        # Layout coordinates are measured in strand-radius units: adjacent
        # strand centres are 2 units apart. Use the same pixels-per-unit for
        # the drawn strand radius so adjacent circles touch (centre spacing
        # = 2 × radius), while limiting the whole bundle to a compact size.
        scale = min(
            30.0,
            (width - 72) / (span_x + 2.0),
            (height - 82) / (span_y + 2.0),
        )
        radius_px = max(3.0, scale)
        center_x, center_y = width / 2, height / 2 - 5
        self._screen_points = [
            (center_x + (x - (min(x_values) + max(x_values)) / 2) * scale,
             center_y + (y - (min(y_values) + max(y_values)) / 2) * scale,
             radius_px)
            for x, y in self.points
        ]
        if self.show_distances:
            self._draw_distance_guides()
        for index, (x, y, radius) in enumerate(self._screen_points):
            fill = YELLOW if index == 0 else BLUE
            if self.strand_count == 3:
                fill = BLUE
            self.create_oval(x - radius + 4, y - radius + 4, x + radius + 4, y + radius + 4,
                             fill=INK, outline=INK, width=0, tags=(f"strand-{index}", "strand"))
            self.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill=fill, outline=INK, width=BORDER_WIDTH,
                tags=(f"strand-{index}", "strand"),
            )
            self.create_text(x, y, text=str(index + 1), fill=INK,
                             font=(FONT_MONO, 10, "bold"), tags=(f"strand-{index}", "strand"))
        self.create_text(
            width / 2, height - 20,
            text=f"{self.strand_count} strand{'s' if self.strand_count != 1 else ''} · hex-packed cross-section",
            fill=INK, font=(FONT_BODY, 12, "bold"),
        )

    def _draw_grid(self, width: int, height: int) -> None:
        grid_color = GRID
        for x in range(20, width, 32):
            self.create_line(x, 0, x, height, fill=grid_color, width=1, dash=(1, 3))
        for y in range(20, height, 32):
            self.create_line(0, y, width, y, fill=grid_color, width=1, dash=(1, 3))

    @staticmethod
    def _packed_points(strand_count: int) -> list[tuple[float, float]]:
        return stranded_layout(strand_count)

    def _draw_distance_guides(self) -> None:
        if len(self._screen_points) < 2:
            return
        center_x, center_y, _ = self._screen_points[0]
        candidates = sorted(
            range(1, len(self._screen_points)),
            key=lambda i: ((self._screen_points[i][0] - center_x) ** 2
                           + (self._screen_points[i][1] - center_y) ** 2),
        )
        targets = candidates[: min(6, len(candidates))]
        for index in targets:
            x, y, _ = self._screen_points[index]
            self.create_line(center_x, center_y, x, y, fill=INK, dash=(5, 4), width=3)
        if targets:
            x, y, _ = self._screen_points[targets[0]]
            text_id = self.create_text(
                (center_x + x) / 2 + 4, (center_y + y) / 2 - 12,
                text="Centre-to-centre spacing = 2r", fill=INK, font=(FONT_MONO, 12, "bold"),
            )
            bounds = self.bbox(text_id)
            if bounds:
                background = self.create_rectangle(bounds[0]-4, bounds[1]-2, bounds[2]+4, bounds[3]+2,
                                                   fill=COLORS["surface"], outline=INK, width=2)
                self.tag_lower(background, text_id)

    def _on_motion(self, event) -> None:
        nearest = None
        nearest_distance = float("inf")
        for index, (x, y, radius) in enumerate(self._screen_points):
            distance = sqrt((event.x - x) ** 2 + (event.y - y) ** 2)
            if distance <= radius and distance < nearest_distance:
                nearest, nearest_distance = index, distance
        if nearest == self._hover_item:
            return
        self._hover_item = nearest
        self.delete("tooltip")
        if nearest is None:
            return
        x, y, _ = self._screen_points[nearest]
        label = "center strand" if nearest == 0 and self.strand_count != 3 else f"strand {nearest + 1}"
        self.create_text(
            x, y - 36, text=label, fill=COLORS["text"],
            font=(FONT_BODY, 12, "bold"), tags="tooltip",
        )

    def _on_leave(self, _event) -> None:
        self._hover_item = None
        self.delete("tooltip")
