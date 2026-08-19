from datetime import datetime
import pytest
from pydantic import ValidationError

from agenda.database import Base
from agenda.models import Task
from agenda.schemas import TaskCreate, TaskUpdate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- FIXTURE PARA BD EN MEMORIA ---

@pytest.fixture
def db_session():
    """Crea una base de datos SQLite limpia en memoria para cada test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

# --- PRUEBAS DE VALIDACIÓN DE ESQUEMAS (PYDANTIC) ---

def test_task_create_default_date_and_status():
    """Verifica que si no se provee fecha ni estado, se asignen valores por defecto."""
    schema = TaskCreate(title="Tarea Test")
    assert schema.title == "Tarea Test"
    assert schema.status == "pendiente"
    assert isinstance(schema.due_date, datetime)

def test_task_create_strip_whitespace():
    """Verifica el saneamiento automático de cadenas con espacios."""
    schema = TaskCreate(title="  Título Limpio  ", description="  Descripción Limpia  ")
    assert schema.title == "Título Limpio"
    assert schema.description == "Descripción Limpia"

def test_task_create_invalid_status():
    """Verifica que Pydantic rechace estados no permitidos."""
    with pytest.raises(ValidationError):
        TaskCreate(title="Tarea Invalida", status="en_proceso")  # type: ignore

def test_task_create_invalid_date_format():
    """Verifica el rechazo de formatos de fecha incorrectos."""
    with pytest.raises(ValidationError):
        TaskCreate(title="Tarea Fecha Mal", due_date="19/08/2026 12:00:00")  # type: ignore

def test_task_update_partial_validation():
    """Verifica la validación parcial en actualizaciones."""
    update_schema = TaskUpdate(status="completada")
    dump = update_schema.model_dump(exclude_unset=True)
    assert dump == {"status": "completada"}
    assert "title" not in dump

# --- PRUEBAS DE PERSISTENCIA (SQLALCHEMY) ---

def test_db_create_task_persisted(db_session):
    """Verifica la creación y persistencia de una tarea en la base de datos."""
    schema = TaskCreate(title="Tarea DB", description="Prueba de Persistencia")
    db_task = Task(**schema.model_dump())
    
    db_session.add(db_task)
    db_session.commit()
    db_session.refresh(db_task)

    retrieved = db_session.query(Task).filter(Task.id == db_task.id).first()
    assert retrieved is not None
    assert retrieved.title == "Tarea DB"
    assert retrieved.status == "pendiente"