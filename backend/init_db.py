import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.database import init_database, get_db
from backend.app.core.security import hash_password

def seed_database():
    print("Inicializando estructura de base de datos SQLite...")
    init_database()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if default admin exists
        cursor.execute("SELECT id FROM users WHERE email = 'admin@documind.com'")
        if not cursor.fetchone():
            pwd = hash_password("Admin123!")
            cursor.execute(
                "INSERT INTO users (email, full_name, password_hash, role) VALUES (?, ?, ?, ?)",
                ("admin@documind.com", "Administrador DocuMind", pwd, "ADMIN")
            )
            admin_id = cursor.lastrowid
            print(f"Usuario administrador creado: admin@documind.com (ID: {admin_id})")
            
            # Create default enterprise repositories
            default_repos = [
                ("Contratos y Acuerdos Legales", "Repositorio de minutas, contratos de prestación de servicios y confidencialidad."),
                ("Facturación y Finanzas", "Comprobantes fiscales, facturas electrónicas y órdenes de compra."),
                ("Talento Humano y Selección", "Hojas de vida de candidatos, perfiles de competencias y certificaciones."),
                ("Informes Técnicos de TI", "Arquitectura de software, planes de contingencia y manuales de operaciones.")
            ]
            
            for name, desc in default_repos:
                cursor.execute(
                    "INSERT INTO repositories (user_id, name, description) VALUES (?, ?, ?)",
                    (admin_id, name, desc)
                )
            print("Carpetas y repositorios por defecto inicializados exitosamente.")
        else:
            print("El usuario administrador ya existe en la base de datos.")

if __name__ == "__main__":
    seed_database()
    print("Inicialización completada con éxito.")
