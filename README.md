# 🏹 MineFight: Keyboard Defender

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pygame](https://img.shields.io/badge/pygame-black?style=for-the-badge&logo=python&logoColor=white)

**MineFight** es un juego 2D de supervivencia y físicas desarrollado en Python utilizando la librería Pygame. En este juego, encarnas a un arquero que debe defender su posición dentro de una cueva contra infinitas oleadas de enemigos icónicos de Minecraft (Zombies y Creepers), con un sistema de progresión de experiencia y mejoras.

## Características Principales

* **Sistema de Oleadas y Jefes:** La dificultad escala progresivamente. A partir de ciertas oleadas, aumenta la velocidad, la cantidad de enemigos y la probabilidad de aparición de Jefes con mayor vida y tamaño.
* **Físicas de Proyectiles y Experiencia:** Las flechas viajan hacia el enemigo, y al morir, los mobs liberan orbes de experiencia con físicas de explosión, gravedad y rebote, viajando hacia la pantalla del jugador.
* **Sistema de Economía y Nivel:** Recolecta XP y utiliza la tienda in-game para mejorar tu arco. Cada mejora reduce el tiempo de tensado, cambia el diseño visual del arma y aumenta el daño.
* **Efectos de Sonido y Ambientación:** Audio inmersivo 3D simulado (el volumen de los monstruos y la experiencia depende de su distancia a la pantalla).
* **Dificultad Dinámica:** Modos de juego Normal y Difícil ajustables desde la tienda.

## Controles del Juego

La interfaz está diseñada para requerir habilidad con el teclado (Keyboard Defender):

* **Ctrl + V:** Tensar el arco y disparar al objetivo más cercano.
* **Ctrl + C:** Recargar el carcaj de flechas (solo posible cuando quedan pocas).
* **Shift:** Abrir / Cerrar la tienda de mejoras.
* **F11:** Alternar entre Modo Ventana y Pantalla Completa.
* **Ctrl + Z:** Reintentar tras un Game Over.

## Instalación y Ejecución

### Para Jugadores (Windows .exe)
Si solo quieres jugar, no necesitas instalar Python:
1. Ve a la sección de **Releases** de este repositorio.
2. Descarga el archivo `.zip` con la última versión.
3. Descomprime la carpeta, asegúrate de que las carpetas `textures/` y `sounds/` estén junto al archivo `MineFight.exe`.
4. Ejecuta `MineFight.exe`
