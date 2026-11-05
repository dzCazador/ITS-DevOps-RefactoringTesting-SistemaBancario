import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Intenta importar la Base de SQLAlchemy si existe
try:
    from src.modelos.models import Base
except Exception:
    Base = None

@pytest.fixture
def db_session():
    """Fixture que provee una sesión de base de datos SQLite en memoria."""
    engine = create_engine("sqlite:///:memory:")
    
    if Base is not None:
        Base.metadata.create_engine(bind=engine)
        
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()