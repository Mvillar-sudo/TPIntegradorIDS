CREATE DATABASE IF NOT EXISTS centro_medico;
USE centro_medico;

-- 1. Tabla coberturas
CREATE TABLE IF NOT EXISTS coberturas(
  id_cobertura int auto_increment PRIMARY KEY,
  nombre_cobertura varchar(100)
);

-- 2. Tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios(
  id_usuario int auto_increment PRIMARY KEY,
  rol_usuario enum('admin', 'recepcionista', 'paciente') NOT NULL,
  nombre_usuario varchar(100),
  apellido_usuario varchar(100),
  dni_usuario varchar(20) UNIQUE,
  email_usuario varchar(150) UNIQUE,
  password_hash varchar(255),
  telefono_usuario varchar(12),
  id_cobertura int,
  FOREIGN KEY (id_cobertura) references coberturas(id_cobertura)
);

-- 3. Tabla especialidades
CREATE TABLE IF NOT EXISTS especialidades(
  id_especialidad int auto_increment PRIMARY KEY,
  nombre_especialidad varchar(100)
);

-- 4. Tabla medicos
CREATE TABLE IF NOT EXISTS medicos(
    id_medico int auto_increment PRIMARY KEY,
    id_usuario int,
    id_especialidad int,
    matricula varchar(50),
    FOREIGN KEY (id_usuario) references usuarios(id_usuario),
    FOREIGN KEY (id_especialidad) references especialidades(id_especialidad)
);

-- 5. Tabla consultorios
CREATE TABLE IF NOT EXISTS consultorios(
  id_consultorio int auto_increment PRIMARY KEY,
  numero_consultorio varchar(20),
  piso varchar(20)
);

-- 6. Tabla agendas
CREATE TABLE IF NOT EXISTS agendas(
  id_agenda int auto_increment PRIMARY KEY,
  id_medico int,
  id_consultorio int,
  dia_semana int,
  hora_inicio time,
  hora_fin time,
  duracion_turno_minutos int,
  FOREIGN KEY (id_medico) references medicos(id_medico),
  FOREIGN KEY (id_consultorio) references consultorios(id_consultorio)
);

-- 7. Tabla turnos
CREATE TABLE IF NOT EXISTS turnos(
  id_turno int PRIMARY KEY,
  id_medico int,
  id_paciente int NULL,
  id_consultorio int,
  fecha_hora_inicio datetime,
  fecha_hora_fin datetime,
  estado enum('disponible', 'reservado', 'confirmado', 'atendido', 'cancelado', 'ausente') NOT NULL,
  codigo_qr_hash varchar(255),
  fecha_hora_checkin datetime null,
  FOREIGN KEY (id_medico) references medicos(id_medico),
  FOREIGN KEY (id_paciente) references usuarios(id_usuario),
  FOREIGN KEY (id_consultorio) references consultorios(id_consultorio)
);
