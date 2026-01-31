import sys
print(f"Python Executable: {sys.executable}")
print("Attempting to import Flask...")
try:
    import flask
    print(f"✅ Flask imported successfully! Version: {flask.__version__}")
except ImportError as e:
    print(f"❌ Failed to import Flask: {e}")

print("Attempting to import flask_cors...")
try:
    import flask_cors
    print(f"✅ flask_cors imported successfully! Version: {flask_cors.__version__}")
except ImportError as e:
    print(f"❌ Failed to import flask_cors: {e}")
