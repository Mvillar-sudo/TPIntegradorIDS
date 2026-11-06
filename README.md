# TPIntegradorIDS

Sistema de turnos médicos con check-in por QR (Centro Médico Salud Integral).
Backend y frontend en Flask, base de datos MySQL con SQL escrito a mano (sin ORM).

## Cómo correr el backend

1. Crear el entorno e instalar dependencias (desde la carpeta principal): `source init.sh`
2. Copiar `.env.example` como `backend/.env` y completar los valores (base de datos, `JWT_SECRET_KEY`, mail).
3. Crear la base con los datos de prueba: `mysql -u TU_USUARIO -p < database/schema.sql` y `mysql -u TU_USUARIO -p < database/seeds.sql`
4. Arrancar: `cd backend && python3 app.py` (queda en http://127.0.0.1:5000)

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
