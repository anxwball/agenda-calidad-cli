# agenda/main.py
from agenda.database import init_db, SessionLocal
from agenda.models import Task

def create_task(title, description, status, due_date):
    """Crear una nueva tarea en la base de datos."""
    db = SessionLocal()
    new_task = Task(title=title, description=description, status=status, due_date=due_date)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    db.close()
    print(f"[EXITO] Tarea '{title}' creada con éxito.")
    return new_task

def list_tasks():
    """Listar todas las tareas en la base de datos."""
    db = SessionLocal()
    tasks = db.query(Task).all()
    db.close()
    print("\n--------------- AGENDA DE TAREAS ---------------")
    for t in tasks:
        print(f"[{t.id}] [{t.status}] {t.title}: {t.description} (Vencimiento: {t.due_date})") 
    print("------------------------------------------------")

def delete_task(task_id):
    """Eliminar una tarea de la base de datos por su ID."""
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        print(f"[EXITO] Tarea con ID {task_id} eliminada con éxito.")
    else:
        print(f"[ERROR] No se encontró ninguna tarea con ID {task_id}.")
    db.close()

def update_task(task_id, title=None, description=None, status=None, due_date=None):
    """Actualizar una tarea existente en la base de datos."""
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if due_date is not None:
            task.due_date = due_date
        db.commit()
        print(f"[EXITO] Tarea con ID {task_id} actualizada con éxito.")
    else:
        print(f"[ERROR] No se encontró ninguna tarea con ID {task_id}.")
    db.close()

def main():
    """Función principal para ejecutar el menú CLI interactivo."""
    init_db()  # Inicializar la base de datos y crear tablas si no existen
    while True:
        print("\n--- MENÚ DE AGENDA ---")
        print("1. Crear tarea")
        print("2. Listar tareas")
        print("3. Eliminar tarea")
        print("4. Actualizar tarea")
        print("5. Salir")
        choice = input("Seleccione una opción: ")

        if choice == "1":
            title = input("Ingrese el título de la tarea: ")
            description = input("Ingrese la descripción de la tarea: ")
            status = input("Ingrese el estado de la tarea (pendiente/completada): ")
            due_date = input("Ingrese la fecha de vencimiento (YYYY-MM-DD HH:MM:SS): ")
            create_task(title, description, status, due_date)
        elif choice == "2":
            list_tasks()
        elif choice == "3":
            task_id = int(input("Ingrese el ID de la tarea a eliminar: "))
            delete_task(task_id)
        elif choice == "4":
            task_id = int(input("Ingrese el ID de la tarea a actualizar: "))
            title = input("Ingrese el nuevo título de la tarea (deje en blanco para no cambiar): ")
            description = input("Ingrese la nueva descripción de la tarea (deje en blanco para no cambiar): ")
            status = input("Ingrese el nuevo estado de la tarea (pendiente/completada, deje en blanco para no cambiar): ")
            due_date = input("Ingrese la nueva fecha de vencimiento (YYYY-MM-DD HH:MM:SS, deje en blanco para no cambiar): ")
            update_task(task_id, title or None, description or None, status or None, due_date or None)
        elif choice == "5":
            print("Saliendo del programa...")
            break
        else:
            print("[ERROR] Opción no válida. Intente nuevamente.")    

if __name__ == "__main__":
    main()
