-- =============================================
-- DATOS INICIALES / SEMILLA (SEED DATA)
-- =============================================

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

-- 4. Médicos de prueba
INSERT INTO medicos (nombre_medico, apellido_medico, id_especialidad, matricula) VALUES
('Juan', 'Pérez', (SELECT id_especialidad FROM especialidades WHERE nombre_especialidad = 'Cardiología'), 'MN-12345'),
('María', 'González', (SELECT id_especialidad FROM especialidades WHERE nombre_especialidad = 'Pediatría'), 'MN-67890');