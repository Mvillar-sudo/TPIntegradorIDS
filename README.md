# TPIntegradorIDS

Sistema de turnos médicos con check-in por QR (Centro Médico Salud Integral).
Backend y frontend en Flask, base de datos MySQL con SQL escrito a mano (sin ORM).

## Cómo correr el backend

1. Crear el entorno e instalar dependencias (desde la carpeta principal): `source init.sh`
2. Copiar `.env.example` como `.env` y completar los valores (base de datos, `JWT_SECRET_KEY`, mail).
3. Crear la base con los datos de prueba: `mysql -u TU_USUARIO -p -e "DROP DATABASE IF EXISTS centro_medico; CREATE DATABASE centro_medico;" && mysql -u TU_USUARIO -p centro_medico < database/schema.sql && mysql -u TU_USUARIO -p centro_medico < database/seeds.sql`
4. Arrancar: `cd backend && python3 app.py` (queda en http://127.0.0.1:5000)

## Cómo correr el frontend

1. Activar el entorno virtual: `source .venv/bin/activate`
2. Asegurarse de tener el backend corriendo en paralelo en http://127.0.0.1:5000 (el frontend consume su API vía `BACKEND_URL`).
3. Arrancar el servidor del frontend: `cd frontend && python3 app.py` (queda en http://127.0.0.1:3000)
4. Ingresar desde el navegador a: [http://127.0.0.1:3000](http://127.0.0.1:3000)

### Pruebas en el frontend:
- **Iniciar sesión**: Ir a `/login` con cualquiera de los usuarios de prueba (contraseña: `Prueba1234`).
- **Check-in y Sala de espera**: Iniciar sesión como recepcionista (`ana@test.com`) o admin (`maria@test.com`) e ingresar a `/recepcion/`.
  - Códigos QR de prueba para registrar llegada: `qr_valido_123` y `qr_confirmado_456`.

## Usuarios de prueba

Los carga `database/seeds.sql`. Todos tienen la contraseña `Prueba1234`. **Solo para desarrollo:** no usar estos usuarios en un despliegue real.

| Email | Rol |
|---|---|
| maria@test.com | admin |
| ana@test.com | recepcionista |
| carlos@test.com | médico (Cardiología) |
| jose@test.com | médico (Dermatología) |
| juan@test.com | paciente |
| laura@test.com | paciente |

Para loguearse: `POST /api/v1/auth/login` con `{"email": "...", "password": "Prueba1234"}`. Devuelve un token que se manda en el encabezado `Authorization: Bearer <token>`.

## Fecha y hora

Todo el sistema trabaja en hora de Argentina (GMT-3). Las fechas se guardan en un único campo `DATETIME` sin zona horaria y el backend las compara con `tiempo.obtener_ahora_gmt3()`, así que no depende de la zona horaria de la computadora o del servidor.
