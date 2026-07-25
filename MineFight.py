import pygame
import sys
import os
import random
import math

pygame.init()

# --- INICIALIZACIÓN DE AUDIO ---
pygame.mixer.init(channels=32)

# --- 1. CONFIGURACIÓN BÁSICA ---
screen_width, screen_height = 1240, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("MineFight")
clock = pygame.time.Clock()

# --- 2. RUTAS COMPATIBLES CON EJECUTABLE (.EXE) ---
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEXTURES_DIR = os.path.join(BASE_DIR, "textures")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds") 
RUTA_FUENTE = os.path.join(TEXTURES_DIR, "Minecraft.ttf") 

try:
    icono_app = pygame.image.load(os.path.join(TEXTURES_DIR, "icon.png")).convert_alpha()
    pygame.display.set_icon(icono_app)
except Exception:
    pass

def cargar_animacion(carpeta, prefijo, cant_frames):
    frames = []
    for i in range(1, cant_frames + 1):
        nombre_archivo = f"{prefijo}{i}.png"
        ruta = os.path.join(TEXTURES_DIR, carpeta, nombre_archivo)
        try:
            img = pygame.image.load(ruta).convert_alpha()
            frames.append(img)
        except Exception as e:
            pass 
            
    if not frames:
        temp_img = pygame.Surface((400, 600), pygame.SRCALPHA)
        temp_img.fill((255, 0, 255)) 
        frames.append(temp_img)
        
    return frames

# --- 3. CARGA DE SONIDOS (80% VOLUMEN) ---
def load_sound_list(folder, prefix, count):
    sounds = []
    for i in range(1, count + 1):
        try:
            snd = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, folder, f"{prefix}{i}.ogg"))
            snd.set_volume(0.7) 
            sounds.append(snd)
        except Exception:
            pass
    return sounds

def load_single_sound(folder, filename):
    try:
        snd = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, folder, filename))
        snd.set_volume(0.7)
        return snd
    except Exception:
        return None

# --- DICCIONARIO DE SFX (CON PRUEBA DOBLE PARA EL ERROR DE TIPEO) ---
sfx = {
    "bow_hit": load_sound_list("bow", "bowHit", 4),
    "bow_reload": [load_single_sound("bow", "bowReload.ogg")], 
    "bow_extension": [load_single_sound("bow", "bowExstension.ogg")], 
    "bow_shoot": [load_single_sound("bow", "bowTrow.ogg")], 
    "creeper_hurt": load_sound_list("creeper", "creeperHurt", 3),
    "creeper_death": [load_single_sound("creeper", "creeperDeath.ogg")],
    "creeper_explode": load_sound_list("creeper", "explode", 3),
    "step": load_sound_list("step", "stepStone", 6),
    "zombie_hurt": load_sound_list("zombie", "zombieHurt", 2),
    "zombie_death": [load_single_sound("zombie", "zombieDeath.ogg")],
    "zombie_say": load_sound_list("zombie", "zombieSay", 3),
    "zombie_walk": load_sound_list("zombie", "zombieWalk", 2),
    "menu_click": [load_single_sound("menu", "menuClick.ogg")],
    "player_death": [load_single_sound("player", "playerDeath.ogg")],
    "player_level": [load_single_sound("xp", "xpLevel.ogg")],
    # Cargamos ambas versiones del nombre por si lo cambiaste:
    "xp_recolection": [load_single_sound("xp", "xpRecolection.ogg"), load_single_sound("xp", "xpRecoletion.ogg")] 
}

def play_random_sfx(sound_list, volume_scale=1.0):
    valid_sounds = [s for s in sound_list if s is not None]
    if valid_sounds:
        snd = random.choice(valid_sounds)
        snd.set_volume(0.8 * volume_scale) 
        snd.play()

def detener_sfx(sound_list):
    valid_sounds = [s for s in sound_list if s is not None]
    for snd in valid_sounds:
        snd.stop()

INTERVALO_SONIDO_PASOS = 50 
VELOCIDAD_ANIMACION_XP = 5 

# --- CARGAMOS LAS IMÁGENES ---
animacion_creeper = cargar_animacion("creeper", "creeper", 7)
animacion_zombie = cargar_animacion("zombie", "zombie", 12)
animacion_arco = cargar_animacion("bow", "bow", 6) 
animacion_xp = cargar_animacion("xpOrb", "xpOrb", 7) 

def aplicar_filtro_arco(frames_base, nivel):
    if nivel == 1:
        return frames_base 
        
    nuevos_frames = []
    for frame in frames_base:
        copia = frame.copy()
        if nivel == 2: 
            copia.fill((80, 50, 0), special_flags=pygame.BLEND_RGB_SUB)
        elif nivel == 3: 
            copia.fill((100, 155, 205), special_flags=pygame.BLEND_RGB_ADD)
        elif nivel == 4: 
            copia.fill((150, 0, 0), special_flags=pygame.BLEND_RGB_SUB)
            copia.fill((0, 155, 205), special_flags=pygame.BLEND_RGB_ADD)
        elif nivel >= 5: 
            copia.fill((100, 100, 0), special_flags=pygame.BLEND_RGB_SUB)
            copia.fill((30, 0, 60), special_flags=pygame.BLEND_RGB_ADD)
        nuevos_frames.append(copia)
    return nuevos_frames

animacion_arco_actual = aplicar_filtro_arco(animacion_arco, 1)

mobs_data = {
    "creeper": animacion_creeper,
    "zombie": animacion_zombie
}

try:
    fondo_original = pygame.image.load(os.path.join(TEXTURES_DIR, "background.png")).convert()
    fondo_img = pygame.transform.scale(fondo_original, (screen_width, screen_height))
except Exception as e:
    fondo_img = pygame.Surface((screen_width, screen_height))
    fondo_img.fill((40, 40, 40))

try:
    img_flecha_ui_grande = pygame.image.load(os.path.join(TEXTURES_DIR, "arrow.png")).convert_alpha()
    img_flecha_ui = pygame.transform.scale(img_flecha_ui_grande, (50, 50))
    img_flecha_ui_peque = pygame.transform.scale(img_flecha_ui_grande, (30, 30))
except Exception as e:
    img_flecha_ui = pygame.Surface((40, 40), pygame.SRCALPHA)
    img_flecha_ui.fill((200, 200, 200))
    img_flecha_ui_peque = pygame.Surface((30, 30), pygame.SRCALPHA)
    img_flecha_ui_peque.fill((200, 200, 200))

try:
    img_skeleton_ui_grande = pygame.image.load(os.path.join(TEXTURES_DIR, "skeleton.png")).convert_alpha()
    img_skeleton_ui = pygame.transform.scale(img_skeleton_ui_grande, (30, 30)) 
except Exception as e:
    img_skeleton_ui = pygame.Surface((30, 30), pygame.SRCALPHA)
    img_skeleton_ui.fill((255, 0, 255)) 

try:
    img_bow_icon_original = pygame.image.load(os.path.join(TEXTURES_DIR, "bowIcon.png")).convert_alpha()
    img_bow_icon_base = pygame.transform.scale(img_bow_icon_original, (120, 120)) 
except Exception as e:
    img_bow_icon_base = pygame.Surface((120, 120), pygame.SRCALPHA)
    img_bow_icon_base.fill((255, 0, 255))

# --- COLORES ---
COLOR_SANGRE = (150, 0, 0)
COLOR_CRUZ_BORDE = (50, 150, 255) 
COLOR_CRUZ_FONDO = (20, 60, 120)
COLOR_BOTON = (50, 150, 50)
COLOR_BOTON_HOVER = (80, 200, 80)
COLOR_BOTON_DESACTIVADO = (100, 100, 100)

# --- CONFIGURACIÓN DE DIFICULTAD Y BALANCEO MATEMÁTICO ---
dificultad = "Normal" 
pantalla_completa = False 

def obtener_vel_base():
    return 1.0032 if dificultad == "Normal" else 1.0045

def obtener_incremento_vel():
    return 0.00005 if dificultad == "Normal" else 0.00015

def obtener_max_flechas():
    return 8 if dificultad == "Normal" else 5

def calcular_costo_mejora(nivel):
    base = 120
    if nivel >= 4:
        base += (nivel - 3) * 40
    return base

# --- CLASES Y VARIABLES DEL JUEGO ---
class Enemigo:
    def __init__(self, es_boss=False):
        self.tipo = random.choice(["creeper", "zombie"])
        self.es_boss = es_boss
        self.escala = 0.10 
        self.estado = "vivo" 
        self.frame_actual = 0
        self.temporizador_animacion = 0
        self.temporizador_sonido_paso = random.randint(0, INTERVALO_SONIDO_PASOS)
        self.tiempo_muerte = 0
        self.offset_x = random.randint(-60, 60) 
        
        hp_base = 2.0 if dificultad == "Normal" else 3.0 
        
        if self.es_boss:
            multiplicador = 1.0 + (max(0, oleada_actual - 6) * 0.5)
            self.hp_max = (hp_base * 2.0 * multiplicador) + (oleada_actual * 0.5) 
            self.hp = self.hp_max
        else:
            multiplicador = 1.0 + (max(0, oleada_actual - 6) * 0.2)
            self.hp_max = hp_base * multiplicador
            self.hp = self.hp_max

# --- CLASE PARA LA EXPERIENCIA ---
class XpOrb:
    def __init__(self, x_inicial, y_inicial, escala_inicial, valor):
        self.escala_inicial = escala_inicial # Guardamos esto para la matemática 3D
        self.escala = escala_inicial
        self.frame_actual = random.randint(0, len(animacion_xp) - 1)
        self.temporizador_animacion = 0
        self.valor = valor 
        
        self.x = x_inicial
        self.y = y_inicial
        self.vel_x = random.uniform(-15.0, 15.0) * escala_inicial 
        self.vel_y = random.uniform(-20.0, -5.0) * escala_inicial 
        self.gravedad = 1.5 * escala_inicial
        self.piso_y = y_inicial + (random.uniform(20.0, 50.0) * escala_inicial)
        self.rebotando = True
        
        self.vel_z = obtener_vel_base() + random.uniform(0.005, 0.025)

FRAMES_POR_DIBUJO = 12 

oleada_actual = 1
mobs_en_pantalla = []
orbes_xp = [] 
mobs_por_spawnear = oleada_actual + 1 if dificultad == "Normal" else int(oleada_actual * 1.5) + 1
mobs_eliminados = 0
spawn_timer = 0
spawn_rate = 240 

estado_juego = "jugando" 
PUNTO_FUGA_Y = (screen_height // 2) - 80 
multiplicador_acercamiento = obtener_vel_base()
escala_maxima = 1.8 

# --- JUGADOR, ECONOMÍA Y STATS ---
flechas = obtener_max_flechas() 
flecha_progreso = 0.0
flecha_velocidad = 0.1 
disparando = False
objetivo_actual = None 
estado_arco = "idle" 

puntos = 0
nivel_arco = 1
dano_jugador = 1.0 
tiempo_tensado_segundos = 1.5 
nivel_disponible_sonido_reproducido = False 

boton_mejorar_rect = pygame.Rect(0, 0, 160, 160) 
boton_dif_rect = pygame.Rect(0, 0, 0, 0) 

# --- FUNCIONES DE DIBUJO UI ---
def render_texto_borde(fuente, texto, color, color_borde=(0,0,0)):
    sup_texto = fuente.render(texto, True, color)
    sup_borde = fuente.render(texto, True, color_borde)
    ancho, alto = sup_texto.get_size()
    surf = pygame.Surface((ancho + 2, alto + 2), pygame.SRCALPHA)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                surf.blit(sup_borde, (dx + 1, dy + 1))
    surf.blit(sup_texto, (1, 1))
    return surf

def dibujar_cruz_tecla(x, y, size=24, cross_color=COLOR_CRUZ_BORDE, background_color=COLOR_CRUZ_FONDO, stroke=3):
    cx, cy = int(x), int(y)
    w = size // 6
    h = size // 2
    points = [
        (cx - w, cy - h), (cx + w, cy - h), (cx + w, cy - w), (cx + h, cy - w),
        (cx + h, cy + w), (cx + w, cy + w), (cx + w, cy + h), (cx - w, cy + h),
        (cx - w, cy + w), (cx - h, cy + w), (cx - h, cy - w), (cx - w, cy - w)
    ]
    pygame.draw.polygon(screen, background_color, points)
    pygame.draw.lines(screen, cross_color, True, points, stroke)

def dibujar_diamante_tecla(x, y, size=24, diamond_color=(255, 150, 0), background_color=(80, 80, 80), stroke=2):
    cx, cy, r = int(x), int(y), int(size / 2)
    angles = [0, math.pi/2, math.pi, 3*math.pi/2]
    points = [(int(cx + r * math.cos(a)), int(cy + r * math.sin(a))) for a in angles]
    pygame.draw.polygon(screen, background_color, points)
    pygame.draw.lines(screen, diamond_color, True, points, stroke)

# --- BUCLE PRINCIPAL ---
while True:
    frames_tensado_totales = max(5, int(tiempo_tensado_segundos * 60)) 
    mouse_pos = pygame.mouse.get_pos() 
    costo_mejora = calcular_costo_mejora(nivel_arco)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            ctrl_presionado = mods & pygame.KMOD_CTRL
            
            if event.key == pygame.K_F11:
                pantalla_completa = not pantalla_completa
                if pantalla_completa:
                    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((screen_width, screen_height))
            
            if estado_juego == "jugando":
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    estado_juego = "tienda"
                    estado_arco = "idle" 
                    detener_sfx(sfx["bow_extension"]) 
                    
                if ctrl_presionado and event.key == pygame.K_c and flechas <= 4:
                    flechas = obtener_max_flechas()
                    play_random_sfx(sfx["bow_reload"]) 
                    
                if ctrl_presionado and event.key == pygame.K_v and flechas > 0 and not disparando and estado_arco == "idle":
                    vivos = [m for m in mobs_en_pantalla if m.estado == "vivo"]
                    if vivos:
                        estado_arco = "tensando"
                        tiempo_tensado = 0
                        play_random_sfx(sfx["bow_extension"]) 
                        
                        vivos.sort(key=lambda m: m.escala * (1.2 if m.es_boss else 1.0), reverse=True)
                        objetivo_actual = vivos[0] 
                        
            elif estado_juego == "tienda":
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT or event.key == pygame.K_ESCAPE:
                    estado_juego = "jugando"

            elif estado_juego == "intermedio":
                estado_juego = "jugando"
                oleada_actual += 1
                
                mobs_por_spawnear = oleada_actual + 1 if dificultad == "Normal" else int(oleada_actual * 1.5) + 1
                
                if oleada_actual >= 7:
                    mobs_por_spawnear += (oleada_actual - 6) * 3
                    
                mobs_eliminados = 0
                orbes_xp.clear() 
                multiplicador_acercamiento += obtener_incremento_vel()
                
            elif estado_juego == "game_over":
                if ctrl_presionado and event.key == pygame.K_z:
                    estado_juego = "jugando"
                    oleada_actual = 1
                    mobs_en_pantalla.clear()
                    orbes_xp.clear()
                    mobs_por_spawnear = 2 if dificultad == "Normal" else 3
                    mobs_eliminados = 0
                    flechas = obtener_max_flechas()
                    puntos = 0
                    nivel_arco = 1
                    dano_jugador = 1.0
                    tiempo_tensado_segundos = 1.5
                    animacion_arco_actual = aplicar_filtro_arco(animacion_arco, nivel_arco)
                    nivel_disponible_sonido_reproducido = False
                    
                    multiplicador_acercamiento = obtener_vel_base()
                    estado_arco = "idle"
                    disparando = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            if estado_juego == "tienda":
                if boton_mejorar_rect.collidepoint(mouse_pos) and puntos >= costo_mejora:
                    puntos -= costo_mejora
                    nivel_arco += 1
                    tiempo_tensado_segundos = max(0.15, tiempo_tensado_segundos - 0.35)
                    
                    if nivel_arco % 2 != 0:
                        dano_jugador += 0.5 
                        
                    animacion_arco_actual = aplicar_filtro_arco(animacion_arco, nivel_arco)
                    nivel_disponible_sonido_reproducido = False 
                    play_random_sfx(sfx["menu_click"])
                    
                elif boton_dif_rect.collidepoint(mouse_pos):
                    dificultad = "Dificil" if dificultad == "Normal" else "Normal"
                    flechas = obtener_max_flechas() 
                    multiplicador_acercamiento = obtener_vel_base() + (obtener_incremento_vel() * (oleada_actual - 1))
                    play_random_sfx(sfx["menu_click"])

    # --- LÓGICA Y DIBUJO ---
    screen.blit(fondo_img, (0, 0))

    if estado_juego == "jugando" or estado_juego == "tienda":
        
        if puntos >= costo_mejora and not nivel_disponible_sonido_reproducido:
            play_random_sfx(sfx["player_level"])
            nivel_disponible_sonido_reproducido = True
        elif puntos < costo_mejora:
            nivel_disponible_sonido_reproducido = False

        if estado_juego == "jugando" and mobs_por_spawnear > 0:
            spawn_timer += 1
            if spawn_timer >= spawn_rate:
                chance_boss = 15 if oleada_actual >= 5 else 0
                if oleada_actual >= 7:
                    chance_boss += (oleada_actual - 6) * 10 
                chance_boss = min(50, chance_boss) 
                
                es_boss = (random.randint(1, 100) <= chance_boss)
                mobs_en_pantalla.append(Enemigo(es_boss=es_boss))
                
                mobs_por_spawnear -= 1
                spawn_timer = 0
                
                if oleada_actual < 7:
                    spawn_rate = random.randint(240, 330) if dificultad == "Normal" else random.randint(180, 240)
                else:
                    limite_inf = max(60, 200 - (oleada_actual * 10))
                    limite_sup = max(120, 260 - (oleada_actual * 10))
                    spawn_rate = random.randint(limite_inf, limite_sup)

        elementos_a_dibujar = []
        for mob in mobs_en_pantalla:
            profundidad_visual = mob.escala * (1.2 if mob.es_boss else 1.0)
            elementos_a_dibujar.append({"tipo": "mob", "obj": mob, "profundidad": profundidad_visual})
        for orbe in orbes_xp:
            elementos_a_dibujar.append({"tipo": "orbe", "obj": orbe, "profundidad": orbe.escala})
            
        elementos_a_dibujar.sort(key=lambda e: e["profundidad"])

        for elemento in elementos_a_dibujar:
            if elemento["tipo"] == "mob":
                mob = elemento["obj"]
                if estado_juego == "jugando":
                    mob.temporizador_animacion += 1
                    if mob.temporizador_animacion >= FRAMES_POR_DIBUJO:
                        mob.temporizador_animacion = 0
                        mob.frame_actual = (mob.frame_actual + 1) % len(mobs_data[mob.tipo])
                    
                    if mob.estado == "vivo":
                        mob.temporizador_sonido_paso += 1
                        if mob.temporizador_sonido_paso >= INTERVALO_SONIDO_PASOS:
                            mob.temporizador_sonido_paso = 0
                            vol_3d = min(1.0, mob.escala / 1.2)
                            play_random_sfx(sfx["step"], vol_3d)
                            
                            if mob.tipo == "zombie":
                                if random.randint(1, 100) <= 25:
                                    play_random_sfx(sfx["zombie_walk"], vol_3d)
                                elif random.randint(1, 100) <= 30:
                                    play_random_sfx(sfx["zombie_say"], vol_3d)

                        if mob.es_boss:
                            vel_boss = 1.0 + ((multiplicador_acercamiento - 1.0) * 0.70)
                            mob.escala *= vel_boss
                        else:
                            mob.escala *= multiplicador_acercamiento
                            
                        if mob.escala >= escala_maxima:
                            estado_juego = "game_over" 
                            detener_sfx(sfx["bow_extension"]) 
                            play_random_sfx(sfx["player_death"], 1.0)
                            if mob.tipo == "creeper":
                                play_random_sfx(sfx["creeper_explode"], 1.0)

                    elif mob.estado == "dying":
                        mob.escala = max(0.01, mob.escala - 0.01)
                        mob.tiempo_muerte += 1
                        if mob.tiempo_muerte > 20:
                            mobs_en_pantalla.remove(mob)
                            mobs_eliminados += 1
                            continue 

                mob_original = mobs_data[mob.tipo][mob.frame_actual]
                modificador_tamano = 0.70 if mob.tipo == "creeper" else 1.0
                mod_escala_boss = 1.2 if mob.es_boss else 1.0
                mod_ancho_boss = 1.1 if mob.es_boss else 1.0
                
                nuevo_ancho = max(1, int(mob_original.get_width() * mob.escala * modificador_tamano * mod_escala_boss * mod_ancho_boss))
                nuevo_alto = max(1, int(mob_original.get_height() * mob.escala * modificador_tamano * mod_escala_boss))
                
                factor_pixelado = 10
                low_res_w = max(1, int(nuevo_ancho / factor_pixelado))
                low_res_h = max(1, int(nuevo_alto / factor_pixelado))
                
                mob_low_res = pygame.transform.scale(mob_original, (low_res_w, low_res_h))
                mob_escalado = pygame.transform.scale(mob_low_res, (nuevo_ancho, nuevo_alto))

                offset_y = (nuevo_alto // 2) * 0.3 
                centro_x = (screen_width // 2) + int(mob.offset_x * mob.escala)
                rect_mob = mob_escalado.get_rect(center=(centro_x, PUNTO_FUGA_Y + offset_y))
                
                if mob.estado == "dying":
                    flash_rojo = pygame.Surface((nuevo_ancho, nuevo_alto), pygame.SRCALPHA)
                    flash_rojo.fill((255, 0, 0, 128))
                    mob_escalado.blit(flash_rojo, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                screen.blit(mob_escalado, rect_mob)
                
                if mob.es_boss and mob.estado == "vivo":
                    ancho_barra = nuevo_ancho
                    alto_barra = max(5, int(nuevo_alto * 0.05)) 
                    x_barra = rect_mob.left
                    y_barra = rect_mob.top - alto_barra - 10 
                    pygame.draw.rect(screen, (150, 0, 0), (x_barra, y_barra, ancho_barra, alto_barra))
                    porcentaje_hp = max(0, mob.hp / mob.hp_max)
                    pygame.draw.rect(screen, (0, 255, 0), (x_barra, y_barra, int(ancho_barra * porcentaje_hp), alto_barra))
                    pygame.draw.rect(screen, (255, 255, 255), (x_barra, y_barra, ancho_barra, alto_barra), 2)

            elif elemento["tipo"] == "orbe":
                orbe = elemento["obj"]
                if estado_juego == "jugando":
                    orbe.temporizador_animacion += 1
                    if orbe.temporizador_animacion >= VELOCIDAD_ANIMACION_XP:
                        orbe.temporizador_animacion = 0
                        orbe.frame_actual = (orbe.frame_actual + 1) % len(animacion_xp)
                    
                    if orbe.rebotando:
                        orbe.x += orbe.vel_x
                        orbe.y += orbe.vel_y
                        orbe.vel_y += orbe.gravedad
                        if orbe.y >= orbe.piso_y:
                            orbe.y = orbe.piso_y
                            orbe.rebotando = False
                    else:
                        orbe.escala *= orbe.vel_z 
                        
                        # FIX MATEMÁTICO: Escala y Posición Y sincronizadas 1 a 1
                        progreso = (orbe.escala - orbe.escala_inicial) / (escala_maxima - orbe.escala_inicial)
                        progreso = max(0.0, min(1.0, progreso)) # Asegura que no se rompa el calculo
                        
                        # La bolita viaja desde donde cayó hasta la base de tu pantalla
                        orbe.y = orbe.piso_y + progreso * (screen_height + 50 - orbe.piso_y)
                        
                        # Efecto 3D adicional: se abren un poco al acercarse a la pantalla
                        distancia_x = orbe.x - (screen_width // 2)
                        orbe.x += distancia_x * (orbe.vel_z - 1.0)
                        
                    if orbe.escala >= escala_maxima:
                        puntos += orbe.valor
                        play_random_sfx(sfx["xp_recolection"], 1.0) 
                        if orbe in orbes_xp:
                            orbes_xp.remove(orbe)
                        continue

                if animacion_xp:
                    img_orbe = animacion_xp[orbe.frame_actual]
                    ancho_orbe = max(1, int(60 * orbe.escala)) # Tamaño aumentado (antes era 40, ahora 60)
                    factor_pixelado_xp = 4
                    low_w = max(1, ancho_orbe // factor_pixelado_xp)
                    
                    orbe_low = pygame.transform.scale(img_orbe, (low_w, low_w))
                    orbe_final = pygame.transform.scale(orbe_low, (ancho_orbe, ancho_orbe))
                    screen.blit(orbe_final, orbe_final.get_rect(center=(int(orbe.x), int(orbe.y))))

        if estado_arco == "tensando" and estado_juego == "jugando":
            if objetivo_actual not in mobs_en_pantalla or objetivo_actual.estado != "vivo":
                estado_arco = "idle"
                detener_sfx(sfx["bow_extension"]) 
            else:
                tiempo_tensado += 1
                if tiempo_tensado >= frames_tensado_totales:
                    estado_arco = "idle"
                    disparando = True
                    flechas -= 1
                    flecha_progreso = 0.0
                    
                    detener_sfx(sfx["bow_extension"]) 
                    play_random_sfx(sfx["bow_shoot"]) 

        if disparando and objetivo_actual in mobs_en_pantalla and estado_juego == "jugando":
            flecha_progreso += flecha_velocidad
            
            if flecha_progreso < 1.0:
                start_x = int(1073 * (screen_width / 1547))
                start_y = int(517 * (screen_height / 870))
                
                end_x = (screen_width // 2) + int(objetivo_actual.offset_x * objetivo_actual.escala)
                end_y = PUNTO_FUGA_Y + ((int(mobs_data[objetivo_actual.tipo][0].get_height() * objetivo_actual.escala * (0.8 if objetivo_actual.tipo == "creeper" else 1.0))) // 2) * 0.3
                
                actual_y = start_y + (end_y - start_y) * flecha_progreso
                actual_x = start_x + (end_x - start_x) * flecha_progreso
                
                tamaño_flecha = max(5, int(100 * (1.0 - (flecha_progreso * 0.7))))
                ancho_flecha = max(2, tamaño_flecha // 4)
                
                dx = end_x - start_x
                dy = end_y - start_y
                angulo = math.atan2(dy, dx) 
                
                punta_x, punta_y = actual_x, actual_y
                largo_cabeza = tamaño_flecha * 0.4
                base_x = punta_x - largo_cabeza * math.cos(angulo)
                base_y = punta_y - largo_cabeza * math.sin(angulo)
                
                izq_x = base_x + ancho_flecha * math.cos(angulo - math.pi/2)
                izq_y = base_y + ancho_flecha * math.sin(angulo - math.pi/2)
                der_x = base_x + ancho_flecha * math.cos(angulo + math.pi/2)
                der_y = base_y + ancho_flecha * math.sin(angulo + math.pi/2)
                
                cola_x = punta_x - tamaño_flecha * math.cos(angulo)
                cola_y = punta_y - tamaño_flecha * math.sin(angulo)
                
                pygame.draw.polygon(screen, (200, 200, 200), [(punta_x, punta_y), (izq_x, izq_y), (der_x, der_y)])
                pygame.draw.line(screen, (150, 100, 50), (base_x, base_y), (cola_x, cola_y), max(2, ancho_flecha//2))
                
            else:
                vol_3d = min(1.0, objetivo_actual.escala / 1.0)
                play_random_sfx(sfx["bow_hit"], vol_3d)

                objetivo_actual.hp -= dano_jugador
                if objetivo_actual.hp <= 0:
                    objetivo_actual.estado = "dying"
                    
                    centro_mob_x = (screen_width // 2) + int(objetivo_actual.offset_x * objetivo_actual.escala)
                    alto_mob = mobs_data[objetivo_actual.tipo][0].get_height() * objetivo_actual.escala * (0.7 if objetivo_actual.tipo == "creeper" else 1.0)
                    offset_y = (alto_mob // 2) * 0.3
                    centro_mob_y = PUNTO_FUGA_Y + offset_y
                    
                    xp_por_orbe = 15 if objetivo_actual.es_boss else 5
                    for _ in range(3):
                        orbes_xp.append(XpOrb(centro_mob_x, centro_mob_y, objetivo_actual.escala, xp_por_orbe))

                    if objetivo_actual.tipo == "zombie":
                        play_random_sfx(sfx["zombie_death"], vol_3d)
                    else:
                        play_random_sfx(sfx["creeper_death"], vol_3d)
                else:
                    if objetivo_actual.tipo == "zombie":
                        play_random_sfx(sfx["zombie_hurt"], vol_3d)
                    else:
                        play_random_sfx(sfx["creeper_hurt"], vol_3d)

                disparando = False
                objetivo_actual = None
                
        elif disparando and objetivo_actual not in mobs_en_pantalla:
            disparando = False 

        if estado_juego == "jugando" and mobs_por_spawnear == 0 and len(mobs_en_pantalla) == 0 and len(orbes_xp) == 0:
            estado_juego = "intermedio"

    # --- RENDERIZAR ARCO TEÑIDO ---
    indice_arco = 0
    if estado_arco == "tensando":
        calculo_indice = 1 + int((tiempo_tensado / frames_tensado_totales) * (len(animacion_arco_actual) - 1))
        indice_arco = calculo_indice
        
    indice_arco = min(len(animacion_arco_actual) - 1, indice_arco)
    imagen_arco_actual = animacion_arco_actual[indice_arco]
    arco_escalado = pygame.transform.smoothscale(imagen_arco_actual, (screen_width, screen_height))
    screen.blit(arco_escalado, (0, 0))

    # --- INTERFAZ (UI) ---
    fuente_chica = pygame.font.Font(RUTA_FUENTE, 25)
    fuente_media = pygame.font.Font(RUTA_FUENTE, 40)
    fuente_puntos = pygame.font.Font(RUTA_FUENTE, 55)
    fuente_grande = pygame.font.Font(RUTA_FUENTE, 70)

    if estado_juego == "jugando":
        txt_oleada = render_texto_borde(fuente_chica, f"Oleada: {oleada_actual}", (255, 255, 255))
        txt_faltan = render_texto_borde(fuente_chica, f"Faltan: {mobs_por_spawnear + len([m for m in mobs_en_pantalla if m.estado == 'vivo'])}", (200, 200, 200))
        screen.blit(txt_oleada, (20, 20))
        screen.blit(txt_faltan, (20, 60))
        
        # --- BARRA DE EXPERIENCIA ESTILO MINECRAFT ---
        barra_w = 400
        barra_h = 15
        barra_x = screen_width // 2 - barra_w // 2
        barra_y = 40
        
        pygame.draw.rect(screen, (0, 0, 0), (barra_x - 2, barra_y - 2, barra_w + 4, barra_h + 4))
        pygame.draw.rect(screen, (50, 50, 50), (barra_x, barra_y, barra_w, barra_h))
        
        progreso_xp = min(1.0, puntos / costo_mejora)
        ancho_xp = int(barra_w * progreso_xp)
        if ancho_xp > 0:
            pygame.draw.rect(screen, (0, 255, 0), (barra_x, barra_y, ancho_xp, barra_h))
            
        txt_puntos = render_texto_borde(fuente_chica, f"{puntos}", (50, 255, 50))
        screen.blit(txt_puntos, txt_puntos.get_rect(center=(screen_width // 2 - 20, barra_y - 15)))

        if puntos >= costo_mejora:
            rebote_y = math.sin(pygame.time.get_ticks() / 150.0) * 8 
            arr_x = barra_x + barra_w + 20
            arr_y = barra_y + (barra_h // 2) + rebote_y
            
            puntos_flecha = [
                (arr_x, arr_y - 15), (arr_x - 10, arr_y - 5), (arr_x - 5, arr_y - 5),
                (arr_x - 5, arr_y + 10), (arr_x + 5, arr_y + 10), (arr_x + 5, arr_y - 5),
                (arr_x + 10, arr_y - 5)
            ]
            pygame.draw.polygon(screen, (0, 0, 0), puntos_flecha) 
            pygame.draw.polygon(screen, (255, 255, 0), puntos_flecha, 2)

        if flechas == 0:
            rojo_transparente = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            rojo_transparente.fill((255, 0, 0, 40)) 
            screen.blit(rojo_transparente, (0, 0))
            
            urgente = render_texto_borde(fuente_grande, "+ C PARA RECARGAR!", (255, 255, 0))
            ancho_cruz = 80
            separacion = 20
            ancho_texto = urgente.get_width()
            
            ancho_total = ancho_cruz + separacion + ancho_texto
            start_x = (screen_width - ancho_total) // 2
            
            cruz_x = start_x + (ancho_cruz // 2)
            cruz_y = screen_height // 2
            dibujar_cruz_tecla(cruz_x, cruz_y, size=ancho_cruz, stroke=6)
            
            texto_x = start_x + ancho_cruz + separacion
            texto_y = cruz_y - (urgente.get_height() // 2) 
            screen.blit(urgente, (texto_x, texto_y))
        else:
            max_capacidad = obtener_max_flechas()
            espacio_entre = 45 if max_capacidad > 5 else 60
            alto_total_flechas = (flechas - 1) * espacio_entre
            inicio_y = (screen_height // 2) - (alto_total_flechas // 2) - 50 
            
            for i in range(flechas):
                rect_flechita = img_flecha_ui.get_rect(center=(50, inicio_y + (i * espacio_entre)))
                screen.blit(img_flecha_ui, rect_flechita)

        if flechas > 0:
            y_r1 = screen_height - 120
            dibujar_cruz_tecla(40, y_r1, size=26)
            screen.blit(img_flecha_ui_peque, img_flecha_ui_peque.get_rect(center=(150, y_r1)))
            txt_rec = render_texto_borde(fuente_chica, "+ C =", COLOR_CRUZ_BORDE)
            screen.blit(txt_rec, (60, y_r1 - 22))
            
            y_r2 = screen_height - 75
            dibujar_cruz_tecla(40, y_r2, size=26)
            screen.blit(img_skeleton_ui, img_skeleton_ui.get_rect(center=(150, y_r2)))
            txt_disp = render_texto_borde(fuente_chica, "+ V =", COLOR_CRUZ_BORDE)
            screen.blit(txt_disp, (60, y_r2 -22))
            
            y_r3 = screen_height - 30
            dibujar_diamante_tecla(40, y_r3, size=24)
            txt_dinero = render_texto_borde(fuente_chica, "= $$$", (255, 200, 0))
            screen.blit(txt_dinero, (60, y_r3 - 19))

        if estado_arco == "tensando":
            ancho_barra = 200
            pygame.draw.rect(screen, (0, 0, 0), (screen_width//2 - ancho_barra//2 - 2, screen_height - 62, ancho_barra + 4, 14))
            pygame.draw.rect(screen, (100, 100, 100), (screen_width//2 - ancho_barra//2, screen_height - 60, ancho_barra, 10))
            progreso = (tiempo_tensado / frames_tensado_totales) * ancho_barra
            pygame.draw.rect(screen, (255, 255, 255), (screen_width//2 - ancho_barra//2, screen_height - 60, progreso, 10))

    elif estado_juego == "tienda":
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) 
        screen.blit(overlay, (0, 0))
        
        info_txt = render_texto_borde(fuente_media, f"Nivel Actual: {nivel_arco}", (200, 200, 200))
        screen.blit(info_txt, info_txt.get_rect(center=(screen_width//2 - 20, 190)))
        
        txt_costo = render_texto_borde(fuente_media, f"Costo: {costo_mejora} xp", (255, 255, 0))
        screen.blit(txt_costo, txt_costo.get_rect(center=(screen_width//2 - 20, 250)))
        
        boton_mejorar_rect.center = (screen_width // 2 - 20, 370) 
        puedo_comprar = puntos >= costo_mejora
        color_btn = COLOR_BOTON_HOVER if boton_mejorar_rect.collidepoint(mouse_pos) and puedo_comprar else (COLOR_BOTON if puedo_comprar else COLOR_BOTON_DESACTIVADO)
        
        pygame.draw.rect(screen, color_btn, boton_mejorar_rect, border_radius=15)
        pygame.draw.rect(screen, (0, 0, 0), boton_mejorar_rect, 4, border_radius=15) 
        
        lista_temporal = [img_bow_icon_base]
        icono_filtrado = aplicar_filtro_arco(lista_temporal, nivel_arco + 1)[0]
        screen.blit(icono_filtrado, icono_filtrado.get_rect(center=boton_mejorar_rect.center))
        
        texto_dif = render_texto_borde(fuente_media, "Dificultad:", (255, 255, 255))
        ancho_texto_dif = texto_dif.get_width()
        ancho_boton_dif = 150
        espacio_dif = 15
        ancho_total_dif = ancho_texto_dif + espacio_dif + ancho_boton_dif
        
        start_x_dif = (screen_width - ancho_total_dif) // 2 - 20
        screen.blit(texto_dif, (start_x_dif, 500))
        
        boton_dif_rect.x = start_x_dif + ancho_texto_dif + espacio_dif
        boton_dif_rect.y = 490 
        boton_dif_rect.width = ancho_boton_dif
        boton_dif_rect.height = 50
        
        color_btn_dif = (50, 150, 200) if boton_dif_rect.collidepoint(mouse_pos) else (40, 100, 150)
        pygame.draw.rect(screen, color_btn_dif, boton_dif_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), boton_dif_rect, 3, border_radius=10)
        
        lbl_dif = render_texto_borde(fuente_chica, dificultad, (255, 255, 255))
        rect_lbl = lbl_dif.get_rect(center=boton_dif_rect.center)
        rect_lbl.x -= 5
        screen.blit(lbl_dif, rect_lbl)

        txt_presiona = render_texto_borde(fuente_chica, "Presiona ", (150, 150, 150))
        txt_cerrar = render_texto_borde(fuente_chica, " para cerrar", (150, 150, 150))
        
        ancho_presiona = txt_presiona.get_width()
        ancho_cerrar = txt_cerrar.get_width()
        ancho_diamante = 24
        separacion = 5
        
        ancho_total_salir = ancho_presiona + separacion + ancho_diamante + separacion + ancho_cerrar
        start_x_salir = (screen_width - ancho_total_salir) // 2 - 20
        y_salir = 580
        
        screen.blit(txt_presiona, (start_x_salir, y_salir))
        
        centro_x_diamante = start_x_salir + ancho_presiona + separacion + (ancho_diamante // 2)
        centro_y_diamante = y_salir + (txt_presiona.get_height() // 2)
        dibujar_diamante_tecla(centro_x_diamante, centro_y_diamante-3, size=ancho_diamante)
        
        x_cerrar = start_x_salir + ancho_presiona + (separacion * 2) + ancho_diamante
        screen.blit(txt_cerrar, (x_cerrar+3, y_salir))

    elif estado_juego == "intermedio":
        msj = render_texto_borde(fuente_grande, f"¡OLEADA {oleada_actual} SUPERADA!", (0, 255, 0))
        screen.blit(msj, msj.get_rect(center=(screen_width//2 - 20, screen_height//2 - 50)))
        sub = render_texto_borde(fuente_chica, "Presiona cualquier tecla para la siguiente oleada...", (255, 255, 255))
        screen.blit(sub, sub.get_rect(center=(screen_width//2 - 20, screen_height//2 + 30)))

    elif estado_juego == "game_over":
        screen.fill(COLOR_SANGRE)
        msj = render_texto_borde(fuente_grande, "¡TE ATRAPARON!", (255, 255, 255))
        screen.blit(msj, msj.get_rect(center=(screen_width//2 - 20, screen_height//2 - 50)))
        
        cruz_x, cruz_y = screen_width // 2 - 140, screen_height // 2 + 40
        dibujar_cruz_tecla(cruz_x, cruz_y, size=30)
        sub = render_texto_borde(fuente_chica, " + Z = Reintentar", (255, 255, 0))
        screen.blit(sub, (cruz_x + 25, cruz_y - 15))

    pygame.display.flip()
    clock.tick(60)