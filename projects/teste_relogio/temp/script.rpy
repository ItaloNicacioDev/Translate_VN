default persistent.firstrun = False

label splashscreen:
    if persistent.firstrun == False:
        scene black
        call screen language_select with dissolve
    else:
        pass
    return

screen language_select:
    modal True
    window:
        background None
        xalign 0.5 yalign 0.5
        xsize 1200 ysize 1000
        has vbox
        yalign 0.5
        spacing 30
        label "{size=+5}Content Warning{/size}" xalign 0.5
        text "This game is not suitable for everyone. It contains mature themes such as depictions of sexual activity. By continuing past this warning, you confirm that you are 18 years of age or above, and can legally view such content." xalign 0.5
        text "Please select a language." xalign 0.5
        null height 20
        hbox:
            xalign 0.5
            spacing 300
            button:
                xsize 200 ysize 70
                idle_background "#00000080"
                hover_background "#ADD8E660"
                text "English" xalign 0.5 yalign 0.5
                action [Language("English"), SetVariable("persistent.firstrun", True), Return()]
            button:
                xsize 200 ysize 70
                idle_background "#00000080"
                hover_background "#ADD8E660"
                text "Español" xalign 0.5 yalign 0.5
                action [Language(None), SetVariable("persistent.firstrun", True), Return()]
        null height 20
        text "{size=-5}Language settings can be changed in the Preferences option. This warning will only be shown once.{/size}" xalign 0.5




image cocina = "images/fondos/cocina.png"
image dormitorio = "images/fondos/dormitorio.png"
image dormitorio_tarde = "images/fondos/dormitorio_tarde.png"
image dormitorio_noche = "images/fondos/dormitorio_noche.png"
image banio = "images/fondos/banio.png"
image banio_tarde = "images/fondos/banio_noche.png"
image banio_noche = "images/fondos/banio_noche.png"
image salon = "images/fondos/salon.png"


image vestuario = "images/fondos/vestuarios.png"
image gimnasio = "images/fondos/gimnasio.png"
image duchas_gimnasio = "images/fondos/duchas.png"
image zonaprivada = "images/fondos/zonaprivada.png"
image probadores = "images/fondos/probadores.png"
image piso_tiger = "images/fondos/piso_tiger.png"



image restaurante = "images/fondos/bar_presodal.png"
image dormitorio_presodal = "images/fondos/dormitorio_presodal.png"
image cocina_presodal = "images/fondos/cocina_presodal.png"
image salon_presodal = "images/fondos/salon_presodal.png"
image burdel = "images/fondos/burdel.png"
image disco_privada = "images/fondos/disco privada.png"
image oficina_kyle = "images/fondos/oficina_kyle.png"
image backstage = "images/fondos/backstage_prost.png"



image dormitoriomarcos = "images/fondos/dormitoriomarcos.png"
image salonmarcos = "images/fondos/salamarcos.png"
image cocinamarcos = "images/fondos/cocinamarcos.png"
image campo_recuerdo = "images/fondos/campo.png"
image banio_marcos = "images/fondos/banio_marcos.png"
image clase = "images/fondos/clase.png"


image recepcion_darius = "images/fondos/recibidor_darius.png"
image oficina_darius = "images/fondos/oficina_darius.png"
image vestidor_darius = "images/fondos/vestidor_darius.png"
image pasillo_darius = "images/fondos/pasillo_darius.png"
image salon_mansion = "images/fondos/salon_mansion.png"


image casa_clarence = "images/fondos/casa_clarence.png"
image atico_clarence = "images/fondos/atico_clarence.png"
image oficina_clarence = "images/fondos/oficina_clarence.png"
image cocina_clarence = "images/fondos/cocina_clarence.png"



image bg negro = "images/fondos/black.png"
image callejon = "images/fondos/callejon.png"
image callepeligrosa = "images/fondos/callepeligrosa.png"
image callecasa = "images/fondos/callebuena.png"
image ciudad = "images/fondos/ciudad.png"
image parque = "images/fondos/parque_dia.png"
image parque_noche = "images/fondos/parque_noche.png"
image cafeteria = "images/fondos/cafeteria.png"
image restaurante2 = "images/fondos/restaurante2.png"
image centrocomercial = "images/fondos/centrocomercial.png"
image tiendavideojuegos = "images/fondos/tiendavideojuegos.png"
image supermercado = "images/fondos/supermercado.png"
image tiendaropa = "images/fondos/tienda ropa.png"
image parque_pesadilla = "images/fondos/parque_pesadilla.png"
image oficina_psicologo = "images/fondos/oficina_psicologo.png"
image arcade = "images/fondos/arcade.png"
image bolera = "images/fondos/bolera.png"
image oficina_vr = "images/fondos/oficina_vr.png"
image espera_vr = "images/fondos/espera_vr.png"
image bosque_vr = "images/fondos/bosque_vr.png"
image cementerio = "images/fondos/cementerio.png"
image pueblo = "images/fondos/pueblo.png"
image autopista = "images/fondos/autopista.png"
image convencion_juegos = "images/fondos/convencion_juegos.png"
image hospital = "images/fondos/hospital.png"
image habitacion_hospital = "images/fondos/habitacion_hospital.png"
image mercado_nocturno = "images/fondos/mercado_nocturno.png"


image tiger_prologo = "images/cgs/tiger_prologo.png"
image tiger_dia6_vestidor = "images/cgs/tiger_dia6_vestidor.png"


image presodal_dia2 = "images/cgs/presodal_dia2.png"
image presodal_vip_1 = "images/cgs/presodal_vip_1.png"
image presodal_vip_2 = "images/cgs/presodal_vip_2.png"
image presodal_vip_3 = "images/cgs/presodal_vip_3.png"
image presodal_vip_4 = "images/cgs/presodal_vip_4.png"
image presodal_vip_5 = "images/cgs/presodal_vip_5.png"
image presodal_vip_6 = "images/cgs/presodal_vip_6.png"
image presodal_cap9_manana1 = "images/cgs/presodal_dia5_manana1.png"
image presodal_cap9_manana3 = "images/cgs/presodal_dia5_manana3.png"
image presodal_cap8_noche3 = "images/cgs/presodal_dia5_noche3.png"
image presodal_cap8_noche2 = "images/cgs/presodal_dia5_noche2.png"
image presodal_cap8_noche1 = "images/cgs/presodal_dia5_noche1.png"


image marcos_dia2 = "images/cgs/marcos_dia2.png"
image marcos_dia3_1 = "images/cgs/marcos_dia3_1.png"
image marcos_dia3_2 = "images/cgs/marcos_dia3_2.png"
image marcos_dia3_3 = "images/cgs/marcos_dia3_3.png"
image marcos_dia3_4 = "images/cgs/marcos_dia3_4.png"
image marcos_dia4 = "images/cgs/marcos_dia4.png"
image marcos_dia5_1 = "images/cgs/marcos_dia5_1.png"
image marcos_dia5_2 = "images/cgs/marcos_dia5_2.png"
image marcos_dia5_3 = "images/cgs/marcos_dia5_3.png"




image clarence_dia3_banio = "images/cgs/clarence_dia3_banio.png"


image alexq_1 = "images/fanarts/alexq_1.png"
image haslord_1 = "images/fanarts/haslord/haslord_1.png"
image orecobosrojas_1 = "images/fanarts/orebcobosrojas_1.png"
image kaisanzang_1 = "images/fanarts/kaisanzang_1.png"
image lucartss_1 = "images/fanarts/lucartss_1.png"
image haslord_1 = "images/fanarts/haslord/haslord2_1.png"
image haslord_1 = "images/fanarts/haslord/haslord2_2.png"
image haslord_1 = "images/fanarts/haslord/haslord2_3.png"
image haslord_1 = "images/fanarts/haslord/haslord2_4.png"
image haslord_1 = "images/fanarts/haslord/haslord2_5.png"
image haslord_1 = "images/fanarts/haslord/haslord2_6.png"
image lilardo_1 = "images/fanarts/luiseduardo/lilardo_1.png"
image lilardo_2 = "images/fanarts/luiseduardo/lilardo_2.png"
image lilardo_3 = "images/fanarts/luiseduardo/lilardo_3.png"
image hfz = "images/fanarts/hfz.png"
image lobus = "images/fanarts/lobus.png"
image pyrusk = "images/fanarts/pyrusk.png"




define oc = Character("[name]", color="#DBDBDB")
define jl = Character("Julia", color="#504F4F")
define hr = Character("Harold")
define so = Character("Sofia")
define fi = Character("Filena")
define le = Character("Leonardo")
define js = Character("Josh")


define t = Character("Tiger", color="#FF8214")
define b = Character("Buld", color="#9F6328")
define mt = Character("Mantar", color="#935D04")
define cr = Character("Crock", color="#03C808")
define ld = Character("Lindrer", color="#e93c70")
define zo = Character("Zoe")
define an = Character("Angela", color="#C503C8")
define dk = Character("Derkan", color="#dde013")


define p = Character("Presodal", color="#1BB2C5")
define al = Character("Aleinor")
define r = Character("Raúl")
define mn = Character("Manny")
define sh = Character("Shona")
define rc = Character("Rachel")
define mk = Character("Mika")
define kl = Character("Kyle")


define m = Character("Marcos", color="#11BA02")
define mm = Character("Myriam")
define ti = Character("Otis")


define d = Character("Darius", color="#E20202")
define yn = Character("Yuon", color="#FFFFFF")
define li = Character("Lisa")
define st = Character("Stanley")
define bl = Character("Belinda", color="#aaf58c")


define c = Character("Clarence", color="#18F7DB")


define pl = Character("Pedro")
define lx = Character("Alex")




define show_nsfw = True

label start:

    stop music

    "Bienvenido a Labios Salvajes."
    "Esta novela visual está en desarrollo."
    "Todos los personajes, nombres, lugares y demás son propiedad de la imaginación del escritor o se han usado de manera ficticia."
    "Cualquier parecido con hechos o personas, reales o ficticias, es pura casualidad."
    "Labios Salvajes tiene y TENDRÁ contenido maduro y sensible que algunas personas pueden encontrar ofensivo o molesto."
    "Si continúas después de este aviso, doy por hecho que eres mayor de 18 años. Si no es así, es bajo tu propio riesgo."
    "Y ahora, antes de empezar, necesito que me digas tu nombre."

    python:

        name = renpy.input(_("¿Cuál es tu nombre? Nombre por defecto: Lucas."))

        name = name.strip() or __("Lucas")

    "Gracias, es muy importante."
    "Ahora entraremos en una gran decisión."
    "¿Qué historia quieres leer?"
    "Aviso: Las demás rutas estarán disponibles pronto."
    menu:
        "Tigre Boxeador":
            "Muy bien. Esta historia ha sido creada originalmente en Wattpad."
            "Tendrá algunos cambios, pero también contará parte de la vida de los demás personajes principales."
            "Esto no significa que se cuente todo sobre ellos, pues algunos secretos se mantienen para sus historias."
            "Espero que te guste y te deje con ganas de más."
            pause 2
            jump prologo_tiger
        "Lazos Azules":

            "¿Qué hubiera pasado si Tiger no te hubiera salvado?"
            "¿Y si no te hubiera encontrado en esa calle, sino que seguía en el restaurante?"
            "¿Habrías tenido la misma suerte? ¿Habrías muerto en aquel lugar?"
            "Sólo, con la mirada en el cielo, siendo apuñalado una y otra vez..."
            "¿Qué hubiera pasado? Es lo que me pregunto todo el tiempo."
            pause 2
            jump presodal_prologo
        "Husky Parlanchín":

            "¿Qué hubiera pasado si hubieras escogido una ruta distinta?"
            "¿Y si fuera otra persona quien te ayudase?"
            "¿Conocerías a las mismas personas o el destino no lo querría así?"
            "¿Quieres descubrirlo? Yo también."
            pause 2
            jump clarence_prologo
        "Busca Llamas":

            pause 2.0
            jump darius_prologo
        "Especial Q&A 5º Aniversario":

            jump preguntas_respuestas
return
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
