#MAIN

import tkinter as tk
import json
import random
from acciones import *

#================= VENTANA =================

# Colores modernos
COLOR_BG = "#1e1e2e"
COLOR_FG = "#cdd6f4"
COLOR_ACCENT = "#89b4fa"
COLOR_GREEN = "#a6e3a1"
COLOR_RED = "#f38ba8"
COLOR_YELLOW = "#f9e2af"
COLOR_CARD = "#313244"

ventana = tk.Tk()
ventana.title("Investor The Troll Game")
ventana.geometry("900x700")
ventana.configure(bg=COLOR_BG)

#Centrar ventana en la pantalla
ancho_ventana = 900
alto_ventana = 700
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()
x = (ancho_pantalla // 2) - (ancho_ventana // 2)
y = (alto_pantalla // 2) - (alto_ventana // 2)
ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

# Título moderno
canvas_titulo = tk.Canvas(ventana, width=500, height=60, highlightthickness=0, bg=COLOR_BG)
canvas_titulo.pack(pady=15)
texto_juego = "Investor The Troll Game"
fuente_juego = ("Segoe UI", 24, "bold")
canvas_titulo.create_text(250, 30, text=texto_juego, font=fuente_juego, fill=COLOR_ACCENT)

etiqueta_saldo = tk.Label(ventana, text="Saldo: $100000 | Acciones: 0", 
                          font=("Segoe UI", 16, "bold"), bg=COLOR_CARD, fg=COLOR_GREEN,
                          padx=20, pady=10, relief="flat")
etiqueta_saldo.pack(side="top", pady=10)

#=============== FRAMES ================
frame_superior = tk.Frame(ventana, bg=COLOR_BG)
frame_superior.pack(anchor="center", padx=10, pady=10)

frame_entradas = tk.Frame(ventana, bg=COLOR_BG)
frame_entradas.pack(fill="x", padx=50, pady=15)

entrada = tk.Entry(frame_entradas, font=("Segoe UI", 14), bg=COLOR_CARD, fg=COLOR_FG,
                   relief="flat", insertbackground=COLOR_ACCENT)
entrada.pack(side="left", padx=8)

entrada2 = tk.Entry(frame_entradas, font=("Segoe UI", 14), bg=COLOR_CARD, fg=COLOR_FG,
                    relief="flat", insertbackground=COLOR_ACCENT)
entrada2.pack(side="right", padx=8)

aviso = tk.Label(frame_entradas, text="", font=("Segoe UI", 11, "bold"), bg=COLOR_BG)
aviso.pack(expand=True)

frame_botones = tk.Frame(ventana, bg=COLOR_BG)
frame_botones.pack(fill="x", padx=50, pady=10)

#================= ENTRADAS =================

def obtener_texto():
    texto_ingresado = entrada.get()

    if not texto_ingresado.isdigit():
        aviso.config(text="⚠️ Solo se permiten números")
        return
    
    cantidad = int(texto_ingresado)
    if cantidad <= 0:
        aviso.config(text="⚠️ Ingresa un número positivo")
        return
    
    aviso.config(text="")
    exito, mensaje = comprar(cantidad)
    aviso.config(text=mensaje, fg=COLOR_GREEN if exito else COLOR_RED, bg=COLOR_BG)
    cambiar_saldo()
    
    # Mostrar en caja 1
    caja_texto1.config(state="normal")
    caja_texto1.insert("end", f"\n{mensaje}\n")
    caja_texto1.see("end")
    caja_texto1.config(state="disabled")
    
    # Verificar victoria
    if verificar_victoria():
        aviso.config(text="🎉 ¡GANASTE! Llegaste a $1,000,000", fg="gold")
        caja_texto1.config(state="normal")
        caja_texto1.insert("end", "\n🎉 ¡VICTORIA! 🎉\n", "gold")
        caja_texto1.tag_config("gold", foreground="gold", font=("Arial", 12, "bold"))
        caja_texto1.see("end")
        caja_texto1.config(state="disabled")


def obtener_texto2():
    texto_ingresado2 = entrada2.get()

    if not texto_ingresado2.isdigit():
        aviso.config(text="⚠️ Solo se permiten números")
        return
    
    cantidad = int(texto_ingresado2)
    if cantidad <= 0:
        aviso.config(text="⚠️ Ingresa un número positivo")
        return
    
    aviso.config(text="")
    exito, mensaje = vender(cantidad)
    aviso.config(text=mensaje, fg=COLOR_GREEN if exito else COLOR_RED, bg=COLOR_BG)
    cambiar_saldo()
    
    # Mostrar en caja 1
    caja_texto1.config(state="normal")
    caja_texto1.insert("end", f"\n{mensaje}\n")
    caja_texto1.see("end")
    caja_texto1.config(state="disabled")
    
    # Verificar victoria
    if verificar_victoria():
        aviso.config(text="🎉 ¡GANASTE! Llegaste a $1,000,000", fg="gold")
        caja_texto1.config(state="normal")
        caja_texto1.insert("end", "\n🎉 ¡VICTORIA! 🎉\n", "gold")
        caja_texto1.tag_config("gold", foreground="gold", font=("Arial", 12, "bold"))
        caja_texto1.see("end")
        caja_texto1.config(state="disabled")

# Agregar botones después de definir las funciones
boton = tk.Button(frame_botones, text="💰 COMPRAR", command=obtener_texto,
                  font=("Segoe UI", 12, "bold"), bg=COLOR_GREEN, fg="#1e1e2e",
                  relief="flat", padx=20, pady=10, cursor="hand2")
boton.pack(side="left", padx=10)

boton2 = tk.Button(frame_botones, text="💸 VENDER", command=obtener_texto2,
                   font=("Segoe UI", 12, "bold"), bg=COLOR_RED, fg="#1e1e2e",
                   relief="flat", padx=20, pady=10, cursor="hand2")
boton2.pack(side="right", padx=10)


#=============== TEXTOS =================

caja_texto1 = tk.Text(frame_superior, height=8, width=55, font=("Segoe UI", 11),
                      bg=COLOR_CARD, fg=COLOR_FG, relief="flat", padx=10, pady=10)
caja_texto1.grid(row=0, column=0, padx=8, pady=8)

caja_texto2 = tk.Text(ventana, height=15, width=120, font=("Segoe UI", 11),
                      bg=COLOR_CARD, fg=COLOR_FG, relief="flat", padx=10, pady=10)
caja_texto2.pack(side="bottom", padx=15, pady=15)

caja_texto3 = tk.Text(frame_superior, height=8, width=55, font=("Segoe UI", 11),
                      bg=COLOR_CARD, fg=COLOR_FG, relief="flat", padx=10, pady=10)
caja_texto3.grid(row=0, column=1, padx=8, pady=8)

etiqueta_valor_accion = tk.Label(frame_superior, text=f"Valor acción: ${valor_accion()}", 
                                  font=("Segoe UI", 12, "bold"), bg=COLOR_BG, fg=COLOR_ACCENT)
etiqueta_valor_accion.grid(row=1, column=1, pady=5)

#Cargar eventos desde JSON
with open('eventos.json', 'r', encoding='utf-8') as archivo:
    datos_eventos = json.load(archivo)



#================ EVENTOS =================

etiqueta = tk.Label(ventana, text="📰 EVENTOS DEL MERCADO", font=("Segoe UI", 14, "bold"),
                    bg=COLOR_BG, fg=COLOR_ACCENT)
etiqueta.pack(side="bottom", pady=5)

def mostrar_evento():
    #Seleccionar evento aleatorio
    evento = random.choice(datos_eventos["eventos"])
    
    #Aplicar cambio al valor de la acción
    cambio_porcentaje = evento['cambio']
    valor_actual = valor_accion()
    nuevo_valor = valor_actual + (valor_actual * cambio_porcentaje // 100)
    if nuevo_valor < 1:
        nuevo_valor = 1
    actualizar_valor_accion(nuevo_valor)
    
    #Insertar evento en caja 2
    caja_texto2.insert("end", f"\n--- NOTICIA (ID {evento['id']}) ---\n")
    caja_texto2.insert("end", f"Título: {evento['titulo']}\n")
    caja_texto2.insert("end", f"Descripción: {evento['descripcion']}\n")
    caja_texto2.insert("end", f"Empresa: {evento['empresa']}\n")
    caja_texto2.insert("end", f"Tipo: {evento['tipo'].upper()}\n")
    caja_texto2.insert("end", f"Cambio: {evento['cambio']}%\n")
    caja_texto2.insert("end", f"Valor acción: ${valor_actual} -> ${nuevo_valor}\n")
    caja_texto2.insert("end", "-" * 50 + "\n")
    
    #Auto-scroll al final
    caja_texto2.see("end")
    
    # Actualizar display
    cambiar_saldo()
    etiqueta_valor_accion.config(text=f"Valor acción: ${valor_accion()}")
    
    #Programar siguiente evento (2-4 segundos para más rapidez)
    delay = random.randint(2000, 4000)
    ventana.after(delay, mostrar_evento)
#Iniciar el ciclo de eventos
ventana.after(1000, mostrar_evento)

# Variable global para valor de bolsa
valor_bolsa = 100

def actualizar_bolsa():
    global valor_bolsa
    valor_anterior = valor_bolsa
    
    # Si el valor está muy bajo, favorecer subidas agresivas para recuperarse
    if valor_bolsa == 1:
        cambio = valor_bolsa = 40
    elif valor_bolsa < 20:
        cambio = random.randint(-1, 8)  # Mayor probabilidad de subir
    elif valor_bolsa < 50:
        cambio = random.randint(-2, 6)
    elif valor_bolsa < 100:
        cambio = random.randint(-4, 6)
    else:
        cambio = random.randint(-5, 5)
    
    valor_bolsa += cambio
    if valor_bolsa <= 1:
        valor_bolsa = 10
    
    # Determinar color según si subió o bajó
    color = COLOR_GREEN if valor_bolsa > valor_anterior else COLOR_RED
    flecha = "📈" if valor_bolsa > valor_anterior else "📉"
    
    # Mostrar en caja 3 con color dinámico
    caja_texto3.config(state="normal")
    caja_texto3.delete("1.0", "end")
    caja_texto3.insert("1.0", f"{flecha} BOLSA: {valor_bolsa}", "dynamic")
    caja_texto3.tag_config("dynamic", foreground=color, font=("Segoe UI", 14, "bold"))
    caja_texto3.config(state="disabled")
    
    # Programar siguiente actualización (1-2 segundos para más rapidez)
    ventana.after(random.randint(1000, 2000), actualizar_bolsa)

# Iniciar ciclo de bolsa
ventana.after(2000, actualizar_bolsa)

#=============== SALDO ==================

def cambiar_saldo():
    etiqueta_saldo.config(text=f"Saldo: ${saldo()} | Acciones: {acciones()}")

#Mostrar saldo inicial
cambiar_saldo()



#=============== LABELS =================

try:
    ventana.mainloop()
except KeyboardInterrupt:
    print("Aplicación cerrada por el usuario.")
except Exception as e:
    print(f"Error: {e}")
finally:
    print("¿Te rindes o te quedaste sin saldo?")
