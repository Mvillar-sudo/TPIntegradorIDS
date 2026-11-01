-- =============================================
-- DATOS INICIALES / SEMILLA (SEED DATA)
-- =============================================
USE centro_medico;

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
('paciente',      'Juan',   'García',     '12345678', 'juan@test.com',   'hash_placeholder_123', '1155551234', 1),
('medico',        'Carlos', 'Pérez',      '87654321', 'carlos@test.com', 'hash_placeholder_456', '1155555678', NULL),
('recepcionista', 'Ana',    'López',      '11223344', 'ana@test.com',    'hash_placeholder_789', '1155559012', NULL),
('admin',         'María',  'Rodríguez',  '44332211', 'maria@test.com',  'hash_placeholder_012', '1155553456', NULL),
('paciente',      'Laura',  'Martínez',   '55667788', 'laura@test.com',  'hash_placeholder_345', '1155557890', 2),
('medico',        'Jose', 'Gonzalez',     '11335577', 'jose@test.com', 'hash_placeholder_556', '1145555678', NULL);

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

