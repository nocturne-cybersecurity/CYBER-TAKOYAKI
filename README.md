readme_content = """# 🎮 CyberArcade: Neon Markets & CyberBites

¡Bienvenido a **CyberArcade**! Esta es una colección de dos mini-juegos únicos desarrollados en Python utilizando la librería **Pygame**. El proyecto combina la adrenalina de la simulación financiera de los mercados de valores de alta velocidad con una aventura distópica de un camión de comida callejera cyberpunk equipado con habilidades de hackeo.

---

## 🚀 Los Mini-Juegos

### 📈 1. Crypto & Stock Tycoon (Simulador de Inversiones)
Conviértete en un tiburón financiero en una economía volátil. Analiza gráficos, sigue las tendencias y toma decisiones rápidas antes de que la burbuja explote.
* **Mecánicas clave:**
  * Simulación de mercado en tiempo real con fluctuaciones de precios dinámicas.
  * Interfaz visual de trading con gráficos de líneas o velas.
  * Eventos de noticias aleatorios (tweets de magnates, crisis corporativas, regulaciones) que afectan el valor de las acciones.
  * Sistema de gestión de billetera y portafolio de activos.

### 🚚 2. NeonBytes: Hacker Food Truck
Dirige un negocio de comida rápida en una metrópolis cyberpunk. Pero no todo es cocinar; para sobrevivir a las corporaciones, tendrás que usar tus habilidades de *netrunner* para sabotear rivales y conseguir ingredientes exóticos.
* **Mecánicas clave:**
  * Gestión de pedidos rápidos: prepara platos sintéticos y bebidas de neón para clientes exigentes.
  * Habilidades de Hackeo: Activa mini-juegos de hackeo electrónico en tiempo real para apagar drones de inspección, robar recetas de bases de datos corporativas o congelar el reloj.
  * Árbol de mejoras: Invierte tus ganancias en mejorar los servidores de cocina o tus implantes cibernéticos para hackeos más rápidos.

---

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:
* [Python 3.8 o superior](https://www.python.org/downloads/)
* El administrador de paquetes `pip` (suele incluirse automáticamente con Python).

---

## 🔧 Instalación y Configuración

Sigue estos pasos paso a paso desde tu terminal para clonar el proyecto y preparar el entorno de desarrollo:

### 1. Clonar el repositorio (Opcional)
Si tienes el proyecto en un repositorio de Git, clónalo y navega a la carpeta:
2. Crear el Entorno Virtual
Para mantener las dependencias de este proyecto aisladas de tu sistema global, crea un entorno virtual llamado .venv:

Bash
python -m venv .venv
3. Activar el Entorno Virtual
Dependiendo de tu sistema operativo, ejecuta el comando correspondiente:

En Windows (PowerShell):

PowerShell
.venv\\Scripts\\Activate.ps1
En Windows (CMD):

DOS
.venv\\Scripts\\activate.bat
En macOS / Linux:

Bash
source .venv/bin/activate
Verificarás que está activo porque aparecerá (.venv) al inicio de tu línea de comandos.

4. Instalar las Dependencias
Con el entorno virtual activado, instala la librería Pygame:

Bash
pip install pygame
