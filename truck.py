#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CYBER-TAKOYAKI: FOOD TRUCK HACKER
Neo-Tokio, 2088. Cocina comida callejera futurista y hackea a tus rivales.
Un solo archivo. Tkinter + threading + (opcional) pygame.mixer.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import random


try:
    import pygame

    PYGAME_OK = True
except ImportError:
    PYGAME_OK = False


def try_start_music():

    if not PYGAME_OK:
        return
    try:
        pygame.mixer.init()

        import os
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthwave.mp3")
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.75)
            pygame.mixer.music.play(-1)
    except Exception:
        pass



BG = "#0a0118"
PANEL = "#150a30"
PANEL2 = "#1d1042"
CYAN = "#00fff2"
MAGENTA = "#ff2bd6"
PURPLE = "#9d4bff"
YELLOW = "#f4ff00"
RED = "#ff2e4d"
GREEN = "#39ff88"
ORANGE = "#ff9a00"
GREY = "#5a5a7a"
WHITE = "#eae6ff"

FONT_S = ("Consolas", 9)
FONT = ("Consolas", 11)
FONT_B = ("Consolas", 11, "bold")
FONT_L = ("Consolas", 14, "bold")
FONT_T = ("Consolas", 22, "bold")


INGREDIENTS = {
    "Pulpo Sintético":        {"cost": 8,  "color": MAGENTA, "icon": "🐙"},
    "Salsa de Uranio Dulce":  {"cost": 6,  "color": GREEN,   "icon": "☢️"},
    "Fideos de Fibra Óptica": {"cost": 5,  "color": CYAN,    "icon": "🍜"},
    "Alga Cuántica":          {"cost": 7,  "color": PURPLE,  "icon": "🌀"},
    "Wasabi de Plasma":       {"cost": 10, "color": YELLOW,  "icon": "⚡"},
    "Chip de Sabor Umami":    {"cost": 9,  "color": RED,     "icon": "💾"},
    "Tempura Nano":           {"cost": 6,  "color": ORANGE,  "icon": "🍤"},
    "Caviar de Datos":        {"cost": 12, "color": "#00bfff", "icon": "🧬"},
}
ING_NAMES = list(INGREDIENTS.keys())

RIVALS = ["Noodle-Corp", "Synth-Burger", "Ramen-Bot 3000", "Kraken Sushi Inc."]
HACK_ENERGY_COST = 25

KEY_POOL = list("ASDFJKLQWEIOZXCV")


class Customer:
    _next_id = 1

    def __init__(self):
        self.id = Customer._next_id
        Customer._next_id += 1
        n = random.randint(2, 3)
        self.order = random.sample(ING_NAMES, n)
        self.max_patience = random.uniform(22, 34)  # segundos "de vida"
        self.patience = 100.0
        self.reward = round(14 + 6 * len(self.order))
        self.name = f"Cliente-{self.id:03d}"

    def tick(self, dt):
        self.patience -= (100.0 / self.max_patience) * dt
        return self.patience <= 0


class GameState:
    def __init__(self):
        self.lock = threading.RLock()
        self.running = True

        self.credits = 120
        self.reputation = 0

        self.max_energy = 100.0
        self.energy = 100.0
        self.energy_regen = 3.0       # por segundo
        self.ing_discount = 0          # reduce costo de ingredientes

        self.battery_level = 0
        self.processor_level = 0

        self.customers = []            # list[Customer]
        self.max_customers = 4
        self.selected_customer_id = None
        self.current_dish = []         # list[str] nombres de ingredientes

        self.rival_status = {r: 0.0 for r in RIVALS}   # tiempo (epoch) hasta el cual está "bloqueado"
        self.hack_boost_until = 0.0    # boost de spawn de clientes

        self.log_msgs = []             # mensajes recientes para el status bar

    def log(self, msg):
        self.log_msgs.append(msg)
        self.log_msgs = self.log_msgs[-4:]

    def spawn_multiplier(self):
        return 1.6 if time.time() < self.hack_boost_until else 1.0


def thread_spawn_customers(gs: GameState):
    while gs.running:
        base_wait = random.uniform(4.5, 8.5)
        wait = base_wait / gs.spawn_multiplier()
        time.sleep(min(wait, 1.0))  # dormir en trozos cortos para poder salir rápido si running=False
        remaining = wait - min(wait, 1.0)
        while remaining > 0 and gs.running:
            step = min(remaining, 1.0)
            time.sleep(step)
            remaining -= step
        if not gs.running:
            break
        with gs.lock:
            if len(gs.customers) < gs.max_customers:
                gs.customers.append(Customer())


def thread_patience(gs: GameState):
    last = time.time()
    while gs.running:
        time.sleep(0.15)
        now = time.time()
        dt = now - last
        last = now
        with gs.lock:
            still = []
            for c in gs.customers:
                dead = c.tick(dt)
                if dead:
                    gs.reputation -= 1
                    gs.log(f"😡 {c.name} se fue enojado (paciencia agotada)")
                    if gs.selected_customer_id == c.id:
                        gs.selected_customer_id = None
                else:
                    still.append(c)
            gs.customers = still


def thread_energy_regen(gs: GameState):
    while gs.running:
        time.sleep(1.0)
        with gs.lock:
            gs.energy = min(gs.max_energy, gs.energy + gs.energy_regen)


def neon_button(parent, text, command, fg=CYAN, bg=PANEL2, width=None, font=FONT_B):
    b = tk.Button(
        parent, text=text, command=command, fg=fg, bg=bg,
        activebackground=fg, activeforeground=BG,
        relief="flat", bd=0, font=font, cursor="hand2",
        highlightthickness=1, highlightbackground=fg, highlightcolor=fg,
        padx=10, pady=6,
    )
    if width:
        b.config(width=width)
    return b


class Bar(tk.Canvas):

    def __init__(self, parent, width=160, height=14, color=CYAN, **kw):
        super().__init__(parent, width=width, height=height, bg=PANEL,
                          highlightthickness=1, highlightbackground=GREY, **kw)
        self.w = width
        self.h = height
        self.color = color
        self.set(1.0)

    def set(self, frac, color=None):
        frac = max(0.0, min(1.0, frac))
        c = color or self.color
        self.delete("all")
        self.create_rectangle(0, 0, self.w, self.h, fill=PANEL, outline="")
        self.create_rectangle(0, 0, self.w * frac, self.h, fill=c, outline="")


class MastermindGame(tk.Toplevel):
    COLORS = [MAGENTA, CYAN, GREEN, YELLOW, ORANGE, "#00bfff"]

    def __init__(self, master, rival, on_result):
        super().__init__(master)
        self.title(f"HACKEO :: {rival} :: Descifrar código")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.rival = rival
        self.on_result = on_result
        self.secret = [random.randint(0, len(self.COLORS) - 1) for _ in range(4)]
        self.guess = []
        self.attempts_left = 8
        self.time_left = 45
        self.finished = False

        tk.Label(self, text=f"⚠ INTRUSIÓN :: {rival}", fg=RED, bg=BG, font=FONT_L).pack(pady=(14, 2))
        tk.Label(self, text="Descifra la secuencia de 4 códigos. Bulls = color y posición correctos. Cows = color correcto, posición incorrecta.",
                 fg=WHITE, bg=BG, font=FONT_S, wraplength=380, justify="center").pack(pady=(0, 8))

        self.timer_lbl = tk.Label(self, text="", fg=YELLOW, bg=BG, font=FONT_B)
        self.timer_lbl.pack()
        self.attempts_lbl = tk.Label(self, text="", fg=CYAN, bg=BG, font=FONT_S)
        self.attempts_lbl.pack(pady=(0, 8))

        self.guess_frame = tk.Frame(self, bg=BG)
        self.guess_frame.pack(pady=4)
        self.guess_slots = []
        for i in range(4):
            c = tk.Canvas(self.guess_frame, width=36, height=36, bg=PANEL, highlightthickness=2,
                           highlightbackground=GREY)
            c.grid(row=0, column=i, padx=4)
            self.guess_slots.append(c)

        pal = tk.Frame(self, bg=BG)
        pal.pack(pady=8)
        for i, col in enumerate(self.COLORS):
            btn = tk.Button(pal, bg=col, width=3, height=1, relief="flat", cursor="hand2",
                             command=lambda i=i: self.add_color(i))
            btn.grid(row=0, column=i, padx=3)

        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(pady=6)
        neon_button(ctrl, "⌫ Borrar", self.undo, fg=GREY).grid(row=0, column=0, padx=4)
        neon_button(ctrl, "✔ Probar", self.submit, fg=GREEN).grid(row=0, column=1, padx=4)

        self.history = tk.Frame(self, bg=BG)
        self.history.pack(pady=8, fill="x", padx=14)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()
        self._tick_timer()

    def add_color(self, i):
        if self.finished or len(self.guess) >= 4:
            return
        self.guess.append(i)
        slot = self.guess_slots[len(self.guess) - 1]
        slot.configure(bg=self.COLORS[i])

    def undo(self):
        if self.finished or not self.guess:
            return
        self.guess.pop()
        slot = self.guess_slots[len(self.guess)]
        slot.configure(bg=PANEL)

    def submit(self):
        if self.finished or len(self.guess) < 4:
            return
        bulls = sum(1 for a, b in zip(self.guess, self.secret) if a == b)
        cows = sum(min(self.guess.count(c), self.secret.count(c)) for c in set(self.guess)) - bulls
        row = tk.Frame(self.history, bg=BG)
        row.pack(anchor="w", pady=1)
        for i in self.guess:
            tk.Canvas(row, width=16, height=16, bg=self.COLORS[i], highlightthickness=0).pack(side="left", padx=1)
        tk.Label(row, text=f"   Bulls:{bulls}  Cows:{cows}", fg=WHITE, bg=BG, font=FONT_S).pack(side="left")

        self.attempts_left -= 1
        if bulls == 4:
            self.finish(True)
            return
        if self.attempts_left <= 0:
            self.finish(False)
            return
        self.guess = []
        for s in self.guess_slots:
            s.configure(bg=PANEL)
        self.attempts_lbl.config(text=f"Intentos restantes: {self.attempts_left}")

    def _tick_timer(self):
        if self.finished:
            return
        self.timer_lbl.config(text=f"⏱ {self.time_left}s", fg=(RED if self.time_left <= 10 else YELLOW))
        self.attempts_lbl.config(text=f"Intentos restantes: {self.attempts_left}")
        if self.time_left <= 0:
            self.finish(False)
            return
        self.time_left -= 1
        self.after(1000, self._tick_timer)

    def finish(self, success):
        if self.finished:
            return
        self.finished = True
        self.on_result(self.rival, success)
        self.after(300, self.destroy)

    def on_close(self):
        self.finish(False)


# ------------------------------------------------------------------
# MINIJUEGO B: SECUENCIA RÁPIDA DE TECLAS
# ------------------------------------------------------------------
class ReflexGame(tk.Toplevel):
    def __init__(self, master, rival, on_result):
        super().__init__(master)
        self.title(f"HACKEO :: {rival} :: Secuencia rápida")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.rival = rival
        self.on_result = on_result
        length = random.randint(6, 9)
        self.sequence = [random.choice(KEY_POOL) for _ in range(length)]
        self.index = 0
        self.finished = False
        self.time_left = round(3.0 + 0.55 * length, 1)

        tk.Label(self, text=f"⚠ INTRUSIÓN :: {rival}", fg=RED, bg=BG, font=FONT_L).pack(pady=(14, 2))
        tk.Label(self, text="¡Escribe la secuencia EXACTA antes de que se acabe el tiempo!",
                 fg=WHITE, bg=BG, font=FONT_S).pack(pady=(0, 10))

        self.timer_lbl = tk.Label(self, text="", fg=YELLOW, bg=BG, font=FONT_B)
        self.timer_lbl.pack()

        self.seq_frame = tk.Frame(self, bg=BG)
        self.seq_frame.pack(pady=14)
        self.key_lbls = []
        for k in self.sequence:
            lbl = tk.Label(self.seq_frame, text=k, fg=GREY, bg=PANEL, font=("Consolas", 18, "bold"),
                            width=2, relief="flat", highlightthickness=2, highlightbackground=GREY)
            lbl.pack(side="left", padx=3)
            self.key_lbls.append(lbl)

        self.status_lbl = tk.Label(self, text="Presiona la primera tecla para comenzar...", fg=CYAN, bg=BG, font=FONT_S)
        self.status_lbl.pack(pady=6)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<KeyPress>", self.on_key)
        self.grab_set()
        self.focus_force()
        self._deadline = None
        self._tick_started = False
        self._tick_timer_idle()

    def _tick_timer_idle(self):
        self.timer_lbl.config(text=f"⏱ {self.time_left:.1f}s (empieza al presionar)", fg=YELLOW)

    def on_key(self, event):
        if self.finished:
            return
        if not self._tick_started:
            self._tick_started = True
            self._deadline = time.time() + self.time_left
            self._tick_timer()

        ch = event.char.upper() if event.char else ""
        expected = self.sequence[self.index]
        if ch == expected:
            self.key_lbls[self.index].config(fg=BG, bg=GREEN, highlightbackground=GREEN)
            self.index += 1
            self.status_lbl.config(text="Correcto...", fg=GREEN)
            if self.index >= len(self.sequence):
                self.finish(True)
        else:
            for lbl in self.key_lbls:
                lbl.config(fg=BG, bg=RED, highlightbackground=RED)
            self.status_lbl.config(text=f"Tecla incorrecta: {ch or '?'}", fg=RED)
            self.finish(False)

    def _tick_timer(self):
        if self.finished:
            return
        remaining = self._deadline - time.time()
        if remaining <= 0:
            self.finish(False)
            return
        self.timer_lbl.config(text=f"⏱ {remaining:.1f}s", fg=(RED if remaining <= 1.5 else YELLOW))
        self.after(80, self._tick_timer)

    def finish(self, success):
        if self.finished:
            return
        self.finished = True
        self.on_result(self.rival, success)
        self.after(350, self.destroy)

    def on_close(self):
        self.finish(False)


# ------------------------------------------------------------------
# APLICACIÓN PRINCIPAL
# ------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🐙 CYBER-TAKOYAKI :: Food Truck Hacker 🤖 — Neo-Tokio 2088")
        self.configure(bg=BG)
        self.geometry("1150x720")
        self.minsize(1000, 650)

        self.gs = GameState()

        self._build_style()
        self._build_topbar()
        self._build_tabs()
        self._build_kitchen_frame()
        self._build_hack_frame()
        self._build_upgrades_frame()
        self.show_frame("kitchen")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Hilos de fondo (clientes, paciencia, energía)
        threading.Thread(target=thread_spawn_customers, args=(self.gs,), daemon=True).start()
        threading.Thread(target=thread_patience, args=(self.gs,), daemon=True).start()
        threading.Thread(target=thread_energy_regen, args=(self.gs,), daemon=True).start()

        try_start_music()

        self.after(150, self.refresh_ui)

    # ---------------- estilo ----------------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

    # ---------------- barra superior ----------------
    def _build_topbar(self):
        top = tk.Frame(self, bg=PANEL, height=70)
        top.pack(side="top", fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="CYBER-TAKOYAKI", fg=MAGENTA, bg=PANEL, font=FONT_T).pack(side="left", padx=18)

        stats = tk.Frame(top, bg=PANEL)
        stats.pack(side="left", padx=20)

        self.credits_var = tk.StringVar()
        self.rep_var = tk.StringVar()
        tk.Label(stats, textvariable=self.credits_var, fg=YELLOW, bg=PANEL, font=FONT_L).pack(side="left", padx=12)
        tk.Label(stats, textvariable=self.rep_var, fg=CYAN, bg=PANEL, font=FONT).pack(side="left", padx=12)

        energy_box = tk.Frame(top, bg=PANEL)
        energy_box.pack(side="left", padx=12)
        tk.Label(energy_box, text="⚡ ENERGÍA", fg=GREEN, bg=PANEL, font=FONT_S).pack(anchor="w")
        self.energy_bar = Bar(energy_box, width=180, height=16, color=GREEN)
        self.energy_bar.pack()

        self.log_var = tk.StringVar(value="Bienvenido a Neo-Tokio, cocinero-hacker.")
        tk.Label(top, textvariable=self.log_var, fg=WHITE, bg=PANEL, font=FONT_S,
                 wraplength=320, justify="left").pack(side="right", padx=18)

    # ---------------- tabs ----------------
    def _build_tabs(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(side="top", fill="x", pady=6)
        self.tab_buttons = {}
        for key, label, color in [
            ("kitchen", "🍳 COCINA HOLOGRÁFICA", CYAN),
            ("hack", "💀 MENÚ DE HACKEO", MAGENTA),
            ("upgrades", "⚙️ MEJORAS", PURPLE),
        ]:
            b = neon_button(bar, label, lambda k=key: self.show_frame(k), fg=color, width=24)
            b.pack(side="left", padx=8)
            self.tab_buttons[key] = b

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(side="top", fill="both", expand=True)
        self.frames = {}

    def show_frame(self, key):
        for f in self.frames.values():
            f.pack_forget()
        self.frames[key].pack(fill="both", expand=True)
        for k, b in self.tab_buttons.items():
            b.config(relief=("sunken" if k == key else "flat"))

    # ---------------- COCINA ----------------
    def _build_kitchen_frame(self):
        f = tk.Frame(self.container, bg=BG)
        self.frames["kitchen"] = f

        left = tk.Frame(f, bg=PANEL)
        left.pack(side="left", fill="y", padx=(14, 7), pady=10)
        tk.Label(left, text="INGREDIENTES", fg=CYAN, bg=PANEL, font=FONT_L).pack(pady=(10, 6), padx=14)
        for name, data in INGREDIENTS.items():
            row = tk.Frame(left, bg=PANEL)
            row.pack(fill="x", padx=12, pady=3)
            btn = tk.Button(
                row, text=f"{data['icon']} {name}\n({max(1, data['cost']-self.gs.ing_discount)} energía)",
                bg=PANEL2, fg=data["color"], activebackground=data["color"], activeforeground=BG,
                relief="flat", font=FONT_S, justify="left", anchor="w", width=28, cursor="hand2",
                highlightthickness=1, highlightbackground=data["color"],
                command=lambda n=name: self.add_ingredient(n),
            )
            btn.pack(fill="x")

        mid = tk.Frame(f, bg=PANEL)
        mid.pack(side="left", fill="both", expand=True, padx=7, pady=10)
        tk.Label(mid, text="PLATO ACTUAL", fg=YELLOW, bg=PANEL, font=FONT_L).pack(pady=(10, 6))
        self.dish_list_var = tk.StringVar(value="(vacío)")
        tk.Label(mid, textvariable=self.dish_list_var, fg=WHITE, bg=PANEL, font=FONT,
                 wraplength=280, justify="left").pack(pady=6, padx=10)
        btnrow = tk.Frame(mid, bg=PANEL)
        btnrow.pack(pady=10)
        neon_button(btnrow, "🗑 Limpiar plato", self.clear_dish, fg=RED).pack(side="left", padx=5)
        neon_button(btnrow, "🍱 Servir a cliente seleccionado", self.serve_dish, fg=GREEN).pack(side="left", padx=5)

        right = tk.Frame(f, bg=PANEL)
        right.pack(side="left", fill="both", expand=True, padx=(7, 14), pady=10)
        tk.Label(right, text="CLIENTES EN COLA", fg=MAGENTA, bg=PANEL, font=FONT_L).pack(pady=(10, 6))
        self.customers_frame = tk.Frame(right, bg=PANEL)
        self.customers_frame.pack(fill="both", expand=True, padx=8, pady=4)

    def add_ingredient(self, name):
        with self.gs.lock:
            cost = max(1, INGREDIENTS[name]["cost"] - self.gs.ing_discount)
            if self.gs.energy < cost:
                self.gs.log("⚠ No hay energía suficiente para cocinar.")
                return
            self.gs.energy -= cost
            self.gs.current_dish.append(name)

    def clear_dish(self):
        with self.gs.lock:
            self.gs.current_dish = []

    def serve_dish(self):
        with self.gs.lock:
            cid = self.gs.selected_customer_id
            if cid is None:
                self.gs.log("⚠ Selecciona un cliente antes de servir.")
                return
            customer = next((c for c in self.gs.customers if c.id == cid), None)
            if customer is None:
                self.gs.log("⚠ Ese cliente ya no está.")
                self.gs.selected_customer_id = None
                return
            if sorted(self.gs.current_dish) != sorted(customer.order):
                self.gs.log(f"❌ El plato no coincide con lo que pidió {customer.name}.")
                return
            reward = round(customer.reward * (0.5 + customer.patience / 100.0))
            self.gs.credits += reward
            self.gs.reputation += 1
            self.gs.customers = [c for c in self.gs.customers if c.id != cid]
            self.gs.selected_customer_id = None
            self.gs.current_dish = []
            self.gs.log(f"✅ {customer.name} atendido. +{reward} créditos.")

    def select_customer(self, cid):
        with self.gs.lock:
            self.gs.selected_customer_id = cid

    # ---------------- HACKEO ----------------
    def _build_hack_frame(self):
        f = tk.Frame(self.container, bg=BG)
        self.frames["hack"] = f
        tk.Label(f, text="TERMINAL DE CIBER-ATAQUE", fg=MAGENTA, bg=BG, font=FONT_T).pack(pady=16)
        tk.Label(f, text=f"Cada intrusión consume {HACK_ENERGY_COST} de energía. Éxito: +50% de clientes por 60s "
                          f"y bloqueas al rival. Fallo: multa de la ciber-policía.",
                 fg=WHITE, bg=BG, font=FONT_S, wraplength=700, justify="center").pack(pady=(0, 16))

        self.rival_rows_frame = tk.Frame(f, bg=BG)
        self.rival_rows_frame.pack(fill="x", padx=40)
        self.rival_widgets = {}
        for rival in RIVALS:
            row = tk.Frame(self.rival_rows_frame, bg=PANEL)
            row.pack(fill="x", pady=6)
            name_lbl = tk.Label(row, text=rival, fg=CYAN, bg=PANEL, font=FONT_B, width=20, anchor="w")
            name_lbl.pack(side="left", padx=14, pady=10)
            status_lbl = tk.Label(row, text="", fg=GREEN, bg=PANEL, font=FONT_S, width=22, anchor="w")
            status_lbl.pack(side="left")
            b1 = neon_button(row, "🔓 Descifrar código", lambda r=rival: self.start_hack(r, "code"), fg=YELLOW)
            b1.pack(side="right", padx=8, pady=8)
            b2 = neon_button(row, "⌨ Secuencia rápida", lambda r=rival: self.start_hack(r, "reflex"), fg=ORANGE)
            b2.pack(side="right", padx=8, pady=8)
            self.rival_widgets[rival] = {"status": status_lbl, "b1": b1, "b2": b2}

    def start_hack(self, rival, mode):
        with self.gs.lock:
            if time.time() < self.gs.rival_status.get(rival, 0):
                self.gs.log(f"⏳ {rival} ya está bloqueado, espera a que se recupere.")
                return
            if self.gs.energy < HACK_ENERGY_COST:
                self.gs.log("⚠ No hay energía suficiente para hackear.")
                return
            self.gs.energy -= HACK_ENERGY_COST

        if mode == "code":
            MastermindGame(self, rival, self.on_hack_result)
        else:
            ReflexGame(self, rival, self.on_hack_result)

    def on_hack_result(self, rival, success):
        with self.gs.lock:
            if success:
                self.gs.credits += 40
                self.gs.hack_boost_until = time.time() + 60
                self.gs.rival_status[rival] = time.time() + 60
                self.gs.log(f"💥 ¡Hackeo exitoso a {rival}! +40 créditos, +50% clientes 60s.")
            else:
                fine = 20
                self.gs.credits = max(0, self.gs.credits - fine)
                self.gs.log(f"🚨 Ciber-policía te multó por intentar hackear {rival}: -{fine} créditos.")

    # ---------------- MEJORAS ----------------
    def _build_upgrades_frame(self):
        f = tk.Frame(self.container, bg=BG)
        self.frames["upgrades"] = f
        tk.Label(f, text="TALLER DE MEJORAS", fg=PURPLE, bg=BG, font=FONT_T).pack(pady=16)

        box = tk.Frame(f, bg=PANEL)
        box.pack(pady=10, padx=40, fill="x")

        row1 = tk.Frame(box, bg=PANEL)
        row1.pack(fill="x", pady=14, padx=20)
        tk.Label(row1, text="🔋 Batería mejorada", fg=GREEN, bg=PANEL, font=FONT_B, width=26, anchor="w").pack(side="left")
        self.battery_info = tk.Label(row1, text="", fg=WHITE, bg=PANEL, font=FONT_S, width=30, anchor="w")
        self.battery_info.pack(side="left")
        self.battery_btn = neon_button(row1, "Comprar", self.buy_battery, fg=GREEN)
        self.battery_btn.pack(side="right")

        row2 = tk.Frame(box, bg=PANEL)
        row2.pack(fill="x", pady=14, padx=20)
        tk.Label(row2, text="🧠 Procesador de cocina", fg=CYAN, bg=PANEL, font=FONT_B, width=26, anchor="w").pack(side="left")
        self.processor_info = tk.Label(row2, text="", fg=WHITE, bg=PANEL, font=FONT_S, width=30, anchor="w")
        self.processor_info.pack(side="left")
        self.processor_btn = neon_button(row2, "Comprar", self.buy_processor, fg=CYAN)
        self.processor_btn.pack(side="right")

    def battery_cost(self):
        return 50 + 30 * self.gs.battery_level

    def processor_cost(self):
        return 60 + 35 * self.gs.processor_level

    def buy_battery(self):
        with self.gs.lock:
            cost = self.battery_cost()
            if self.gs.credits < cost:
                self.gs.log("⚠ Créditos insuficientes para la batería.")
                return
            self.gs.credits -= cost
            self.gs.battery_level += 1
            self.gs.max_energy += 20
            self.gs.energy_regen += 0.5
            self.gs.log("🔋 ¡Batería mejorada instalada!")

    def buy_processor(self):
        with self.gs.lock:
            cost = self.processor_cost()
            if self.gs.credits < cost:
                self.gs.log("⚠ Créditos insuficientes para el procesador.")
                return
            if self.gs.ing_discount >= 5:
                self.gs.log("🧠 Procesador ya al máximo nivel útil.")
                return
            self.gs.credits -= cost
            self.gs.processor_level += 1
            self.gs.ing_discount += 1
            self.gs.log("🧠 ¡Procesador de cocina mejorado!")

    # ---------------- REFRESCO DE UI (hilo principal) ----------------
    def refresh_ui(self):
        with self.gs.lock:
            credits = self.gs.credits
            rep = self.gs.reputation
            energy = self.gs.energy
            max_energy = self.gs.max_energy
            dish = list(self.gs.current_dish)
            customers = list(self.gs.customers)
            selected = self.gs.selected_customer_id
            log_msg = self.gs.log_msgs[-1] if self.gs.log_msgs else ""
            rival_status = dict(self.gs.rival_status)
            battery_cost = self.battery_cost()
            processor_cost = self.processor_cost()
            battery_level = self.gs.battery_level
            processor_level = self.gs.processor_level
            ing_discount = self.gs.ing_discount

        self.credits_var.set(f"💰 {credits} créditos")
        self.rep_var.set(f"⭐ Reputación: {rep}")
        self.energy_bar.set(energy / max_energy if max_energy else 0,
                             color=(GREEN if energy > max_energy * 0.3 else RED))
        self.log_var.set(log_msg)

        self.dish_list_var.set(
            "  +  ".join(f"{INGREDIENTS[n]['icon']} {n}" for n in dish) if dish else "(vacío) — elige ingredientes"
        )

        # refrescar lista de clientes
        for w in self.customers_frame.winfo_children():
            w.destroy()
        if not customers:
            tk.Label(self.customers_frame, text="No hay clientes ahora mismo...\nespera a que lleguen.",
                     fg=GREY, bg=PANEL, font=FONT_S).pack(pady=20)
        for c in customers:
            sel = (c.id == selected)
            row = tk.Frame(self.customers_frame, bg=(PANEL2 if sel else PANEL),
                            highlightthickness=2, highlightbackground=(CYAN if sel else GREY))
            row.pack(fill="x", pady=4, padx=2)
            order_text = " + ".join(f"{INGREDIENTS[n]['icon']}{n.split()[0]}" for n in c.order)
            tk.Label(row, text=f"{c.name}", fg=YELLOW, bg=row["bg"], font=FONT_B, anchor="w").pack(
                fill="x", padx=8, pady=(6, 0))
            tk.Label(row, text=f"Pide: {order_text}", fg=WHITE, bg=row["bg"], font=FONT_S, anchor="w",
                     wraplength=260, justify="left").pack(fill="x", padx=8)
            bar = Bar(row, width=240, height=10,
                      color=(GREEN if c.patience > 50 else (YELLOW if c.patience > 20 else RED)))
            bar.set(c.patience / 100.0)
            bar.pack(padx=8, pady=(2, 8))
            row.bind("<Button-1>", lambda e, cid=c.id: self.select_customer(cid))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, cid=c.id: self.select_customer(cid))

        # refrescar estado de rivales
        now = time.time()
        for rival, w in self.rival_widgets.items():
            blocked_until = rival_status.get(rival, 0)
            if now < blocked_until:
                remaining = int(blocked_until - now)
                w["status"].config(text=f"🔒 Bloqueado ({remaining}s)", fg=RED)
                w["b1"].config(state="disabled")
                w["b2"].config(state="disabled")
            else:
                w["status"].config(text="🟢 Operativo", fg=GREEN)
                w["b1"].config(state="normal")
                w["b2"].config(state="normal")

        self.battery_info.config(text=f"Nivel {battery_level} · +20 energía máx · {battery_cost} créditos")
        self.processor_info.config(
            text=(f"Nivel {processor_level} · -{ing_discount} costo ingr. · {processor_cost} créditos"
                  if ing_discount < 5 else "MÁXIMO ALCANZADO"))

        if self.gs.running:
            self.after(150, self.refresh_ui)

    def on_close(self):
        self.gs.running = False
        if PYGAME_OK:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self.destroy()


# ------------------------------------------------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()