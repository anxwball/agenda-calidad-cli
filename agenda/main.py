from typing import Any, Dict
from pydantic import ValidationError
from agenda.database import init_db, SessionLocal
from agenda.models import Task
from agenda.schemas import TaskCreate, TaskUpdate

def create_task(title: str, description: str, status: str, due_date: str) -> None:
    """Crear una nueva tarea previa validación con Pydantic."""
    raw_data: Dict[str, Any] = {
        "title": title,
        "description": description,
        "status": status.strip() if status.strip() else "pendiente",
        "due_date": due_date.strip() if due_date.strip() else None,
    }

    try:
        task_data = TaskCreate(**raw_data)
    except ValidationError as e:
        print("\n[ERROR DE VALIDACIÓN]")
        for err in e.errors():
            print(f"- Campo '{err['loc'][0]}': {err['msg']}")
        return

    db = SessionLocal()
    new_task = Task(**task_data.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    db.close()
    print(f"[ÉXITO] Tarea '{new_task.title}' creada con éxito.")

def list_tasks() -> None:
    """Listar todas las tareas en la base de datos."""
    db = SessionLocal()
    tasks = db.query(Task).all()
    db.close()
    print("\n--------------- AGENDA DE TAREAS ---------------")
    for t in tasks:
        fmt_date = t.due_date.strftime("%Y-%m-%d %H:%M:%S") if hasattr(t.due_date, "strftime") else str(t.due_date)
        print(f"[{t.id}] [{t.status}] {t.title}: {t.description} (Vencimiento: {fmt_date})") 
    print("------------------------------------------------")

def delete_task(task_id: int) -> None:
    """Eliminar una tarea por su ID."""
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        print(f"[ÉXITO] Tarea con ID {task_id} eliminada con éxito.")
    else:
        print(f"[ERROR] No se encontró ninguna tarea con ID {task_id}.")
    db.close()

def update_task(task_id: int, title: str | None = None, description: str | None = None, status: str | None = None, due_date: str | None = None) -> None:
    """Actualizar una tarea previa validación parcial con Pydantic."""
    raw_data: Dict[str, Any] = {}
    if title: raw_data["title"] = title
    if description: raw_data["description"] = description
    if status: raw_data["status"] = status
    if due_date: raw_data["due_date"] = due_date

    try:
        update_data = TaskUpdate(**raw_data)
    except ValidationError as e:
        print("\n[ERROR DE VALIDACIÓN]")
        for err in e.errors():
            print(f"- Campo '{err['loc'][0]}': {err['msg']}")
        return

    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        db.commit()
        print(f"[ÉXITO] Tarea con ID {task_id} actualizada con éxito.")
    else:
        print(f"[ERROR] No se encontró ninguna tarea con ID {task_id}.")
    db.close()

# --- HANDLERS PARA REDUCIR COMPLEJIDAD COGNITIVA EN MAIN ---

def _handle_create():
    title = input("Ingrese el título de la tarea: ")
    description = input("Ingrese la descripción de la tarea: ")
    status = input("Ingrese el estado (pendiente/completada): ")
    due_date = input("Ingrese la fecha de vencimiento (YYYY-MM-DD HH:MM:SS) [Dejar en blanco para hoy]: ")
    create_task(title, description, status, due_date)

def _handle_delete():
    try:
        task_id = int(input("Ingrese el ID de la tarea a eliminar: "))
        delete_task(task_id)
    except ValueError:
        print("[ERROR] El ID debe ser un número entero.")

def _handle_update():
    try:
        task_id = int(input("Ingrese el ID de la tarea a actualizar: "))
        title = input("Nuevo título (deje en blanco para no cambiar): ")
        description = input("Nueva descripción (deje en blanco para no cambiar): ")
        status = input("Nuevo estado (pendiente/completada, deje en blanco para no cambiar): ")
        due_date = input("Nueva fecha (YYYY-MM-DD HH:MM:SS, deje en blanco para no cambiar): ")
        update_task(
            task_id,
            title or None,
            description or None,
            status or None,
            due_date or None
        )
    except ValueError:
        print("[ERROR] El ID debe ser un número entero.")

def main() -> None:
    """Función principal con baja complejidad cognitiva."""
    init_db()
    
    # Mapeo de opciones a funciones (Dispatch Pattern)
    actions = {
        "1": _handle_create,
        "2": list_tasks,
        "3": _handle_delete,
        "4": _handle_update,
    }

    while True:
        print("\n--- MENÚ DE AGENDA ---")
        print("1. Crear tarea\n2. Listar tareas\n3. Eliminar tarea\n4. Actualizar tarea\n5. Salir")
        choice = input("Seleccione una opción: ").strip()

        if choice == "5":
            print("Saliendo del programa...")
            break

        action = actions.get(choice)
        if action:
            action()
        else:
            print("[ERROR] Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()