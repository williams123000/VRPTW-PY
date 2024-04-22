
from tqdm import tqdm
import time

# Definir la cantidad total de iteraciones
total_iterations = 100

# Iterar sobre las iteraciones totales
for i in tqdm(range(total_iterations), desc="Procesando", unit="iter"):
    # Simular un proceso que tarda un poco de tiempo
    time.sleep(0.1)

print("¡Proceso completado!")
