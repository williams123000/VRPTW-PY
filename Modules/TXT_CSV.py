"""
Autor: Williams Chan Pescador
Descripción: Este script se encarga de leer un archivo txt que contiene los datos de una instancia y
convertirlo a un archivo CSV.
"""

import csv
import sys
import os

# Función para convertir un archivo .txt a .csv
def txt_to_csv(input_file, output_file, name_instance):
    # Abre el archivo de entrada y salida
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        lines = infile.readlines()
        lines_iter = iter(lines)
        writer = csv.writer(outfile)
        writer.writerow([name_instance])
        for line in lines_iter:
            line = line.strip()
            if not line:
                continue  # Ignore empty lines

            if line.isupper():
                current_section = line
                header = next(lines_iter).split()
                continue

            data = line.split()
            writer.writerow(data)
            
def Convert(Name_Instance):
    # Especifica las rutas de los directorios aquí
    input_directory = "VRP_Solomon/"
    output_directory = "Instances/"

    txt_file = os.path.join(input_directory, Name_Instance.split(".")[0] + ".txt")
    csv_file = os.path.join(output_directory, Name_Instance.split(".")[0] + ".csv")
    txt_to_csv(txt_file, csv_file, Name_Instance.split(".")[0])
    #print(f"Se ha convertido {txt_file} a {csv_file}")