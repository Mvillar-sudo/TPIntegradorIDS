(() => {
    const app = document.querySelector("#booking-app");
    if (!app || app.dataset.success === "true") return;

    const especialidad = document.querySelector("#specialty-select");
    const medico = document.querySelector("#doctor-select");
    const fecha = document.querySelector("#date-select");
    const horarios = document.querySelector("#time-grid");
    const mensaje = document.querySelector("#booking-message");
    const botonHorarios = document.querySelector("#to-schedule");
    const botonConfirmar = document.querySelector("#to-confirmation");
    const pasos = document.querySelectorAll("[data-panel]");
    const progreso = document.querySelectorAll("[data-progress]");

    let horarioSeleccionado = null;

    // La fecha mínima es el día de hoy.
    const hoy = new Date();
    fecha.min = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, "0")}-${String(hoy.getDate()).padStart(2, "0")}`;

    function mostrarMensaje(texto = "") {
        mensaje.textContent = texto;
        mensaje.hidden = !texto;
    }

    function cambiarPaso(numero) {
        pasos.forEach((paso) => paso.hidden = Number(paso.dataset.panel) !== numero);
        progreso.forEach((paso) => {
            const actual = Number(paso.dataset.progress);
            paso.classList.toggle("is-current", actual === numero);
            paso.classList.toggle("is-complete", actual < numero);
        });
        mostrarMensaje();
    }

    function limpiarHorarios(texto) {
        horarioSeleccionado = null;
        botonConfirmar.disabled = true;
        document.querySelector("#office-note").hidden = true;
        document.querySelector("#availability-count").textContent = "";

        const estado = document.createElement("p");
        estado.className = "empty-state";
        estado.textContent = texto;
        horarios.replaceChildren(estado);
    }

    async function consultar(url) {
        const respuesta = await fetch(url, { headers: { Accept: "application/json" } });
        const datos = await respuesta.json();
        if (!respuesta.ok) throw new Error(datos.error || "No se pudo completar la consulta.");
        return datos;
    }

    // Carga los médicos de la especialidad elegida.
    async function cargarMedicos() {
        medico.disabled = true;
        medico.replaceChildren(new Option("Cargando médicos...", ""));
        botonHorarios.disabled = true;
        limpiarHorarios("Elegí una fecha para consultar los horarios.");
        mostrarMensaje();

        if (!especialidad.value) {
            medico.replaceChildren(new Option("Primero elegí una especialidad", ""));
            document.querySelector("#doctor-hint").textContent = "La lista de médicos se filtra según la especialidad elegida.";
            return;
        }

        try {
            const url = new URL(app.dataset.medicosUrl, window.location.origin);
            url.searchParams.set("id_especialidad", especialidad.value);
            const medicos = await consultar(url);

            medico.replaceChildren(new Option("Seleccioná un médico", ""));
            medicos.forEach((item) => {
                medico.add(new Option(`${item.nombre_medico} ${item.apellido_medico}`, item.id_medico));
            });
            medico.disabled = medicos.length === 0;
            document.querySelector("#doctor-hint").textContent = medicos.length
                ? `${medicos.length} médico(s) disponible(s) en esta especialidad.`
                : "No hay médicos registrados para esta especialidad.";
        } catch (error) {
            medico.replaceChildren(new Option("No se pudieron cargar los médicos", ""));
            mostrarMensaje(error.message);
        }
    }

    // Consulta los turnos del médico para la fecha elegida.
    async function cargarHorarios() {
        limpiarHorarios("Buscando horarios disponibles...");
        if (!fecha.value) return;

        const url = new URL(app.dataset.disponiblesUrl, window.location.origin);
        url.searchParams.set("medico_id", medico.value);
        url.searchParams.set("id_especialidad", especialidad.value);
        url.searchParams.set("fecha", fecha.value);

        try {
            const turnos = await consultar(url);
            const disponibles = turnos.filter((turno) => turno.estado === "disponible");
            document.querySelector("#availability-count").textContent = disponibles.length
                ? `${disponibles.length} horario(s)`
                : "Sin disponibilidad";

            if (disponibles.length === 0) {
                limpiarHorarios("No hay horarios disponibles para este día. Probá con otra fecha.");
                document.querySelector("#availability-count").textContent = "Sin disponibilidad";
                return;
            }

            horarios.replaceChildren();
            disponibles.forEach((turno) => {
                const boton = document.createElement("button");
                boton.type = "button";
                boton.className = "time-option";
                boton.textContent = new Intl.DateTimeFormat("es-AR", {
                    hour: "2-digit", minute: "2-digit", hour12: false
                }).format(new Date(turno.fecha_hora));
                boton.addEventListener("click", () => seleccionarHorario(turno, boton));
                horarios.append(boton);
            });
        } catch (error) {
            limpiarHorarios(error.message);
        }
    }

    function seleccionarHorario(turno, boton) {
        horarioSeleccionado = turno;
        horarios.querySelectorAll(".time-option").forEach((opcion) => opcion.classList.remove("is-selected"));
        boton.classList.add("is-selected");
        botonConfirmar.disabled = false;
        document.querySelector("#office-doctor").textContent = turno.medico;
        document.querySelector("#office-name").textContent = turno.consultorio;
        document.querySelector("#office-note").hidden = false;
    }

    // Eventos para avanzar, volver y confirmar la reserva.
    especialidad.addEventListener("change", cargarMedicos);
    medico.addEventListener("change", () => {
        botonHorarios.disabled = !medico.value;
        limpiarHorarios("Elegí una fecha para consultar los horarios.");
    });
    fecha.addEventListener("change", cargarHorarios);

    botonHorarios.addEventListener("click", () => {
        document.querySelector("#selected-doctor-label").textContent =
            `${medico.selectedOptions[0].textContent} · ${especialidad.selectedOptions[0].textContent}`;
        cambiarPaso(2);
        fecha.focus();
        if (fecha.value) cargarHorarios();
    });

    document.querySelector("#back-to-professional").addEventListener("click", () => cambiarPaso(1));
    document.querySelector("#back-to-schedule").addEventListener("click", () => cambiarPaso(2));

    botonConfirmar.addEventListener("click", () => {
        if (!horarioSeleccionado) return;

        document.querySelector("#summary-specialty").textContent = horarioSeleccionado.especialidad;
        document.querySelector("#summary-doctor").textContent = horarioSeleccionado.medico;
        document.querySelector("#summary-office").textContent = horarioSeleccionado.consultorio;
        document.querySelector("#summary-datetime").textContent = new Intl.DateTimeFormat("es-AR", {
            dateStyle: "full", timeStyle: "short"
        }).format(new Date(horarioSeleccionado.fecha_hora));
        document.querySelector("#selected-turno-id").value = horarioSeleccionado.id_turno;
        cambiarPaso(3);
    });
})();