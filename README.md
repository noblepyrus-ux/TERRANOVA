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