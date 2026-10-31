"""Live geometry view for line conductors."""

from dataclasses import replace
from math import hypot
import tkinter as tk
from collections.abc import Sequence

from core.models import Conductor
from theme import COLORS, INK, GRID, SURFACE, FONT_BODY, FONT_MONO, BORDER_WIDTH


PHASE_COLORS = {"A": COLORS["pink"], "B": COLORS["amber"], "C": COLORS["sky"]}


class GeometryCanvas(tk.Canvas):
    def __init__(self, master, *, on_drag=None, **kwargs):
        super().__init__(master, background=COLORS["surface"], highlightthickness=0, **kwargs)
        self.conductors: list[Conductor] = []
        self.show_distances = False
        self.on_drag = on_drag or (lambda _index, _conductor: None)
        self._screen_points: list[tuple[float, float]] = []
        self._transform = None
        self._drag_transform = None
        self._drag_index: int | None = None
        self._hover_label: int | None = None
        self.bind("<Configure>", lambda _event: self.redraw())
        self.bind("<ButtonPress-1>", self._start_drag)
        self.bind("<B1-Motion>", self._move_drag)
        self.bind("<ButtonRelease-1>", self._finish_drag)
        self.bind("<Motion>", self._show_hover)

    def set_model(self, conductors: Sequence[Conductor], show_distances: bool | None = None) -> None:
        self.conductors = list(conductors)
        if show_distances is not None:
            self.show_distances = show_distances
        self.redraw()

    def redraw(self) -> None:
        self.delete("all")
        width, height = max(self.winfo_width(), 320), max(self.winfo_height(), 180)
        for x in range(16, width, 32):
            self.create_line(x, 0, x, height, fill=GRID, dash=(1, 3))
        for y in range(16, height, 32):
            self.create_line(0, y, width, y, fill=GRID, dash=(1, 3))
        if not self.conductors:
            self.create_text(
                width / 2, height / 2,
                text="Your conductor layout will appear here",
                fill=COLORS["muted"], font=(FONT_BODY, 14),
            )
            return

        xs = [item.x for item in self.conductors]
        ys = [item.y for item in self.conductors]
        span_x = max(max(xs) - min(xs), 0.01)
        span_y = max(max(ys) - min(ys), 0.01)
        scale = min((width - 80) / span_x, (height - 68) / span_y)
        if span_x < 0.02:
            scale = (height - 68) / span_y
        if span_y < 0.02:
            scale = (width - 80) / span_x
        scale = max(1.0, min(scale, 180.0))
        center_x, center_y = width / 2, height / 2
        transform = self._drag_transform or (center_x, center_y, scale,
                                               (min(xs) + max(xs)) / 2,
                                               (min(ys) + max(ys)) / 2)
        center_x, center_y, scale, world_x, world_y = transform
        if self._drag_transform is None:
            self._transform = transform
        screen_points = [
            (center_x + (item.x - world_x) * scale,
             center_y - (item.y - world_y) * scale)
            for item in self.conductors
        ]
        self._screen_points = screen_points

        if self.show_distances:
            self._draw_phase_distances(screen_points)
        for index, (conductor, (x, y)) in enumerate(zip(self.conductors, screen_points)):
            radius = max(12, min(14, 10 + scale * conductor.r))
            color = PHASE_COLORS[conductor.phase]
            tags = (f"conductor-{index}", "conductor")
            self.create_oval(x-radius+4, y-radius+4, x+radius+4, y+radius+4,
                             fill=INK, outline=INK, width=0, tags=tags)
            self.create_oval(x-radius, y-radius, x+radius, y+radius,
                             fill=color, outline=INK, width=BORDER_WIDTH, tags=tags)
            self.create_text(x + radius + 10, y, anchor="w", text=conductor.phase,
                             fill=INK, font=(FONT_BODY, 12, "bold"))
        self.create_text(
            12, height - 12, anchor="w",
            text=f"{len(self.conductors)} sub-conductor{'s' if len(self.conductors) != 1 else ''} · coordinates in metres",
            fill=INK, font=(FONT_BODY, 11, "bold"),
        )

    def _draw_phase_distances(self, screen_points: list[tuple[float, float]]) -> None:
        by_phase = {phase: [] for phase in "ABC"}
        for index, conductor in enumerate(self.conductors):
            by_phase[conductor.phase].append((conductor, screen_points[index]))
        for first_phase, second_phase in (("A", "B"), ("B", "C"), ("C", "A")):
            if not by_phase[first_phase] or not by_phase[second_phase]:
                continue
            first, second = min(
                ((a, b) for a in by_phase[first_phase] for b in by_phase[second_phase]),
                key=lambda pair: hypot(pair[0][0].x - pair[1][0].x, pair[0][0].y - pair[1][0].y),
            )
            x1, y1 = first[1]
            x2, y2 = second[1]
            self.create_line(x1, y1, x2, y2, fill=INK, dash=(6, 4), width=3)
            distance_m = hypot(first[0].x - second[0].x, first[0].y - second[0].y)
            label = f"D{first_phase}{second_phase} = {distance_m:.4g} m"
            label_id = self.create_text(
                (x1+x2)/2, (y1+y2)/2-13, text=label,
                fill=INK, font=(FONT_MONO, 12, "bold"),
            )
            bounds = self.bbox(label_id)
            if bounds:
                pad = 4
                background_id = self.create_rectangle(
                    bounds[0]-pad, bounds[1]-2, bounds[2]+pad, bounds[3]+2,
                    fill=SURFACE, outline=INK, width=2,
                )
                self.tag_lower(background_id, label_id)

    def _nearest(self, x: float, y: float, radius: float = 20) -> int | None:
        if not self._screen_points:
            return None
        nearest = min(range(len(self._screen_points)), key=lambda i: hypot(
            self._screen_points[i][0] - x, self._screen_points[i][1] - y))
        sx, sy = self._screen_points[nearest]
        return nearest if hypot(sx - x, sy - y) <= radius else None

    def _start_drag(self, event) -> None:
        self._drag_index = self._nearest(self.canvasx(event.x), self.canvasy(event.y))
        if self._drag_index is not None:
            self._drag_transform = self._transform
            self.configure(cursor="fleur")

    def _move_drag(self, event) -> None:
        if self._drag_index is None or self._drag_transform is None:
            return
        center_x, center_y, scale, world_x, world_y = self._drag_transform
        x = (self.canvasx(event.x) - center_x) / scale + world_x
        y = (center_y - self.canvasy(event.y)) / scale + world_y
        self.conductors[self._drag_index] = replace(self.conductors[self._drag_index], x=x, y=y)
        self.redraw()

    def _finish_drag(self, _event) -> None:
        if self._drag_index is None:
            return
        index = self._drag_index
        conductor = self.conductors[index]
        self._drag_index = None
        self._drag_transform = None
        self.configure(cursor="")
        self.redraw()
        self.on_drag(index, conductor)

    def _show_hover(self, event) -> None:
        if self._drag_index is not None:
            return
        index = self._nearest(self.canvasx(event.x), self.canvasy(event.y))
        if self._hover_label is not None:
            self.delete(self._hover_label)
            self._hover_label = None
        if index is not None:
            item = self.conductors[index]
            x, y = self._screen_points[index]
            self._hover_label = self.create_text(
                x + 42, y - 20, anchor="w",
                text=f"Phase {item.phase} · x={item.x:.4g} m, y={item.y:.4g} m · drag to move",
                fill=INK, font=(FONT_BODY, 12, "bold"),
            )
