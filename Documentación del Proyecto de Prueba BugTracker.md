# Proyecto de Prueba: BugTracker

## Descripción General

El framework incluye un proyecto de prueba que implementa un sistema de seguimiento de bugs (BugTracker). Este proyecto sirve como ejemplo de uso del framework y como base para desarrollo y testing.

## Estructura de Datos

### Tablas Principales

1. **Projects (Proyectos)**

   - Información básica de proyectos
   - Campos: nombre, descripción, estado, fechas
   - Estados disponibles: Activo, En Espera, Completado, Cancelado

2. **Issues (Tickets/Bugs)**

   - Sistema central de tracking de problemas
   - Campos: título, descripción, estado, prioridad, tipo
   - Estados: Abierto, En Progreso, En Revisión, Resuelto, Cerrado
   - Prioridades: Crítica, Alta, Media, Baja
   - Tipos: Bug, Nueva Funcionalidad, Mejora, Tarea

### Tablas Auxiliares

3. **Comments (Comentarios)**

   - Comentarios en issues
   - Campos: contenido, autor, fecha

4. **Tags (Etiquetas)**

   - Sistema de etiquetado para issues
   - Campos: nombre, color, descripción

5. **Issue History (Historial)**

   - Registro de cambios en issues
   - Campos: campo modificado, valor anterior, nuevo valor, autor del cambio

6. **Issue Tags (Relación Issues-Tags)**

   - Tabla de relación para etiquetas
   - Permite asignar múltiples etiquetas a issues

## Relaciones

- Issues pertenecen a un Proyecto (Many-to-One)
- Comments pertenecen a un Issue (Many-to-One)
- Issues tienen múltiples Tags (Many-to-Many vía Issue_Tags)
- Issue History registra cambios de un Issue (Many-to-One)

## Características del Sistema

### Configuración UI

- Campos configurados con widgets específicos
- Validaciones incorporadas
- Mensajes de ayuda y placeholders
- Campos de solo lectura donde corresponde

### Campos Automáticos

- Timestamps de creación/actualización
- Tracking de cambios automático
- IDs autogenerados

### Validaciones

- Campos requeridos marcados
- Longitudes máximas definidas
- Valores únicos donde necesario
- Validaciones personalizadas

## Cómo Utilizar

### 1. Generar Metadata

```bash
# Crear directorio si no existe
mkdir -p scripts/initialproject

# Ejecutar script de metadata
python scripts/initialproject/seed_metadata_initial_project.py
```

### 2. Generar Tablas

```bash
# Generar tablas físicas
python scripts/generate_tables.py
```

### 3. Generar Modelos

```bash
# Generar modelos y schemas
python scripts/generate_models.py
```

## Notas de Desarrollo

### Extensiones Posibles

- Sistema de archivos adjuntos
- Notificaciones
- Menciones de usuarios (@usuario)
- Integración con servicios externos
- Sistema de reportes

### Consideraciones

- Las contraseñas de usuario deben ser hasheadas
- Los cambios de estado deben registrarse
- Los comentarios no deben poder modificarse
- Las etiquetas deben ser reutilizables
