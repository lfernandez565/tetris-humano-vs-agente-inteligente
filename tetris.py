# Este modulo nos permitirá ejecutar los procesos secundarios de los archivos humano.py y ai.py
import subprocess

# Ejecuta humano.py
subprocess.Popen(['python', 'humano.py'])

# Ejecuta ai.py
subprocess.Popen(['python', 'ai.py'])