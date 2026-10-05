# 🌾 Terranova - Sistema de Gestión Agrícola

Sistema **Fullstack** para la gestión integral de fincas, lotes, cultivos, tareas, insumos y gastos operativos. Diseñado para agricultores y administradores que necesitan control total de sus operaciones agrícolas.

![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow)
![Angular](https://img.shields.io/badge/Angular-17+-DD0031?logo=angular)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql)

---

## 📸 Capturas de Pantalla



##  Tecnologías Utilizadas

### Backend
- **Python 3.14** con **FastAPI**
- **PostgreSQL** como base de datos relacional
- **SQLAlchemy** como ORM
- **JWT (JSON Web Tokens)** para autenticación segura
- **Passlib + bcrypt** para encriptación de contraseñas
- **Pydantic** para validación de esquemas

### Frontend
- **Angular 17+** (Standalone Components)
- **TypeScript**
- **RxJS** para manejo de observables y streams
- **CSS3** con animaciones y diseño responsive
- **HttpClient** con interceptores para JWT

---

## ✨ Características

- 🔐 **Autenticación segura** con JWT y contraseñas encriptadas
- 👥 **Multi-usuario**: cada usuario solo ve y gestiona sus propias fincas
- 🏠 **CRUD completo** de fincas, lotes, cultivos, tareas, insumos, compras, cosechas y gastos
- 📊 **Gestión de inventario** de insumos con cálculo automático de costo promedio
- 💰 **Registro de gastos operativos** categorizados por tipo y alcance
- 🎨 **Interfaz moderna** con animaciones y diseño responsive

---

## ️ Instalación y Configuración

### Requisitos Previos
- Python 3.14+
- Node.js 18+
- PostgreSQL 15+
- Git

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/terranova.git
cd terranova

### 2. Configurar el Backend
```bash
cd backend
pip install -r requirements.txt
```

### edita database.py con tus credenciales de PostgreSQL:

engine = create_engine("postgresql://usuario:contraseña@localhost:5432/terranova")

### Si es la primera vez que ejecutas el proyecto, crea la base de datos vacía en PostgreSQL:

```sql
CREATE DATABASE terranova;
```

### Es posible que falten columnas en la tabla tareas (por actualizaciones recientes del modelo). Ejecuta este script en la raiz del proyecto para sincronizar:

```bash
cd backend/scripts
python add_tareas_columns.py
```

### Agregar nuevas categorías para Gastos Operativos

```
-- Agregar categorías específicas para gastos operativos
INSERT INTO categorias (id, nombre) VALUES 
(6, 'Mano de obra'),
(7, 'Transporte'),
(8, 'Maquinaria'),
(9, 'Servicios públicos'),
(10, 'Mantenimiento'),
(11, 'Administración')
ON CONFLICT (id) DO NOTHING;
```

### Agregar columna fecha_limite a la tabla tareas

```
-- Agregar campo de fecha límite para tareas
ALTER TABLE tareas 
ADD COLUMN IF NOT EXISTS fecha_limite DATE;
```

### Agregar columna fecha_limite a la tabla gastos_operativos

```
-- Agregar campo de fecha límite para gastos operativos
ALTER TABLE gastos_operativos 
ADD COLUMN IF NOT EXISTS fecha_limite DATE;
```

### Actualizar registros antiguos de gastos con fecha límite por defecto (opcional)

```
-- Establecer fecha límite para registros antiguos (30 días después de la fecha original)

UPDATE gastos_operativos 
SET fecha_limite = fecha + INTERVAL '30 days'
WHERE fecha_limite IS NULL AND fecha IS NOT NULL;

-- Si no tienen fecha, ponerla como hoy + 7 días
UPDATE gastos_operativos 
SET fecha_limite = CURRENT_DATE + INTERVAL '7 days'
WHERE fecha_limite IS NULL;
```
## 🗄️ Migraciones de Base de Datos

### Sesión del 05/10/2026 - Integración de Insumos en Tareas, Compras, Gastos Operativos y Fechas Límite

#### Cambios realizados:

1. **Tabla `categorias`**: Se agregaron nuevas categorías para gastos operativos (IDs 6-11).
2. **Tabla `tareas`**: Se agregó la columna `fecha_limite` (DATE) para control de vencimiento.
3. **Tabla `gastos_operativos`**: Se agregó la columna `fecha_limite` (DATE) para control de vencimiento.

#### Scripts SQL ejecutados:
[pegar los scripts de arriba]
