label clarence_prologo:
    "Prólogo"
    pause 2
    scene callejon with dissolve
    play music "sounds/calle.mp3"
    "La noche se cierne sobre ti mientras ocultas tu rostro en la capucha de tu chaqueta."
    "El frío consigue colarse por cada agujero, dejando que enfríe tu piel hasta el punto en el que te da un escalofrío."
    "Las estrellas no son visibles, la contaminación lumínica te lo impide."
    "Tampoco te importa, estás en un callejón oscuro. Lo último que quieres es mirar las estrellas estando en peligro."
    "Mientras caminas, unas pisadas tras de ti aceleran tu pulso."
    "¿Un ladrón? ¿Un asesino? Sea lo que sea, no quieres tener nada que ver."
    oc "Tal vez si corro no me pille a tiempo y llegue a una calle atestada de gente."
    oc "O puede que la suerte no esté de mi parte."
    "Te das la vuelta para ver si de verdad es algo peligroso."
    "La sombra de un individuo se detiene delante de ti, sin poder matener el equilibrio."
    oc "Tal vez sea un borracho."
    oc "\"Señor, ¿se encuentra bien?\""
    "Camina para intentar llegar a ti."
    play music "music/all_this.mp3"
    "Te das cuenta que se dirige a ti, por lo que te intentas alejar."
    "Cada paso que da hace que tu corazón saboree la adrenalina que corre por tus venas."
    "No entiendes sus intenciones, pero crees que quiere atacarte, robarte... Matarte."
    oc "Tengo que irme de aquí. ¡Tengo que ponerme a correr por mi vida!"
    "Tus ojos visualizan una navaja salir de su bolsillo que dispara un brillo por la luz artificial."
    "Y una sonrisa perlada en toda la oscuridad."
    oc "¡Tengo que irme ya mismo!"
    "Sin perder ni un segundo más, das media vuelta y empiezas a correr."
    play sound "sounds/correr.mp3"
    "Escuchas sus pisadas tomando la carrera de tu vida como un desafío, como si estuvieran jugando al pilla pilla."
    "La adrenalina te ayuda, el cansancio no es un problema. Es un aliado poderoso."
    stop sound
    scene callepeligrosa with dissolve
    "Salís del callejón y entráis a una zona urbana poco habitada."
    "Una calle de mala muerte y llena de vagabundos calentando sus manos en el típico bidón oxidado."
    "Los ladrones son menos peligrosos que el que te sigue. Al menos sus intenciones son claras."
    "Te encuentras con algunos vagabundos que no pueden ayudarte. Ninguno puede en estos momentos."
    "Una rápida mirada atrás y ves cómo el cuerpo, que antes se tambaleaba, ahora se mueve con agilidad. Está ganando distancia poco a poco."
    oc "Esto no puede ir peor."
    show clarence with dissolve
    "Giras una esquina más y ves otra figura a lo lejos. Al principio no se da cuenta de tu presencia, pero cuando lo hace..."
    show clarence nervios
    "...nota lo que ocurre."
    hide clarence nervios with dissolve
    "Se da la vuelta mientras te hace una señal para que le sigas."
    "Corre contigo, pero no siente tu mismo miedo."
    "Te agarra de la mano y entráis en un local que estaba a punto de cerrar."
    scene bg negro with dissolve
    "La persiana metálica va bajando, pero una mano la detiene con fuerza."
    oc "¡Joder! ¡¿Es un robot o qué?!"
    "El chico, sin soltarte de la mano, te lleva a otra puerta mientras grita."
    "???" "\"¡Jefe! ¡Un intruso!\""
    stop music fadeout 2.0
    "Cierra detrás de vosotros y te mantiene cerca, esperando algo o alguien."
    "???" "\"¿Estás bien?\""
    show clarence with dissolve
    "Levantas la mirada para poder verle bien."
    "Un husky se postra delante de ti, sonriendo tímidamente."
    oc "\"Y-Yo... Gracias.\""
    show clarence habla
    "???" "\"Aún no ha acabado. Esperemos un momento, mi jefe debe de estar lidiando con el problema.\""
    show clarence
    "No habláis, el silencio es atroz. Cada segundo que pasa te parece eterno."
    "La adrenalina se va de tu cuerpo y sientes el cansancio. Tu cuerpo tiembla sin parar."
    "El husky te acerca a él y te abraza."
    show clarence habla
    "???" "\"Tranquilo, todo irá bien. Ya verás.\""
    show clarence
    "La timidez se va de su rostro. Una sonrisa cálida es lo que queda."
    show clarence habla
    "???" "\"Un abrazo siempre ayuda a calmar los nervios. ¿Te sientes mejor?\""
    show clarence
    "Es ligeramente más alto que tú, también más ancho. Su abrazo te calienta."
    "Asientes con la cabeza, no tienes palabras. O más bien estás demasiado cansado como para articular palabra."
    show clarence habla
    c "\"Me llamo Clarence. ¿Y tú?\""
    show clarence
    oc "\"[name].\""
    "Sueltas sin fuerza."
    show clarence habla
    c "\"Ya verás que todo irá bien. Mi jefe da mucho miedo, seguro que asusta al intruso.\""
    show clarence
    "Un par de minutos más tarde, se oyen un par de toques a la puerta."
    scene zonaprivada with dissolve
    show mantar with dissolve:
        xalign 0.1
    show clarence with dissolve:
        xalign 0.9
    "Al salir, te encuentras con un cocodrilo y una rata."
    "El cocodrilo es quien parece más amenazante. Una cicatriz recorre su ojo izquierdo sin dañarlo, parte del puente de su nariz hasta acabar en su labio inferior."
    oc "Dios mío... ¿Qué le ha ocurrido?"
    "Sus ojos esmeralda te miran, atravesando tu alma."
    "???" "\"¿Quién es este?\""
    show clarence habla
    c "\"[name]. No parece ser de por aquí.\""
    show clarence
    "???" "\"Porque no lo es.\""
    show clarence habla
    c "\"Gracias por encargarse del problema.\""
    show clarence
    "???" "\"Ya me lo contarás todo mañana. Quiero detalles.\""
    hide mantar with dissolve
    show clarence with ease:
        xalign 0.5
    "Asiente y el cocodrilo se aleja junto con la rata."
    show clarence habla
    c "\"Muy bien, ¿dónde vives?\""
    show clarence
    oc "\"¿Eh?\""
    show clarence nervios
    c "\"Oh, perdona... Debes de estar muy cansado. Deja que te traiga un zumo. Eso te ayudará.\""
    c "\"O eso espero.\""
    show clarence
    "Se va un momento y vuelve con un cartón de zumo, el cual ya tiene una pajita clavada."
    "Te lo entrega y empiezas a beber."
    show clarence habla
    c "\"¿Nos vamos? Iré a tu ritmo.\""
    scene bg negro with dissolve
    pause 2
    scene callepeligrosa with dissolve
    play music "sounds/calle.mp3"
    "Empezáis a caminar y lo único que haces es mirar a tu alrededor de forma frenética, con miedo a que el sujeto aún siga cerca."
    oc "La forma en la que se movía, la fuerza con la que detuvo la puerta metálica..."
    oc "Me da escalofríos solo de pensar en lo que me habría hecho si hubiese puesto una mano en mí."
    show clarence with dissolve
    "Clarence se da cuenta de tu nerviosismo."
    show clarence habla
    c "\"No tengas miedo. Estas calles no son seguras, pero cuando mi jefe me deja ir así como tal, significa que no me ocurrirá nada.\""
    c "\"Siempre he mantenido ese pensamiento y no me ha pasado nada. ¿Por qué no haces lo mismo?\""
    c "\"Vamos, respira conmigo. Respira... Expira.\""
    show clarence
    "Te ayuda a relajarte, a mantener la calma. Puede que el pensamiento no signifique lo mismo para ti, pero es una excusa para seguir adelante sin miedo."
    "Buscas un cubo de basura cualquiera para tirar el cartón de zumo."
    show clarence habla
    c "\"Dámelo, lo tiraré por ti más tarde.\""
    show clarence
    "Se lo entregas. Cada palabra que suelta te calma."
    show clarence habla
    c "\"Ahora que te miro tranquilamente, sí que no eres de estos barrios.\""
    c "\"¿Cómo has acabado por aquí? ¿Dónde te encontraste con ese asesino? ¿Por dónde hay que ir para tu casa?\""
    show clarence
    oc "\"Aah... No lo sé.\""
    show clarence nervios
    c "\"Claro, nunca has pasado por aquí, por lo que estás en terreno desconocido.\""
    show clarence habla
    c "\"Tampoco es que sea muy complicado, ya verás que pasando un par de veces acabarás memorizando cada esquina.\""
    show clarence risa
    c "\"Como el gimnasio en el que acabamos de estar. Es donde trabajo. Más bien por la noche. Qué suerte de que la puerta no estuviera cerrada.\""
    show clarence
    oc "Madre mía, habla bastante. No me molesta, más bien me sorprende. Acabamos de pasar por un momento difícil y no se le acaban las palabras."
    oc "También es muy curioso. Quiere saber todo lo que ocurrió."
    "El camino de vuelta pasa rápido gracias a la conversación que te da el husky."
    "Estáis cerca de tu edificio, por lo que le detienes."
    oc "\"Vivo a una calle de distancia.\""
    show clarence habla
    c "\"Oh, ¿qué edificio? Hay tantos con docenas de pisos... ¿Vives en uno que se vea toda la ciudad? Debe de ser muy guay.\""
    show clarence
    "Le señalas el tuyo. Te deja ir con una cálida sonrisa."
    hide clarence with dissolve
    "Te das la vuelta para mirarle. Su cola se mueve con tal fuerza que va a formar una ventisca."
    "Sonríes al haber conocido a un husky parlanchín tan amigable."
    "Con la tranquilidad que te da llegar sano y salvo a tu edificio, entras y te acuestas. El cansancio aún sigue peleando."
    stop music fadeout 2.0
    scene bg negro with dissolve
    pause 2
    jump clarence_capitulo1
return
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
