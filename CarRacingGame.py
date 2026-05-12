import tkinter as tk
import random
import json
import os

# ─── SOUND HELPER ────────────────────────────────────────────
def beep(freq=800, dur=60):
        pass

# ─── CONSTANTS ───────────────────────────────────────────────
WIDTH        = 420
HEIGHT       = 650
LANE_COUNT   = 3
ROAD_LEFT    = 60
ROAD_RIGHT   = WIDTH - 60
ROAD_W       = ROAD_RIGHT - ROAD_LEFT
LANE_W       = ROAD_W // LANE_COUNT
CAR_W        = 44
CAR_H        = 72
OBS_W        = 44
OBS_H        = 72
SCORE_FILE   = "highscore.json"

LANE_CENTERS = [
    ROAD_LEFT + LANE_W * 0 + LANE_W // 2,
    ROAD_LEFT + LANE_W * 1 + LANE_W // 2,
    ROAD_LEFT + LANE_W * 2 + LANE_W // 2,
]

DIFFICULTIES = {
    "Easy":   {"obs_speed": 5,  "obs_interval": 1400, "speed_inc": 0.3},
    "Medium": {"obs_speed": 8,  "obs_interval": 1000, "speed_inc": 0.5},
    "Hard":   {"obs_speed": 12, "obs_interval": 700,  "speed_inc": 0.8},
}

POWERUP_TYPES = ["shield", "slow", "bonus"]
POWERUP_COLORS = {"shield": "#00ff88", "slow": "#ffdd00", "bonus": "#ff69b4"}
POWERUP_LABELS = {"shield": "🛡", "slow": "🐢", "bonus": "⭐"}

THEMES = {
    "night": {
        "sky":        "#0a0a1a",
        "road":       "#1a1a2a",
        "lane_line":  "#ffff00",
        "grass":      "#0d2b0d",
        "border":     "#555577",
        "hud_bg":     "#111122",
        "hud_fg":     "#ffffff",
        "score_col":  "#00d4ff",
        "hi_col":     "#ffd700",
        "player_body":"#1e90ff",
        "player_top": "#87ceeb",
        "player_win": "#ffffff",
        "obs_colors": ["#ff3c3c","#ff6600","#cc00cc","#ff9900"],
        "stripe":     "#ffffff",
        "road_line":  "#333344",
    },
    "day": {
        "sky":        "#87ceeb",
        "road":       "#555566",
        "lane_line":  "#ffffff",
        "grass":      "#4caf50",
        "border":     "#888899",
        "hud_bg":     "#ddeeff",
        "hud_fg":     "#111133",
        "score_col":  "#0055cc",
        "hi_col":     "#cc7700",
        "player_body":"#1565c0",
        "player_top": "#42a5f5",
        "player_win": "#e3f2fd",
        "obs_colors": ["#d32f2f","#e64a19","#7b1fa2","#f57c00"],
        "stripe":     "#eeeeee",
        "road_line":  "#444455",
    }
}

# ─── HIGHSCORE ───────────────────────────────────────────────
def load_highscore():
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE) as f:
                return json.load(f).get("high", 0)
        except Exception:
            pass
    return 0

def save_highscore(val):
    try:
        with open(SCORE_FILE, "w") as f:
            json.dump({"high": val}, f)
    except Exception:
        pass

# ─── DRAW HELPERS ────────────────────────────────────────────
def draw_car(canvas, x, y, body, top, win, tag):
    """Draw a simple top-view car shape."""
    hw, hh = CAR_W // 2, CAR_H // 2
    # Body
    canvas.create_rectangle(x-hw, y-hh, x+hw, y+hh,
                             fill=body, outline="#222", width=2, tags=tag)
    # Roof / cabin
    canvas.create_rectangle(x-hw+8, y-hh+14, x+hw-8, y+hh-14,
                             fill=top, outline="", tags=tag)
    # Windshield
    canvas.create_rectangle(x-hw+10, y-hh+16, x+hw-10, y-hh+30,
                             fill=win, outline="", tags=tag)
    # Rear window
    canvas.create_rectangle(x-hw+10, y+hh-30, x+hw-10, y+hh-16,
                             fill=win, outline="", tags=tag)
    # Wheels
    for wx, wy in [(x-hw-2, y-hh+10),(x+hw+2, y-hh+10),
                   (x-hw-2, y+hh-10),(x+hw+2, y+hh-10)]:
        canvas.create_rectangle(wx-5, wy-8, wx+5, wy+8,
                                 fill="#111", outline="", tags=tag)

def draw_obs_car(canvas, x, y, color, tag):
    hw, hh = OBS_W // 2, OBS_H // 2
    canvas.create_rectangle(x-hw, y-hh, x+hw, y+hh,
                             fill=color, outline="#111", width=2, tags=tag)
    canvas.create_rectangle(x-hw+8, y-hh+14, x+hw-8, y+hh-14,
                             fill="#222", outline="", tags=tag)
    canvas.create_rectangle(x-hw+10, y-hh+16, x+hw-10, y-hh+30,
                             fill="#ff4444", outline="", tags=tag)
    canvas.create_rectangle(x-hw+10, y+hh-30, x+hw-10, y+hh-16,
                             fill="#882222", outline="", tags=tag)
    for wx, wy in [(x-hw-2, y-hh+10),(x+hw+2, y-hh+10),
                   (x-hw-2, y+hh-10),(x+hw+2, y+hh-10)]:
        canvas.create_rectangle(wx-5, wy-8, wx+5, wy+8,
                                 fill="#111", outline="", tags=tag)

# ─── GAME CLASS ──────────────────────────────────────────────
class CarRacingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🚗 Car Racing Game – Ultimate Edition")
        self.root.resizable(False, False)

        self.theme_name  = "night"
        self.T           = THEMES[self.theme_name]
        self.difficulty  = "Medium"
        self.high_score  = load_highscore()

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=self.T["sky"], highlightthickness=0)
        self.canvas.pack()

        # Key bindings
        root.bind("<Left>",  self._lane_left)
        root.bind("<Right>", self._lane_right)
        root.bind("<r>",     lambda e: self._restart())
        root.bind("<R>",     lambda e: self._restart())

        self._show_menu()

    # ── MENU SCREEN ──────────────────────────────────────────
    def _show_menu(self):
        self.canvas.delete("all")
        T = self.T
        self.canvas.configure(bg=T["sky"])
        self._draw_road_bg()

        # Title
        self.canvas.create_text(WIDTH//2, 90,
            text="🚗  CAR RACING", font=("Segoe UI", 26, "bold"),
            fill="#00d4ff", tags="menu")
        self.canvas.create_text(WIDTH//2, 125,
            text="ULTIMATE EDITION", font=("Segoe UI", 12, "bold"),
            fill="#ffffff", tags="menu")

        # High score
        self.canvas.create_text(WIDTH//2, 165,
            text=f"🏆 Best: {self.high_score}",
            font=("Segoe UI", 13, "bold"),
            fill=T["hi_col"], tags="menu")

        # Difficulty buttons
        self.canvas.create_text(WIDTH//2, 215,
            text="Select Difficulty:", font=("Segoe UI", 11),
            fill="#aaccff", tags="menu")

        btn_y = 255
        for diff in ["Easy", "Medium", "Hard"]:
            col = {"Easy":"#00cc66","Medium":"#ffaa00","Hard":"#ff3333"}[diff]
            btn = tk.Button(self.root, text=diff,
                font=("Segoe UI", 11, "bold"),
                bg=col, fg="white", relief="flat",
                padx=20, pady=6, cursor="hand2",
                command=lambda d=diff: self._select_difficulty(d))
            self.canvas.create_window(WIDTH//2, btn_y, window=btn, tags="menu")
            btn_y += 50

        # Theme toggle
        theme_lbl = "☀️ Day Mode" if self.theme_name == "night" else "🌙 Night Mode"
        tb = tk.Button(self.root, text=theme_lbl,
            font=("Segoe UI", 10, "bold"),
            bg="#334466", fg="white", relief="flat",
            padx=14, pady=5, cursor="hand2",
            command=self._toggle_theme_menu)
        self.canvas.create_window(WIDTH//2, btn_y + 10, window=tb, tags="menu")

        # Start
        sb = tk.Button(self.root, text="▶  START GAME",
            font=("Segoe UI", 13, "bold"),
            bg="#1e90ff", fg="white", relief="flat",
            padx=24, pady=10, cursor="hand2",
            command=self._start_game)
        self.canvas.create_window(WIDTH//2, HEIGHT - 90, window=sb, tags="menu")

        self.canvas.create_text(WIDTH//2, HEIGHT - 40,
            text="← → Arrow Keys to change lane  |  R to Restart",
            font=("Segoe UI", 8), fill="#778899", tags="menu")

    def _select_difficulty(self, diff):
        self.difficulty = diff
        self._show_menu()

    def _toggle_theme_menu(self):
        self.theme_name = "day" if self.theme_name == "night" else "night"
        self.T = THEMES[self.theme_name]
        self._show_menu()

    # ── INIT GAME ────────────────────────────────────────────
    def _start_game(self):
        self.canvas.delete("all")
        T  = self.T
        cfg = DIFFICULTIES[self.difficulty]

        self.score        = 0
        self.running      = True
        self.shielded     = False
        self.slowed       = False
        self.shield_timer = 0
        self.slow_timer   = 0
        self.obs_speed    = cfg["obs_speed"]
        self.base_speed   = cfg["obs_speed"]
        self.obs_interval = cfg["obs_interval"]
        self.speed_inc    = cfg["speed_inc"]
        self.player_lane  = 1          # 0=left 1=center 2=right
        self.player_x     = LANE_CENTERS[1]
        self.player_y     = HEIGHT - 100
        self.obstacles    = []         # {id, x, y, tag}
        self.powerups     = []         # {id, x, y, kind, tag}
        self.road_offset  = 0
        self.dodge_count  = 0
        self.frame_count  = 0

        self.canvas.configure(bg=T["sky"])
        self._draw_road_bg()
        self._draw_hud()
        self._draw_player()
        self._spawn_obstacle()
        self._game_loop()

    # ── ROAD BACKGROUND ──────────────────────────────────────
    def _draw_road_bg(self):
        T = self.T
        # Grass sides
        self.canvas.create_rectangle(0, 0, ROAD_LEFT, HEIGHT,
                                     fill=T["grass"], outline="", tags="bg")
        self.canvas.create_rectangle(ROAD_RIGHT, 0, WIDTH, HEIGHT,
                                     fill=T["grass"], outline="", tags="bg")
        # Road
        self.canvas.create_rectangle(ROAD_LEFT, 0, ROAD_RIGHT, HEIGHT,
                                     fill=T["road"], outline="", tags="bg")
        # Road borders
        self.canvas.create_line(ROAD_LEFT, 0, ROAD_LEFT, HEIGHT,
                                fill=T["border"], width=4, tags="bg")
        self.canvas.create_line(ROAD_RIGHT, 0, ROAD_RIGHT, HEIGHT,
                                fill=T["border"], width=4, tags="bg")

    def _draw_lane_lines(self):
        T = self.T
        self.canvas.delete("laneline")
        off = self.road_offset % 60
        for lane in [1, 2]:  # dividers between lanes
            lx = ROAD_LEFT + LANE_W * lane
            y = -60 + off
            while y < HEIGHT:
                self.canvas.create_line(lx, y, lx, y+35,
                    fill=T["lane_line"], width=2,
                    dash=(10,8), tags="laneline")
                y += 60

    # ── HUD ──────────────────────────────────────────────────
    def _draw_hud(self):
        T = self.T
        self.canvas.create_rectangle(0, 0, WIDTH, 46,
                                     fill=T["hud_bg"], outline="", tags="hud")
        self.score_txt = self.canvas.create_text(
            10, 23, anchor="w",
            text=f"⭐ Score: {self.score}",
            font=("Segoe UI", 12, "bold"),
            fill=T["score_col"], tags="hud")
        self.hi_txt = self.canvas.create_text(
            WIDTH//2, 23, anchor="center",
            text=f"🏆 Best: {self.high_score}",
            font=("Segoe UI", 11, "bold"),
            fill=T["hi_col"], tags="hud")
        self.diff_txt = self.canvas.create_text(
            WIDTH-10, 23, anchor="e",
            text=self.difficulty,
            font=("Segoe UI", 11, "bold"),
            fill={"Easy":"#00cc66","Medium":"#ffaa00","Hard":"#ff3333"}[self.difficulty],
            tags="hud")
        # Power-up status
        self.pu_txt = self.canvas.create_text(
            WIDTH//2, HEIGHT - 20, anchor="center",
            text="",
            font=("Segoe UI", 10, "bold"),
            fill="#00ff88", tags="hud")

    def _update_hud(self):
        self.canvas.itemconfig(self.score_txt, text=f"⭐ Score: {self.score}")
        self.canvas.itemconfig(self.hi_txt,    text=f"🏆 Best: {self.high_score}")
        pu_parts = []
        if self.shielded:   pu_parts.append(f"🛡 Shield {self.shield_timer//10}s")
        if self.slowed:     pu_parts.append(f"🐢 Slow {self.slow_timer//10}s")
        self.canvas.itemconfig(self.pu_txt, text="  ".join(pu_parts))

    # ── PLAYER CAR ───────────────────────────────────────────
    def _draw_player(self):
        self.canvas.delete("player")
        T = self.T
        col = "#00ff88" if self.shielded else T["player_body"]
        draw_car(self.canvas, self.player_x, self.player_y,
                 col, T["player_top"], T["player_win"], "player")

    # ── LANE CONTROL ─────────────────────────────────────────
    def _lane_left(self, event=None):
        if self.running and self.player_lane > 0:
            self.player_lane -= 1
            self.player_x = LANE_CENTERS[self.player_lane]
            self._draw_player()
            beep(600, 40)

    def _lane_right(self, event=None):
        if self.running and self.player_lane < 2:
            self.player_lane += 1
            self.player_x = LANE_CENTERS[self.player_lane]
            self._draw_player()
            beep(600, 40)

    # ── SPAWN OBSTACLE ───────────────────────────────────────
    def _spawn_obstacle(self):
        if not self.running:
            return
        T = self.T
        lane = random.randint(0, 2)
        x    = LANE_CENTERS[lane]
        y    = -OBS_H
        tag  = f"obs_{id(object())}"
        col  = random.choice(T["obs_colors"])
        draw_obs_car(self.canvas, x, y, col, tag)
        self.obstacles.append({"x": x, "y": y, "tag": tag, "lane": lane})
        self.canvas.tag_lower(tag, "player")

        # Possibly spawn a power-up too
        if random.random() < 0.25:
            self.root.after(self.obs_interval // 2, self._spawn_powerup)

        next_ms = max(400, int(self.obs_interval * (0.75 if self.slowed else 1.0)))
        self.root.after(next_ms, self._spawn_obstacle)

    def _spawn_powerup(self):
        if not self.running:
            return
        T = self.T
        lane = random.randint(0, 2)
        x    = LANE_CENTERS[lane]
        y    = -30
        kind = random.choice(POWERUP_TYPES)
        tag  = f"pu_{id(object())}"
        col  = POWERUP_COLORS[kind]
        lbl  = POWERUP_LABELS[kind]
        r = 20
        self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                fill=col, outline="white", width=2, tags=tag)
        self.canvas.create_text(x, y, text=lbl,
                                font=("Segoe UI", 14), tags=tag)
        self.powerups.append({"x": x, "y": y, "tag": tag, "kind": kind})

    # ── GAME LOOP ────────────────────────────────────────────
    def _game_loop(self):
        if not self.running:
            return
        self.frame_count += 1

        # Scroll road
        self.road_offset += self.obs_speed
        self._draw_lane_lines()
        self.canvas.tag_raise("hud")
        self.canvas.tag_raise("player")

        # Move obstacles
        dead_obs = []
        for obs in self.obstacles:
            spd = self.obs_speed * (0.5 if self.slowed else 1.0)
            obs["y"] += spd
            self.canvas.move(obs["tag"], 0, spd)
            if obs["y"] > HEIGHT + OBS_H:
                self.canvas.delete(obs["tag"])
                dead_obs.append(obs)
                self.score += 1
                self.dodge_count += 1
                if self.score > self.high_score:
                    self.high_score = self.score
                    save_highscore(self.high_score)
                # Speed up every 5 dodges
                if self.dodge_count % 5 == 0:
                    self.obs_speed = min(self.base_speed + self.speed_inc * (self.dodge_count // 5), 25)
                beep(1100, 30)

        for o in dead_obs:
            self.obstacles.remove(o)

        # Move power-ups
        dead_pu = []
        for pu in self.powerups:
            spd = self.obs_speed * (0.5 if self.slowed else 1.0)
            pu["y"] += spd
            self.canvas.move(pu["tag"], 0, spd)
            if pu["y"] > HEIGHT + 40:
                self.canvas.delete(pu["tag"])
                dead_pu.append(pu)
            elif self._pu_collision(pu):
                self._apply_powerup(pu["kind"])
                self.canvas.delete(pu["tag"])
                dead_pu.append(pu)
        for p in dead_pu:
            if p in self.powerups:
                self.powerups.remove(p)

        # Power-up timers
        if self.shielded:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shielded = False
                self._draw_player()
        if self.slowed:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.slowed = False

        # Collision check
        for obs in self.obstacles:
            if self._collision(obs):
                if self.shielded:
                    # Shield absorbs one hit
                    self.shielded     = False
                    self.shield_timer = 0
                    self.canvas.delete(obs["tag"])
                    self.obstacles.remove(obs)
                    beep(800, 150)
                    self._draw_player()
                    break
                else:
                    self._game_over()
                    return

        self._update_hud()
        self.root.after(16, self._game_loop)   # ~60 fps

    # ── COLLISION HELPERS ─────────────────────────────────────
    def _collision(self, obs):
        px, py = self.player_x, self.player_y
        ox, oy = obs["x"], obs["y"]
        return (abs(px - ox) < (CAR_W + OBS_W) // 2 - 6 and
                abs(py - oy) < (CAR_H + OBS_H) // 2 - 10)

    def _pu_collision(self, pu):
        px, py = self.player_x, self.player_y
        return (abs(px - pu["x"]) < CAR_W // 2 + 20 and
                abs(py - pu["y"]) < CAR_H // 2 + 20)

    # ── POWER-UP APPLY ───────────────────────────────────────
    def _apply_powerup(self, kind):
        beep(1400, 80)
        if kind == "shield":
            self.shielded     = True
            self.shield_timer = 200   # ~3.2 sec at 60fps
            self._draw_player()
        elif kind == "slow":
            self.slowed     = True
            self.slow_timer = 180
        elif kind == "bonus":
            self.score      += 10
            if self.score > self.high_score:
                self.high_score = self.score
                save_highscore(self.high_score)
        self._update_hud()

    # ── GAME OVER ────────────────────────────────────────────
    def _game_over(self):
        self.running = False
        beep(300, 150)
        self.root.after(80,  lambda: beep(250, 150))
        self.root.after(160, lambda: beep(200, 300))

        # Overlay
        self.canvas.create_rectangle(
            WIDTH//2-170, HEIGHT//2-110,
            WIDTH//2+170, HEIGHT//2+130,
            fill="#0a0a1a", outline="#ff3c3c", width=3, tags="gameover"
        )
        self.canvas.create_text(WIDTH//2, HEIGHT//2-75,
            text="💥 GAME OVER 💥",
            font=("Segoe UI", 20, "bold"),
            fill="#ff3c3c", tags="gameover")
        self.canvas.create_text(WIDTH//2, HEIGHT//2-35,
            text=f"Score: {self.score}",
            font=("Segoe UI", 16, "bold"),
            fill="#ffffff", tags="gameover")
        hi_col = "#ffd700" if self.score >= self.high_score else "#aaaacc"
        self.canvas.create_text(WIDTH//2, HEIGHT//2,
            text=f"🏆 Best: {self.high_score}",
            font=("Segoe UI", 13, "bold"),
            fill=hi_col, tags="gameover")
        self.canvas.create_text(WIDTH//2, HEIGHT//2+35,
            text=f"Difficulty: {self.difficulty}",
            font=("Segoe UI", 11),
            fill={"Easy":"#00cc66","Medium":"#ffaa00","Hard":"#ff3333"}[self.difficulty],
            tags="gameover")

        rb = tk.Button(self.root, text="🔄 Restart",
            font=("Segoe UI", 12, "bold"),
            bg="#1e90ff", fg="white", relief="flat",
            padx=18, pady=8, cursor="hand2",
            command=self._restart)
        self.canvas.create_window(WIDTH//2-60, HEIGHT//2+90,
                                  window=rb, tags="gameover")

        mb = tk.Button(self.root, text="🏠 Menu",
            font=("Segoe UI", 12, "bold"),
            bg="#555577", fg="white", relief="flat",
            padx=18, pady=8, cursor="hand2",
            command=self._go_menu)
        self.canvas.create_window(WIDTH//2+65, HEIGHT//2+90,
                                  window=mb, tags="gameover")

    def _restart(self):
        self.canvas.delete("all")
        self._start_game()

    def _go_menu(self):
        self.canvas.delete("all")
        self._show_menu()


# ─── ENTRY POINT ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{WIDTH}x{HEIGHT}")
    game = CarRacingGame(root)
    root.mainloop()
