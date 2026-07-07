init python:
    thumbnail_x = 400
    thumbnail_y = int(thumbnail_x * 0.5625)
    g = Gallery()


    g.button("tiger_prologo")
    g.unlock_image("tiger_prologo")

    g.button("tiger_dia6")
    g.unlock_image("tiger_dia6")


    g.button("presodal_dia2")
    g.unlock_image("presodal_dia2")

    g.button("presodal_dia5")
    g.unlock_image("presodal_cap8_noche1")
    g.unlock_image("presodal_cap8_noche2")
    g.unlock_image("presodal_cap8_noche3")
    g.unlock_image("presodal_cap9_manana1")
    g.unlock_image("presodal_cap9_manana3")


    g.button("marcos_dia2")
    g.unlock_image("marcos_dia2")

    g.button("marcos_dia3")
    g.unlock_image("marcos_dia3_1")
    g.unlock_image("marcos_dia3_2")
    g.unlock_image("marcos_dia3_3")
    g.unlock_image("marcos_dia3_4")

    g.button("marcos_dia5")
    g.unlock_image("marcos_dia4")

    g.button("marcos_dia5")
    g.unlock_image("marcos_dia5_1")
    g.unlock_image("marcos_dia5_2")
    g.unlock_image("marcos_dia5_3")


    g.button("clarence_dia3")
    g.unlock_image("clarence_dia3_banio")


    g.button("alexq_1")
    g.image("alexq_1")

    g.button("haslord_1")
    g.image("haslord_1")

    g.button("haslord2_1")
    g.image("haslord2_1")
    g.image("haslord2_2")
    g.image("haslord2_3")
    g.image("haslord2_4")
    g.image("haslord2_5")
    g.image("haslord2_6")

    g.button("orebcobosrojas_1")
    g.image("orebcobosrojas_1")

    g.button("kaisanzang_1")
    g.image("kaisanzang_1")

    g.button("lucartss_1")
    g.image("lucartss_1")

    g.button("lilardo_1")
    g.image("lilardo_1")
    g.image("lilardo_2")
    g.image("lilardo_3")

    g.button("hfz")
    g.image("hfz")

    g.button("lobus")
    g.image("lobus")

    g.button("pyrusk")
    g.image("pyrusk")

    g.transition = dissolve
    g.locked_button = im.Scale("images/menu_cgs/locked.png",thumbnail_x,thumbnail_y)

screen cg_galeria:
    tag menu


    vbox:
        style_prefix "gallery_nav"
        null height 130
        imagebutton auto "images/menu_cgs/tiger_%s.png" action Show("galeria_tiger")
        imagebutton auto "images/menu_cgs/presodal_%s.png" action SetScreenVariable("cg_page_tiger", 2)
        imagebutton auto "images/menu_cgs/marcos_%s.png" action SetScreenVariable("cg_page_tiger", 3)
        imagebutton auto "images/menu_cgs/darius_%s.png" action SetScreenVariable("cg_page_tiger", 4)
        imagebutton auto "images/menu_cgs/clarence_%s.png" action SetScreenVariable("cg_page_tiger", 5)
        imagebutton auto "images/menu_cgs/fanarts_%s.png" action SetScreenVariable("cg_page_tiger", 6)
        imagebutton auto "images/menu_cgs/others_%s.png" action SetScreenVariable("cg_page_tiger", 7)
        imagebutton auto "images/menu_cgs/back_%s.png" action ShowMenu ("galeria")

style gallery_nav_vbox:
    xalign 0.015
    yalign 0.5
    spacing 15

screen galeria_tiger:
    tag menu

    default cg_page_tiger = 1
    add "images/menu_cgs/GAL"+str(cg_page_tiger)+".png" alpha 1.0
    use cg_galeria
    viewport:
        child_size (1920, 1800)
        mousewheel True
        draggable True
        arrowkeys True
        pagekeys True

        yinitial 0




        has vbox
        xsize 1920
        xalign 1.0

        null height 175


        showif cg_page_tiger == 1:
            grid 3 4:
                xalign 0.855
                spacing 50

                add g.make_button("tiger_prologo", im.Scale("images/cgs/tiger_prologo.png",400,225), idle_border="gallery_idle")

        showif cg_page_tiger == 2:
            grid 3 3:
                xalign 0.855
                spacing 50
                add g.make_button("presodal_dia2", im.Scale("images/cgs/presodal_dia2.png",400,225), idle_border="gallery_idle")
                add g.make_button("presodal_dia5", im.Scale("images/cgs/presodal_dia5_noche1.png",400,225), idle_border="gallery_idle")

        showif cg_page_tiger == 5:
            grid 3 3:
                xalign 0.855
                spacing 50
                add g.make_button("clarence_dia3", im.Scale("images/cgs/clarence_dia3_banio.png",400,225), idle_border="gallery_idle")

        showif cg_page_tiger == 6:
            grid 3 4:
                xalign 0.855
                spacing 50
                add g.make_button("alexq_1", im.Scale("images/fanarts/alexq_1.png",400,225), idle_border="gallery_idle")
                add g.make_button("haslord_1", im.Scale("images/fanarts/haslord/haslord_1.png",400,225), idle_border="gallery_idle")
                add g.make_button("haslord2_1", im.Scale("images/fanarts/haslord/haslord2_1.png",400,225), idle_border="gallery_idle")
                add g.make_button("orebcobosrojas_1", im.Scale("images/fanarts/orebcobosrojas_1.png",400,225), idle_border="gallery_idle")
                add g.make_button("kaisanzang_1", im.Scale("images/fanarts/kaisanzang_1.png",400,225), idle_border="gallery_idle")
                add g.make_button("lucartss_1", im.Scale("images/fanarts/lucartss_1.png",400,225), idle_border="gallery_idle")
                add g.make_button("lilardo_1", im.Scale("images/fanarts/luiseduardo/lilardo_1.png",400,225), idle_border="gallery_idle")
                add g.make_button("hfz", im.Scale("images/fanarts/hfz.png",400,225), idle_border="gallery_idle")
                add g.make_button("lobus", im.Scale("images/fanarts/lobus.png",400,225), idle_border="gallery_idle")
                add g.make_button("pyrusk", im.Scale("images/fanarts/pyrusk.png",400,225), idle_border="gallery_idle")








        null height 60
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
