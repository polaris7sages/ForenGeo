import subprocess
import shutil
import sys

def make_standalone():
    """Create single executable"""
    shutil.rmtree("dist", ignore_errors=True)
    subprocess.run([sys.executable, "-m", "PyInstaller", 
                   "--onefile", "fh3_cli.py", "--name", "fh3"])

if __name__ == "__main__":
    make_standalone()