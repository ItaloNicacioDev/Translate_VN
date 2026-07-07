














define config.name = _("Labios Salvajes")





define gui.show_name = False




define config.version = "0.56"





define gui.about = _p("""

    Original Story by: PedroLibros (Wattpad: Tigre Boxeador)

    Artist/s: {a=https://x.com/vitaly4321}Vitaly4321{/a}, {a=https://x.com/gimetrixz}Gimetrixz{/a}

    Backgrounds & CGs: {a=https://x.com/DelCrysta}DelCrysta{/a}

    Translator/s: Alex (English)

    Programmer: {a=https://x.com/SharpClawr}SharpClawr{/a} (Developer of {a=https://sanctuaryfvn.itch.io/sanctuary}Sanctuary{/a})

    Composer: {a=https://jordanns.carrd.co/}JordanM{/a}

    UI Design: DjmadeyeVN ({a=https://x.com/DjmadeyeVN}Twitter{/a} & {a=https://djmadeyevn.itch.io}Itch{/a})
    
    Main Menu song / Sad Lips / Happy Meal / Fight Me / LoFiJazz

    Bensound:

    Tomorrow / Memories / The Jazz Piano / Love / Acoustic Breeze / Sad Day / Pop Dance / Moose

    Audionatix:

    Fight Scene / Beginning / Acoustic Guitar #1 / Acoustic Meditation

    Soundcloud:

    Hip-Hop Instrumental No.138 - Hiena / Lakey Inspired - Chill Day / Gymnopédie No.1 - Erik Satie

    YouTube:

    All This - Kevin MacLeod ; Smooth Touch - 10 Minutes Of Pleasure (feat. G-Sax)

    Licensed under Creative Commons: By Attribution 3.0

    Some photos are from Freepik and Pixabay.

""")





define build.name = "LabiosSalvajes"







define config.has_sound = True
define config.has_music = True
define config.has_voice = False















define config.main_menu_music = "music/main menu.mp3"










define config.enter_transition = dissolve
define config.exit_transition = dissolve




define config.intra_transition = dissolve




define config.after_load_transition = None




define config.end_game_transition = None
















define config.window = "auto"




define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)








default preferences.text_cps = 25





default preferences.afm_time = 15
















define config.save_directory = "LabiosSalvajes-1588094138"






define config.window_icon = "gui/window_icon.png"







init python:






















    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)
    build.classify('**.rpy', None)
    build.classify('**.docx', None)
    build.classify('**.txt', None)



    build.classify('game/**.png', 'archive')
    build.classify('game/**.jpg', 'archive')




    build.documentation('*.html')
    build.documentation('*.txt')
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
