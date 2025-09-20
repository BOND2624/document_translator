"""
Setup checker for Document Translation System UI
Verifies all dependencies and components are working
"""

import sys
import importlib
import os
from pathlib import Path

def check_imports():
    """Check if all required packages can be imported"""
    required_packages = [
        'streamlit',
        'crewai', 
        'openai',
        'docx',
        'dotenv',
        'pydantic',
        'langchain',
        'langchain_openai'
    ]
    
    print("🔍 Checking package imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package} - {str(e)}")
            failed_imports.append(package)
    
    return failed_imports

def check_project_structure():
    """Check if project structure is correct"""
    required_files = [
        'src/agents/parser_agent.py',
        'src/agents/translation_agent.py', 
        'src/agents/style_agent.py',
        'src/agents/output_agent.py',
        'src/utils/file_manager.py',
        'src/config.py',
        'streamlit_app.py',
        'requirements.txt'
    ]
    
    print("\n📁 Checking project structure...")
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return missing_files

def check_directories():
    """Check if required directories exist"""
    required_dirs = ['src', 'src/agents', 'src/utils', 'output', 'temp']
    
    print("\n📂 Checking directories...")
    for dir_path in required_dirs:
        dir_obj = Path(dir_path)
        if dir_obj.exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"⚠️  {dir_path}/ - creating...")
            dir_obj.mkdir(exist_ok=True, parents=True)

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} - Need 3.8+")
    
    # Check if in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment active")
    else:
        print("⚠️  Virtual environment not detected")

def main():
    """Main setup checker"""
    print("=" * 50)
    print("🚀 Document Translation System - Setup Checker")
    print("=" * 50)
    
    # Check environment
    check_environment()
    
    # Check directories
    check_directories()
    
    # Check project structure
    missing_files = check_project_structure()
    
    # Check imports
    failed_imports = check_imports()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SETUP SUMMARY")
    print("=" * 50)
    
    if not failed_imports and not missing_files:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your system is ready to run the Document Translation UI")
        print("\n🚀 To start the application:")
        print("   • Windows: Double-click 'run_app.bat'")
        print("   • PowerShell: .\\run_app.ps1")
        print("   • Manual: streamlit run streamlit_app.py")
    else:
        print("❌ SETUP ISSUES FOUND:")
        
        if failed_imports:
            print(f"\n📦 Missing packages ({len(failed_imports)}):")
            for package in failed_imports:
                print(f"   • {package}")
            print("\n💡 Fix: pip install -r requirements.txt")
        
        if missing_files:
            print(f"\n📁 Missing files ({len(missing_files)}):")
            for file_path in missing_files:
                print(f"   • {file_path}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
