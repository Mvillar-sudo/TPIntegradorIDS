// Ayudas de formularios. Son comodidades para el usuario: las validaciones
// reales se siguen haciendo en el servidor.

// 1) Confirmar antes de una acción destructiva.
//    Uso: agregar data-confirmar="mensaje" a un botón, link o <form>.
document.addEventListener('click', function (evento) {
	var elemento = evento.target.closest('a[data-confirmar], button[data-confirmar], input[data-confirmar]');
	if (elemento && !window.confirm(elemento.dataset.confirmar)) {
		evento.preventDefault();
	}
});

document.addEventListener('submit', function (evento) {
	var formulario = evento.target;
	if (formulario.dataset.confirmar && !window.confirm(formulario.dataset.confirmar)) {
		evento.preventDefault();
	}
});

// 2) Que "Repetir contraseña" coincida con "Contraseña".
//    Uso: un form con inputs #password y #password_confirm.
document.addEventListener('DOMContentLoaded', function () {
	var password = document.getElementById('password');
	var confirmacion = document.getElementById('password_confirm');
	if (!password || !confirmacion) {
		return;
	}

	function validarCoincidencia() {
		var mensaje = password.value === confirmacion.value ? '' : 'Las contraseñas no coinciden';
		confirmacion.setCustomValidity(mensaje);
	}

	password.addEventListener('input', validarCoincidencia);
	confirmacion.addEventListener('input', validarCoincidencia);
});
