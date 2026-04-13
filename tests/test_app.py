import pytest
from pathlib import Path
import tempfile
import shutil

from config_loader import load_config
from db import init_db, list_technologies, sync_technologies_from_config


def test_config_loading():
    """Test that config.yaml loads correctly"""
    cfg = load_config()
    assert isinstance(cfg, dict)
    assert 'topics' in cfg
    assert 'technologies' in cfg


def test_database_initialization():
    """Test database initialization creates required tables"""
    # Use temporary database for testing
    temp_dir = Path(tempfile.mkdtemp())
    temp_db = temp_dir / "test.db"
    
    # Monkey patch DB_PATH for testing
    import db
    original_path = db.DB_PATH
    db.DB_PATH = temp_db
    
    try:
        init_db()
        
        # Check tables exist
        con = db.get_connection()
        tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t[0] for t in tables]
        
        assert 'topics' in table_names
        assert 'resources' in table_names
        assert 'sessions' in table_names
        assert 'technologies' in table_names
        
        con.close()  # Close connection
        
    finally:
        db.DB_PATH = original_path
        # Force close any remaining connections
        import gc
        gc.collect()
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            pass  # Ignore on Windows


def test_technology_sync():
    """Test syncing technologies from config"""
    temp_dir = Path(tempfile.mkdtemp())
    temp_db = temp_dir / "test.db"
    
    import db
    original_path = db.DB_PATH
    db.DB_PATH = temp_db
    
    try:
        init_db()
        
        # Test config
        test_config = {
            'data_engineering': [
                {'name': 'SQL', 'priority': 'high', 'description': 'Test SQL'},
                {'name': 'Python', 'priority': 'high', 'description': 'Test Python'}
            ]
        }
        
        sync_technologies_from_config(test_config)
        
        techs = list_technologies()
        assert len(techs) == 2
        
        sql_tech = next(t for t in techs if t['name'] == 'SQL')
        assert sql_tech['category'] == 'data_engineering'
        assert sql_tech['priority'] == 'high'
        assert sql_tech['description'] == 'Test SQL'
        
    finally:
        db.DB_PATH = original_path
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])