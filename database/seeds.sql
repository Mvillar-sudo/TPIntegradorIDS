-- =============================================
-- DATOS INICIALES / SEMILLA (SEED DATA)
-- =============================================

USE centro_medico;

-- 1. Coberturas
INSERT IGNORE INTO coberturas (id_cobertura, nombre) VALUES
(1, 'Particular'),
(2, 'OSDE'),
(3, 'Swiss Medical'),
(4, 'Galeno');

-- 2. Especialidades
INSERT IGNORE INTO especialidades (id_especialidad, nombre) VALUES
(1, 'Cardiología'),
(2, 'Clínica Médica'),
(3, 'Dermatología'),
(4, 'Pediatría'),
(5, 'Traumatología');

-- 3. Consultorios
INSERT IGNORE INTO consultorios (id_consultorio, numero, piso) VALUES
(1, '101', 'Planta Baja'),
(2, '102', 'Planta Baja'),
(3, '201', '1er Piso'),
(4, '202', '1er Piso');

-- 4. Usuarios
INSERT IGNORE INTO usuarios (id_usuario, rol_usuario, nombre, apellido, dni, email, password_hash, telefono, id_cobertura) VALUES
(1, 'paciente',      'Juan',   'García',     '12345678', 'juan@test.com',   'hash_placeholder_123', '1155551234', 1),
(2, 'medico',        'Carlos', 'Pérez',      '87654321', 'carlos@test.com', 'hash_placeholder_456', '1155555678', NULL),
(3, 'recepcionista', 'Ana',    'López',      '11223344', 'ana@test.com',    'hash_placeholder_789', '1155559012', NULL),
(4, 'admin',         'María',  'Rodríguez',  '44332211', 'maria@test.com',  'hash_placeholder_012', '1155553456', NULL),
(5, 'paciente',      'Laura',  'Martínez',   '55667788', 'laura@test.com',  'hash_placeholder_345', '1155557890', 2);

-- 5. Médicos
INSERT IGNORE INTO medicos (id_medico, id_usuario, id_especialidad, matricula) VALUES
(1, 2, 1, 'MN-12345');

-- 6. Turnos de prueba
DELETE FROM turnos WHERE id_turno IN (901, 902, 903, 904);

-- Turno 901: reservado, dentro de la ventana de check-in (10 min en el futuro)
INSERT INTO turnos (id_turno, id_medico, id_paciente, id_consultorio, fecha_hora_inicio, fecha_hora_fin, estado, codigo_qr_hash, fecha_hora_checkin)
VALUES (901, 1, 1, 1, DATE_ADD(NOW(), INTERVAL 10 MINUTE), DATE_ADD(NOW(), INTERVAL 30 MINUTE), 'reservado', 'qr_valido_123', NULL);

-- Turno 902: confirmado (check-in ya realizado)
INSERT INTO turnos (id_turno, id_medico, id_paciente, id_consultorio, fecha_hora_inicio, fecha_hora_fin, estado, codigo_qr_hash, fecha_hora_checkin)
VALUES (902, 1, 1, 1, DATE_ADD(NOW(), INTERVAL 1 HOUR), DATE_ADD(NOW(), INTERVAL 2 HOUR), 'confirmado', 'qr_confirmado_456', NOW());

-- Turno 903: ausente (paciente no se presentó)
INSERT INTO turnos (id_turno, id_medico, id_paciente, id_consultorio, fecha_hora_inicio, fecha_hora_fin, estado, codigo_qr_hash, fecha_hora_checkin)
VALUES (903, 1, 1, 1, DATE_ADD(NOW(), INTERVAL -2 HOUR), DATE_ADD(NOW(), INTERVAL -1 HOUR), 'ausente', 'qr_ausente_789', NULL);

-- Turno 904: reservado, paciente diferente (Laura)
INSERT INTO turnos (id_turno, id_medico, id_paciente, id_consultorio, fecha_hora_inicio, fecha_hora_fin, estado, codigo_qr_hash, fecha_hora_checkin)
VALUES (904, 1, 5, 1, DATE_ADD(NOW(), INTERVAL 3 HOUR), DATE_ADD(NOW(), INTERVAL 4 HOUR), 'reservado', 'qr_laura_101', NULL);
