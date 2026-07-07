screen patreon():
    tag menu


    add "images/fondos/dormitorio_noche.png"
    add "black":
        alpha 0.7

    viewport:
        child_size (1920, 2400)
        mousewheel True
        draggable True
        arrowkeys True
        pagekeys True

        yinitial 0

        has fixed
        xsize 1920

        vbox:
            xsize 1500
            xalign 0.5
            spacing 30

            null height 0

            hbox:
                add im.Scale("images/menu_galeria/writers_corner.png", 1500, 150):
                    alpha 0.8

            hbox:
                xsize 1200
                xalign 0.5
                add im.Scale("images/patreons/alexheadshot.png", 230, 230) xalign 0.1
                add im.Scale("images/patreons/foxalpha_headshot.png", 230, 230) xalign 1/3
                add im.Scale("images/patreons/smokey_headshot.png", 230, 230) xalign 2/3
                add im.Scale("images/patreons/placeholder.png", 230, 230) xalign 3/3

            hbox:
                xsize 1200
                xalign 0.5
                text "Camosomi" xalign 0.2:
                    color "#992eb4"
                text "Fox Alfa 3321" xalign 0.1:
                    color "#f06d16"
                text "Smokey" xalign 0.1:
                    color "#999999"
                text "{font=fonts/NotoSansSC-VariableFont_wght.ttf}更鸟 知{/font}" xalign 0.55:
                    color "#999999"

            hbox:
                add im.Scale("images/menu_galeria/gentle_fur.png", 1500, 150):
                    alpha 0.8

            hbox:
                text "barrel, Logan, Aldof, Arxwel, Danish, Ma'Levi, Tomas, CMP, David B Gardner, El Cheeto, jenny Andersson, Kenar, Xero, Curry, Jogaro, Neck, Elvarg, arnau gisbert":
                    color "#999999"

            hbox:
                add im.Scale("images/menu_galeria/tough_past.png", 1500, 150):
                    alpha 0.8

            hbox:
                text "Davy Bogaerts, Pale leaves, Rich Anthony, San, Sparky85, Taryx, TaylorsBrand, VampyrëanFox, abigdeliciouspotato, ADripOfVioletTea, Akimaki, Allowingsoup99, Ari, asdddew, Banjo K!, Buckest{font=fonts/NotoSansSC-VariableFont_wght.ttf}飞{/font}, Carrot, Celt, Dakari Ruth, David G, DeeDee, Deyon Whittaker, dobber, Electromat, Ellipsis, EtherealHex, Exoticsaw, Fallen_Sky3, Fenrir Hróðvitnir, FirstGuard, Gamesir 2474, Gauß, Guillian Develotte, Hasturs, Hexster, Ivan, John Wolfen, Josh Myers, K123098, Kevin Carlos Gomez, Khefu, Kytheon Iora, lobus okami, Maurice Beacham, Mehmeh, Melkaia, MetaMan, Mikey!, mmd, MnJuel, muecsoy, Möbiusparasite, naoirou, NicelCe, NikTikhonov, Non Non, omndragon, Ozranon, pat, Pierre-René Michel, Rarruk, Ren, Ronnek, Sfeei, shiro milkooo, Smokey, Sr.Bejarano, Stephan Nitz, TheHWolf94, Tororo, Trenchino, Wolf_dragon_lover, wu yixuan, Yago, Yuki, Zokny-chan, Александр Гутников, alec nye, Ben, Berlyn, Bob Hiroshi, Coatl, cookie wookie, Daal, Darki, Davepreet, Delusion D, Douglas alves, Edward, Elvarg, floof, Gabriel Santos, Grey Wolf, hjk, Illindar, Jack, Jacob Slocum, JamBam, Lazy Whitetiger, Max Freeman, Maximos, Mikkeke, Mono Shiron, Nightfall, P5YCH0, peter hiro, Phoenix94, ranshin, RedUsic, Reinoscope, Ronzellcool, Rygalt, Sparki, stolid_the_artist Aka, Thasar, the406traveler, Tiger Cub, Tsukimi ypop, yeolvi, zhou weishun, zulu3456, ulquiorra cifer, BEKENEKO OGM, P5YCHO, arnut2020, Cofo, ToHh, Zen, solute, darien barnes, Trashcan, Benjamin Lacroix, David Vaughan, Dreamyyy, Valor, Luigi dellano, SamTheeArisen, Argentcoyote, Wusabi, DentedHead, Rorrry, ChesterKain, Starfall, Esklon Kaine, Leonardo Daniel Urbina Rios, James Cooper Hitchcock, Merocles, Mancado, CodeTiger, lilardo caballero, ameno uwu, Patrik Subic, Lee LKO, Debil, Timtomate, Xhua Evans, Dreki, Lumble":
                    color "#999999"

            hbox:
                add im.Scale("images/menu_galeria/lovely_waiter.png", 1500, 150):
                    alpha 0.8

            hbox:
                text "1794580401, Astus1ake, Baka, CyanCosmic, Diego, DJayreal, El1_, ENRIQUE TAJIMAROA, Haruto, inuta, Jammy Dox, Jayme Salazar, John Murphy, John Taylor, joson1681, jovuan Jackson, Konrad, Kuma, Logan Junior, mrtt71, Nelson Cabrera, Norbert Dudzik, Rabby, Sol-hunter, TerribleLeon, The Orange Cow, TrueLegend807, Tyrun Bratts, Woof, Yosu Garcia Izquierdo, z0Mbieuwu, {font=fonts/NotoSansSC-VariableFont_wght.ttf}度飞 林{/font}, Klazzy135, Leo Owen, Nathanciel, Peete, Retsu, loboblanco YT, Zachary Ross, Felipe Moreira, Juanpa":
                    color "#999999"

    imagebutton idle im.Scale("images/menu_galeria/volver.png", 200,50) xalign 0.001 ypos 940 action ShowMenu("galeria")
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
