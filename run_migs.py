import subprocess

def run_cmd(cmd, outfile):
    result = subprocess.run(cmd, capture_output=True, text=True)
    with open(outfile, 'w') as f:
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)

run_cmd(['.venv\\Scripts\\python.exe', 'manage.py', 'makemigrations'], 'mig1.txt')
run_cmd(['.venv\\Scripts\\python.exe', 'manage.py', 'migrate'], 'mig2.txt')
