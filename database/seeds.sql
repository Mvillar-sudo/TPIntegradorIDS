-- =============================================
-- DATOS INICIALES / SEMILLA (SEED DATA)
-- =============================================
USE centro_medico;

-- Las fechas relativas (NOW()) de estos datos se calculan en hora de Argentina (GMT-3), que es la
-- que usa el backend, sin importar en qué zona horaria esté configurado el servidor MySQL.
SET time_zone = '-03:00';

-- 1. Coberturas
INSERT INTO coberturas (nombre_cobertura) VALUES 
('Particular'),
('OSDE'),
('Swiss Medical'),
('Galeno');

-- 2. Especialidades
INSERT INTO especialidades (nombre_especialidad) VALUES 
('Cardiología'),
('Clínica Médica'),
('Dermatología'),
('Pediatría'),
('Traumatología');

-- 3. Consultorios
INSERT INTO consultorios (numero_consultorio, piso) VALUES 
('101', 'Planta Baja'),
('102', 'Planta Baja'),
('201', '1er Piso'),
('202', '1er Piso');

-- 4. Usuarios de prueba
INSERT INTO usuarios (rol_usuario, nombre_usuario, apellido_usuario, dni_usuario, email_usuario, password_hash, telefono_usuario, id_cobertura) VALUES
('paciente',      'Juan',   'García',     '12345678', 'juan@test.com',   'scrypt:32768:8:1$YpTksgYT2XI14arx$6639353b1bad077b432b72b59289ecf4a745e2d33ab771cc6e268969829ae1c52892b5a3cb1d2018d506640959145a1703e44a245aab1ce252bc94fb84d51d3b', '1155551234', 1),
('medico',        'Carlos', 'Pérez',      '87654321', 'carlos@test.com', 'scrypt:32768:8:1$JIn3C18qqBOXKsZC$d8e6974f0f16e5f326f9e1f0f12408167041f201bb55b32c4087da21c90ea4be363259fdfb922e2e19ca84baf728cb39fb81b5ca3b545a0979b444314961b9b9', '1155555678', NULL),
('recepcionista', 'Ana',    'López',      '11223344', 'ana@test.com',    'scrypt:32768:8:1$y1noT8CNV2drega1$99cda200edd4941ba7a7c9e0d33cef7aee3c272fdb2847bdad7ce31d0704d5cbd224afb85f8863973447375bdd0d9b32196a92ea681d816a82a29507c287668c', '1155559012', NULL),
('admin',         'María',  'Rodríguez',  '44332211', 'maria@test.com',  'scrypt:32768:8:1$jJoHLfHSdv7U1L9v$df151298820128a2a5188af12ff40464a74403aa2d109cea1fadcd6e45b3ae3eba6945e165d94a2604d86baf45103e6174d2856daaa27d3c74fd320940a6b075', '1155553456', NULL),
('paciente',      'Laura',  'Martínez',   '55667788', 'laura@test.com',  'scrypt:32768:8:1$tkiF8Li42Qcb7lcV$fa023dc4c9c041832d029242cf95d7229ccf60f58a043940a546a4b1d159f3ab0280d15e2e85e4dbe5ea5e2683c463b8feee975bc5c7c8fd1543e72c4c63e539', '1155557890', 2),
('medico',        'Jose', 'Gonzalez',     '11335577', 'jose@test.com', 'scrypt:32768:8:1$I1hcVptpONvQjEJM$957911a2a41e7fd694a81a938d13362df3f7a75c22c7e03905c5523a21d6e15b38644d036c953f3fc52b486fc640f3203477694517407ac8617710f0df6f243c', '1145555678', NULL);

-- 5. Médicos de prueba
INSERT INTO medicos (id_usuario, id_especialidad, matricula) VALUES
((SELECT id_usuario FROM usuarios WHERE email_usuario = 'carlos@test.com'), (SELECT id_especialidad FROM especialidades WHERE nombre_especialidad = 'Cardiología'), 'MN-12345'),
((SELECT id_usuario FROM usuarios WHERE email_usuario = 'jose@test.com'), (SELECT id_especialidad FROM especialidades WHERE nombre_especialidad = 'Dermatología'), 'MN-67890');


-- 6. Turnos de prueba

-- Turno reservado, dentro de la ventana de check-in (10 min en el futuro)
INSERT INTO turnos (id_medico, id_paciente, id_consultorio, fecha_hora, estado, token_qr, fecha_hora_checkin)
VALUES (1, 1, 1, DATE_ADD(NOW(), INTERVAL 10 MINUTE), 'reservado', 'qr_valido_123', NULL);

-- Turno confirmado (check-in ya realizado)
INSERT INTO turnos (id_medico, id_paciente, id_consultorio, fecha_hora, estado, token_qr, fecha_hora_checkin)
VALUES (1, 1, 1, DATE_ADD(NOW(), INTERVAL 20 MINUTE), 'confirmado', 'qr_confirmado_456', NOW());

-- Turno ausente (paciente no se presentó)
INSERT INTO turnos (id_medico, id_paciente, id_consultorio, fecha_hora, estado, token_qr, fecha_hora_checkin)
VALUES (1, 1, 1, DATE_ADD(NOW(), INTERVAL -2 HOUR), 'ausente', 'qr_ausente_789', NULL);

-- Turno reservado (paciente: Laura)
INSERT INTO turnos (id_medico, id_paciente, id_consultorio, fecha_hora, estado, token_qr, fecha_hora_checkin)
VALUES (1, 5, 1, DATE_ADD(NOW(), INTERVAL 3 HOUR), 'reservado', 'qr_laura_101', NULL);

