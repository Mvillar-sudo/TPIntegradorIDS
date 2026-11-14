/*
 * Escáner de QR con la cámara para la pantalla de recepción.
 *
 * Qué hace: prende la cámara, busca un código QR en el video y, cuando lo
 * encuentra, escribe el texto en el campo "token_qr" y envía el formulario
 * de siempre (POST /recepcion/checkin). No hace ningún pedido al backend
 * desde el navegador: toda la comunicación sigue pasando por Flask + requests.
 *
 * Requisitos: jsQR cargada antes (static/js/jsQR.js) y que la página se abra
 * desde localhost o https (los navegadores no dejan usar la cámara si no).
 *
 * Es un módulo (<script type="module">): nada de lo que se declara acá queda
 * como variable global de la página. El estado se guarda en el propio <video>
 * (video.srcObject es la cámara prendida) en vez de en variables sueltas.
 */

const MILISEGUNDOS_ENTRE_LECTURAS = 150;


/*
Pre: la página tiene los elementos con id boton_camara, camara_video,
     camara_lienzo, camara_estado, camara_marco y token_qr.
Post: Devuelve un objeto con esos elementos del DOM.
*/
function obtenerElementos() {
    return {
        boton: document.getElementById('boton_camara'),
        video: document.getElementById('camara_video'),
        lienzo: document.getElementById('camara_lienzo'),
        estado: document.getElementById('camara_estado'),
        marco: document.getElementById('camara_marco'),
        campo: document.getElementById('token_qr'),
    };
}


/*
Pre: 'mensaje' es un texto; 'esError' es true/false.
Post: Muestra el mensaje debajo del botón (en rojo si es un error).
*/
function mostrarEstado(mensaje, esError) {
    const { estado } = obtenerElementos();
    estado.textContent = mensaje;
    estado.style.color = esError ? '#c0392b' : '';
}


/*
Pre: 'error' es el error que devolvió getUserMedia.
Post: Devuelve un texto en castellano que explica qué pasó y qué hacer.
*/
function mensajeDeErrorDeCamara(error) {
    const mensajes = {
        NotAllowedError: 'No diste permiso para usar la cámara. Habilitalo en el candado de la barra de direcciones o cargá el código a mano.',
        NotFoundError: 'No se encontró ninguna cámara en este dispositivo. Cargá el código a mano.',
        NotReadableError: 'La cámara está siendo usada por otra aplicación. Cerrala e intentá de nuevo.',
    };
    return mensajes[error.name] || 'No se pudo prender la cámara. Cargá el código a mano.';
}


/*
Pre: -
Post: Apaga la cámara (si estaba prendida), esconde el video y deja el botón
      listo para volver a escanear.
*/
function detenerCamara() {
    const { boton, video, marco } = obtenerElementos();
    if (video.srcObject) {
        for (const pista of video.srcObject.getTracks()) {
            pista.stop();
        }
        video.srcObject = null;
    }
    marco.hidden = true;
    boton.textContent = 'Escanear con la cámara';
}


/*
Pre: 'texto' es el contenido del QR leído.
Post: Apaga la cámara, escribe el texto en el campo token_qr y envía el
      formulario (el mismo POST que si lo hubieran escrito a mano).
*/
function enviarCodigoLeido(texto) {
    const { campo } = obtenerElementos();
    detenerCamara();
    campo.value = texto.trim();
    campo.form.submit();
}


/*
Pre: -
Post: Si hay un QR en el cuadro actual del video lo envía; si no, se vuelve
      a llamar sola dentro de unos milisegundos. Corta cuando la cámara se apaga.
*/
function leerCuadro() {
    const { video, lienzo } = obtenerElementos();
    if (!video.srcObject) {
        return;
    }

    if (video.readyState === video.HAVE_ENOUGH_DATA && video.videoWidth > 0) {
        lienzo.width = video.videoWidth;
        lienzo.height = video.videoHeight;
        const contexto = lienzo.getContext('2d', { willReadFrequently: true });
        contexto.drawImage(video, 0, 0, lienzo.width, lienzo.height);
        const imagen = contexto.getImageData(0, 0, lienzo.width, lienzo.height);
        const codigo = jsQR(imagen.data, imagen.width, imagen.height, {
            inversionAttempts: 'dontInvert',
        });
        if (codigo && codigo.data) {
            enviarCodigoLeido(codigo.data);
            return;
        }
    }

    setTimeout(leerCuadro, MILISEGUNDOS_ENTRE_LECTURAS);
}


/*
Pre: -
Post: Pide permiso, prende la cámara trasera (o la que haya) y empieza a
      buscar el QR. Si algo falla muestra el motivo y deja el formulario manual.
*/
async function iniciarCamara() {
    const { boton, video, marco } = obtenerElementos();

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        mostrarEstado('Este navegador no permite usar la cámara en esta dirección (hace falta localhost o https). Cargá el código a mano.', true);
        return;
    }

    try {
        video.srcObject = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' },
            audio: false,
        });
    } catch (error) {
        mostrarEstado(mensajeDeErrorDeCamara(error), true);
        return;
    }

    marco.hidden = false;
    boton.textContent = 'Apagar cámara';
    mostrarEstado('Apuntá la cámara al QR del paciente…', false);
    await video.play();
    leerCuadro();
}


/*
Pre: -
Post: Si la cámara está prendida la apaga; si está apagada la prende.
*/
async function alternarCamara() {
    const { video } = obtenerElementos();
    if (video.srcObject) {
        detenerCamara();
        mostrarEstado('', false);
    } else {
        await iniciarCamara();
    }
}


/*
Pre: -
Post: Conecta el botón con la cámara y apaga la cámara si el usuario se va de la página.
*/
function configurarEscaner() {
    const { boton } = obtenerElementos();
    boton.addEventListener('click', alternarCamara);
    window.addEventListener('pagehide', detenerCamara);
}


configurarEscaner();
