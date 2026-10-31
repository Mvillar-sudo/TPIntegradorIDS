CREATE DATABASE IF NOT EXISTS centro_medico;
USE centro_medico;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS turnos;
DROP TABLE IF EXISTS agendas_medicos;
DROP TABLE IF EXISTS consultorios;
DROP TABLE IF EXISTS medicos;
DROP TABLE IF EXISTS especialidades;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS coberturas;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Tabla coberturas
CREATE TABLE IF NOT EXISTS coberturas (
    id_cobertura INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- 2. Tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    rol_usuario ENUM('admin', 'paciente', 'recepcionista', 'medico') NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    dni VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    telefono VARCHAR(50),
    id_cobertura INT,
    FOREIGN KEY (id_cobertura) REFERENCES coberturas(id_cobertura)
);

-- 3. Tabla especialidades
CREATE TABLE IF NOT EXISTS especialidades (
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- 4. Tabla medicos
CREATE TABLE IF NOT EXISTS medicos (
    id_medico INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_especialidad INT NOT NULL,
    matricula VARCHAR(50) UNIQUE NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_especialidad) REFERENCES especialidades(id_especialidad)
);

-- 5. Tabla consultorios
CREATE TABLE IF NOT EXISTS consultorios (
    id_consultorio INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(50) NOT NULL,
    piso VARCHAR(50) NOT NULL
);

-- 6. Tabla agendas_medicos
CREATE TABLE IF NOT EXISTS agendas_medicos (
    id_agenda INT AUTO_INCREMENT PRIMARY KEY,
    id_medico INT NOT NULL,
    id_consultorio INT NOT NULL,
    dia_semana INT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    duracion_turno_minutos INT NOT NULL,
    FOREIGN KEY (id_medico) REFERENCES medicos(id_medico),
    FOREIGN KEY (id_consultorio) REFERENCES consultorios(id_consultorio)
);

-- 7. Tabla turnos
CREATE TABLE IF NOT EXISTS turnos (
    id_turno INT AUTO_INCREMENT PRIMARY KEY,
    id_medico INT NOT NULL,
    id_paciente INT NULL,
    id_consultorio INT NOT NULL,
    fecha_hora_inicio DATETIME NOT NULL,
    fecha_hora_fin DATETIME NOT NULL,
    estado ENUM('disponible', 'reservado', 'confirmado', 'atendido', 'cancelado', 'ausente') NOT NULL DEFAULT 'disponible',
    codigo_qr_hash VARCHAR(255) UNIQUE NULL,
    fecha_hora_checkin DATETIME NULL,
    FOREIGN KEY (id_medico) REFERENCES medicos(id_medico),
    FOREIGN KEY (id_paciente) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_consultorio) REFERENCES consultorios(id_consultorio)
);
