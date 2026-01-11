"""
Setup and initialization script
"""
import os
import sys

def setup_environment():
    """Setup environment and create necessary directories"""
    print("🔧 Setting up environment...")
    
    # Create directories
    directories = ['logs', 'models', 'data', 'data/datasets']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  .env file not found, copying from .env.example...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ .env file created")
        else:
            print("❌ .env.example not found")
            return False
    
    print("✅ Environment setup complete")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'flask_cors', 'flask_socketio', 'sqlalchemy',
        'psycopg2', 'redis', 'sklearn', 'numpy', 'pandas'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def init_database():
    """Initialize database"""
    print("\n🗄️  Initializing database...")
    
    try:
        from app import app
        from database import db
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created")
        
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def generate_demo_data():
    """Generate demo data"""
    print("\n📊 Generating demo data...")
    
    try:
        from app import app
        from utils.data_generator import DataGenerator
        
        with app.app_context():
            DataGenerator.generate_all()
        
        return True
    except Exception as e:
        print(f"❌ Demo data generation failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("AI Anomaly Detection Backend - Setup Script")
    print("=" * 60)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠️  Please install missing dependencies first")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Ask user if they want to initialize database
    response = input("\n🗄️  Initialize database? (y/n): ")
    if response.lower() == 'y':
        if not init_database():
            sys.exit(1)
        
        # Ask if they want demo data
        response = input("\n📊 Generate demo data? (y/n): ")
        if response.lower() == 'y':
            if not generate_demo_data():
                print("⚠️  Demo data generation failed, but you can continue")
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Start Docker services: docker-compose up -d")
    print("3. Run the application: python app.py")
    print("4. Access API at: http://localhost:5000")
    print("5. Access Zabbix at: http://localhost:8080")
    print("\n🚀 Happy coding!\n")

if __name__ == '__main__':
    main()
