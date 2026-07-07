label presodal_prologo:
    "Prólogo"
    scene callejon with dissolve
    play music "sounds/calle.mp3"
    "La noche se cierne sobre ti mientras ocultas tu rostro en la capucha de tu chaqueta."
    "El frío consigue colarse por cada agujero, dejando que enfríe tu piel hasta el punto en el que te da un escalofrío"
    "Las estrellas no son visibles gracias a la contaminación lumínica."
    "Tampoco te importa, estás en un callejón algo oscuro. Lo último que quieres es mirar las estrellas estando en peligro."
    "Mientras caminas, unas pisadas tras de ti aceleran tu pulso."
    "¿Un ladrón? ¿Un asesino? Sea lo que sea, no quieres tener nada que ver."
    oc "Tal vez si corro no me pille a tiempo y llegue a una calle llena de gente"
    oc "O puede que la suerte no esté de mi parte."
    "Igual te das la vuelta para ver si de verdad es alguna opción pensada."
    "Te encuentras con una sombra que se tambalea."
    oc "\"Señor, ¿se encuentra bien?\""
    "Camina para intentar llegar a ti."
    play music "music/all_this.mp3"
    "Te das cuenta de ello y vas caminando para atrás."
    "Cada paso que da hace que tu corazón saboree la adrenalina que corre por tus venas."
    "Ese hombre quiere un pedazo de ti. Quiere lo que llevas encima."
    oc "Tengo que irme de aquí. ¡Tengo que ponerme a correr por mi vida!"
    "Tus ojos visualizan una navaja salir de su bolsillo que dispara un brillo por la luz artificial."
    oc "¡Tengo que irme ya mismo!"
    "Sin perder ni un segundo más, das media vuelta y empiezas a correr."
    play sound "sounds/correr.mp3"
    "Escuchas sus pisadas tomando la carrera de tu vida como un desafío, como si estuvieran jugando al pilla pilla."
    "La adrenalina te ayuda a no notar el cansancio. Un aliado poderoso en este momento tan importante."
    stop sound
    scene callepeligrosa with dissolve
    "Salís del callejón y entráis a una zona urbana poco habitada."
    "Una calle de mala muerte y llena de vagabundos calentando sus manos en el típico bidón oxidado."
    "Los ladrones son aún más peligrosos que el que te sigue y matan por cualquier motivo."
    "Te encuentras con algunos vagabundos que no pueden ayudarte. Ninguno puede en estos momentos."
    "Sigues corriendo, teniendo cuidado de no tropezarte con los muchos baches y grietas que hay."
    "A lo lejos puedes entrever una luz muy brillante. Crees que es una cafetería, pues no logras ver con claridad."
    "Pierdes distancia, el asesino está a punto de pillarte. Poco a poco llegas a esa luz."
    "Unos pocos pasos más y llegas a la puerta, abres y entras."
    scene restaurante with dissolve
    "Justo después, te tropiezas y caes de bruces contra el suelo. Te das la vuelta para verle, atravesando la puerta con el cuchillo en alto."
    "Te esfuerzas por echarte atrás, pero te topas con la barra del local."
    stop music fadeout 2.0
    "Cuando crees que no puede ir a peor, te das cuenta de que se detiene al instante."
    "Una sombra se proyecta en tus pies. Miras encima de ti."
    "El cañón de una escopeta."
    "Un dedo listo en el gatillo."
    "???" "\"Tienes dos opciones: salir de mi local o salir en las noticias. Tú eliges.\""
    "Una voz masculina le amenaza."
    "Se echa atrás poco a poco, levantando las manos en señal de rendición."
    "Cierra la puerta y se larga a toda prisa."
    oc "Joder... Dios mío."
    "El cañón desaparece. En su lugar, un rostro serio aparece."
    show presodal serio habla with dissolve
    "???" "\"¿Estás bien?\""
    show presodal serio
    "No tienes palabras ahora mismo. La adrenalina se ha ido y con ello viene el cansancio."
    "Una lágrima resbala por tu mejilla."
    "Ese rostro desaparece por un segundo para ir al otro lado de la barra."
    "Ante ti aparece un tigre de apariencia llamativa. Como si hubieras entrado a un restaurante caro."
    show presodal habla
    "???" "\"Ven.\""
    show presodal
    play music "music/bensound-sadday.mp3"
    "Te ofrece su mano. No dudas en aceptarlo, pues te ha salvado la vida."
    oc "\"G-Gracias.\""
    show presodal habla
    "???" "\"No hay de qué.\""
    show presodal
    "Te pone en uno de los taburetes para que descanses."
    show presodal habla
    "???" "\"Deja que te traiga algo. Te ayudará a calmarte.\""
    hide presodal habla with dissolve
    "Asientes y se va por una puerta."
    "Tus ojos solo van a tus manos, temblando sin parar tras la experiencia."
    oc "¿Dónde estoy? ¿Por qué tuve que pasar por esa calle?"
    "Observas tu alrededor. Un local ambientado en los años ochenta o eso crees."
    "No te parece malo, pero es un poco extraño tenerlo en estas calles."
    "Mientras recuperas el aliento, otra persona aparece por otra puerta."
    show tiger with dissolve
    "Otro tigre. Este parece tener menos paciencia."
    show tiger habla
    "???" "\"¡Presodal! ¡Un cliente!\""
    show tiger with ease:
        xalign 0.9
    show presodal with dissolve:
        xalign 0.1
    "El recién nombrado aparece con un vaso. Lo pone delante de ti y agarra tus manos para ponerlas alrededor de este."
    "Sientes el calor invadir tu cuerpo, aliviar tus emociones."
    show tiger habla
    "???" "\"¿Me he perdido algo?\""
    show tiger
    show presodal habla
    p "\"Mientras tú estabas en el baño, alguien ha intentado matar a este chico.\""
    show presodal
    show tiger habla
    "???" "\"Ah, pues vale.\""
    show tiger
    "Delante de él hay un plato, el cual está a medio terminar."
    show presodal serio habla
    p "\"Tan insensible como siempre, Tiger.\""
    show presodal serio
    "Se encoge de hombros."
    "El olor te da a entender que es chocolate caliente. No puedes aguantar en darle un sorbo."
    show presodal habla
    p "\"¿Cómo has acabado en esta situación?\""
    show presodal
    "Te dedica una sonrisa. Estás a salvo."
    oc "\"Yo...\""
    "Le explicas todo lo que ha ocurrido. Solo fueron cinco minutos de acción, pero sientes que fueron horas."
    "Ya no sientes tus manos temblar. El calor y el dulce sabor del chocolate te han ayudado."
    show presodal triste
    p "\"Pobre chaval.\""
    "Mira al otro tigre."
    show presodal serio habla
    p "\"¿Puedes hacerme el favor de llevarlo a un lugar seguro?\""
    show presodal serio
    show tiger habla
    t "\"No puedo.\""
    show tiger
    "Señala su plato."
    show presodal serio habla
    p "\"¿En serio vas a ser así? ¿Al menos podrías quedarte montando guardia mientras lo llevo?\""
    show presodal serio
    show tiger habla
    t "\"¿Gano algo?\""
    show tiger
    show presodal serio habla
    p "\"Una cena gratis.\""
    show presodal serio
    show tiger habla
    t "\"Me quedaré.\""
    show tiger
    show presodal serio habla
    p "\"Menudo cabrón.\""
    show presodal serio
    "Terminas el chocolate y Presodal espera en la entrada por ti."
    scene bg negro with dissolve
    "Una vez en la calle, se pone a tu lado, preguntándote la dirección a la que te dirigías."
    scene callecasa with dissolve
    show presodal with dissolve
    "Pasan unos minutos y acabáis llegando a una calle segura, cerca de tu edificio."
    show presodal habla
    p "\"Deberías tener cuidado de por dónde vas. Los barrios bajos no son para todo el mundo, y menos de noche.\""
    show presodal
    oc "\"¿Eso eran los barrios bajos?\""
    "Asiente con la cabeza."
    oc "\"Siento haberte dado problemas.\""
    show presodal habla
    p "\"No hay problema que una escopeta no pueda solucionar.\""
    show presodal
    oc "Discrepo rotundamente."
    oc "\"Gracias por salvarme la vida, señor Presodal.\""
    show presodal habla
    p "\"Con Presodal basta, señorito...\""
    show presodal
    oc "\"[name].\""
    show presodal habla
    p "\"[name]...\""
    show presodal guinio
    p "\"Si vuelves a estar en problemas y mi restaurante está cerca, ya sabes a dónde ir.\""
    show presodal
    oc "\"Lo haré. Será mejor que me vaya.\""
    hide presodal with dissolve
    "Presodal se da la vuelta para volver al restaurante, mientras que tú te quedas ahí parado."
    "Es hora de volver a casa. Pero piensas que tal vez lo volverás a ver, tarde o temprano."
    "¿Pero qué ocurrirá entre vosotros?"
    scene bg negro with dissolve
    stop music fadeout 2.0
    pause 2
    jump presodal_capitulo1
return
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
