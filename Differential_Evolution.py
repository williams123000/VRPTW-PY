"""
Autor: Williams Chan Pescador
Descripción: Programa principal que ejecuta el algoritmo de Evolución Diferencial para el problema VRPTW ACO. 
Este programa se encarga de cargar los parámetros del archivo de configuración, inicializar los vectores de la población, 
realizar las evaluaciones de las soluciones, seleccionar las mejores soluciones y guardar los resultados en un archivo JSON.
Alogrítmo: Evolución Diferencial

"""

import random
import json
import math
from VRPTWACO import VRPTWACO
from colorama import Fore
import time
import datetime
from tqdm import tqdm
import csv
import os
from Modules.Generate_JSON import Generate_JSON # Importamos la función Generate_JSON del módulo Generate_JSON en la carpeta Modules 

# Clase Vector para almacenar los parámetros de la solución
class Vector:
    # Constructor de la clase
    def __init__(self):
        self.Alpha = 0.0 # Parámetro Alpha
        self.Beta = 0.0 # Parámetro Beta
        self.Gamma = 0.0 # Parámetro Gamma
        self.Rho = 0.0 # Parámetro Rho
        self.Number_Iterations = 0 # Número de iteraciones
        self.FO = 0.0 # Función Objetivo
        self.Type_Evaluation = 0 # Tipo de evaluación

    # Método para reiniciar los valores del vector
    def Reset_Vector(self):
        self.Alpha = 0.0
        self.Beta = 0.0
        self.Gamma = 0.0
        self.Rho = 0.0
        self.Number_Iterations = 0
        self.FO = 0.0
        self.Type_Evaluation = 0

    # Método para imprimir los valores del vector
    def Print_Vector(self):
        print("Alpha: ", self.Alpha)
        print("Beta: ", self.Beta)
        print("Gamma: ", self.Gamma)
        print("Rho: ", self.Rho)
        print("Number_Iterations: ", self.Number_Iterations)
        print("FO: ", self.FO)
        print("Type_Evaluation: ", self.Type_Evaluation)

    # Método para inicializar los valores del vector
    def Initialize_Objetive (self):
        global Settings # Variable global Settings para acceder a los parámetros del archivo de configuración Settings.json 

        self.Alpha = random.uniform(Settings["Alpha"]["MIN"], Settings["Alpha"]["MAX"]) # Inicializa el parámetro Alpha con un valor aleatorio entre el mínimo y máximo definido en el archivo de configuración Settings.json
        self.Beta = random.uniform(Settings["Beta"]["MIN"], Settings["Beta"]["MAX"]) # Inicializa el parámetro Beta con un valor aleatorio entre el mínimo y máximo definido en el archivo de configuración Settings.json
        self.Gamma = random.uniform(Settings["Gamma"]["MIN"], Settings["Gamma"]["MAX"]) # Inicializa el parámetro Gamma con un valor aleatorio entre el mínimo y máximo definido en el archivo de configuración Settings.json
        self.Rho = random.uniform(Settings["Rho"]["MIN"], Settings["Rho"]["MAX"]) # Inicializa el parámetro Rho con un valor aleatorio entre el mínimo y máximo definido en el archivo de configuración Settings.json 
        self.Number_Iterations = random.randint(Settings["N_Iterations"]["MIN"], Settings["N_Iterations"]["MAX"]) # Inicializa el número de iteraciones con un valor aleatorio entre el mínimo y máximo definido en el archivo de configuración Settings.json
        self.FO = 0.0 # Inicializa la función objetivo en 0
        self.Type_Evaluation = 1 # Inicializa el tipo de evaluación en 1 (Objetivo) 


    # Método para actualizar el tipo de evaluación del vector (Objetivo, Ruido o Prueba)
    def Update_Type_Evaluation(self, Type_Evaluation): 
        self.Type_Evaluation = Type_Evaluation # Actualiza el tipo de evaluación con el valor recibido como parámetro

# Función para inicializar el ruido en los vectores de la población
def Initialize_Noise (Vectors_Objective, Vectors_Noise, Factor_Mutation):
    A = 0 # Variable A para almacenar un valor aleatorio
    B = 0 # Variable B para almacenar un valor aleatorio
    C = 0 # Variable C para almacenar un valor aleatorio

    for i in range(len(Vectors_Noise)):
        A = 0 # Reinicia la variable A
        B = 0 # Reinicia la variable B
        C = 0 # Reinicia la variable C

        while A == B or A == C or B == C :
            A = random.randint(0, len(Vectors_Objective)-1) # Asigna un valor aleatorio a la variable A entre 0 y el tamaño de la población - 1 
            B = random.randint(0, len(Vectors_Objective)-1) # Asigna un valor aleatorio a la variable B entre 0 y el tamaño de la población - 1
            C = random.randint(0, len(Vectors_Objective)-1) # Asigna un valor aleatorio a la variable C entre 0 y el tamaño de la población - 1

        # Actualiza los valores del vector de ruido con los valores de los vectores objetivo y el factor de mutación 
        Vectors_Noise[i].Alpha = Vectors_Objective[C].Alpha + (Factor_Mutation * (Vectors_Objective[B].Alpha - Vectors_Objective[A].Alpha)) 
        Vectors_Noise[i].Beta = Vectors_Objective[C].Beta + (Factor_Mutation * (Vectors_Objective[B].Beta - Vectors_Objective[A].Beta))
        Vectors_Noise[i].Gamma = Vectors_Objective[C].Gamma + (Factor_Mutation * (Vectors_Objective[B].Gamma - Vectors_Objective[A].Gamma))
        Vectors_Noise[i].Rho = Vectors_Objective[C].Rho + (Factor_Mutation * (Vectors_Objective[B].Rho - Vectors_Objective[A].Rho))
        Vectors_Noise[i].Number_Iterations = int(Vectors_Objective[C].Number_Iterations + (Factor_Mutation * (Vectors_Objective[B].Number_Iterations - Vectors_Objective[A].Number_Iterations)))

        Vectors_Noise[i].Type_Evaluation = 2 # Actualiza el tipo de evaluación del vector de ruido a 2 (Ruido)

        if Vectors_Noise[i].Alpha < Settings["Alpha"]["MIN"]: # Si el valor de Alpha es menor al mínimo definido en el archivo de configuración Settings.json
            Vectors_Noise[i].Alpha = Settings["Alpha"]["MIN"] # Asigna el valor mínimo a Alpha 

        elif Vectors_Noise[i].Alpha > Settings["Alpha"]["MAX"]: # Si el valor de Alpha es mayor al máximo definido en el archivo de configuración Settings.json
            Vectors_Noise[i].Alpha = Settings["Alpha"]["MAX"] # Asigna el valor máximo a Alpha

        if Vectors_Noise[i].Beta < Settings["Beta"]["MIN"]: # Si el valor de Beta es menor al mínimo definido en el archivo de configuración Settings.json
            Vectors_Noise[i].Beta = Settings["Beta"]["MIN"] # Asigna el valor mínimo a Beta
        
        elif Vectors_Noise[i].Beta > Settings["Beta"]["MAX"]: # Si el valor de Beta es mayor al máximo definido en el archivo de configuración Settings.json
            Vectors_Noise[i].Beta = Settings["Beta"]["MAX"] # Asigna el valor máximo a Beta

        if Vectors_Noise[i].Gamma < Settings["Gamma"]["MIN"]: # Si el valor de Gamma es menor al mínimo definido en el archivo de configuración Settings.json
            Vectors_Noise[i].Gamma = Settings["Gamma"]["MIN"] # Asigna el valor mínimo a Gamma

        elif Vectors_Noise[i].Gamma > Settings["Gamma"]["MAX"]: # Si el valor de Gamma es mayor al máximo definido en el archivo de configuración Settings.json
            Vectors_Noise[i].Gamma = Settings["Gamma"]["MAX"] # Asigna el valor máximo a Gamma

        if Vectors_Noise[i].Rho < Settings["Rho"]["MIN"]: # Si el valor de Rho es menor al mínimo definido en el archivo de configuración Settings.json
            Vectors_Noise[i].Rho = Settings["Rho"]["MIN"] # Asigna el valor mínimo a Rho
        
        elif Vectors_Noise[i].Rho > Settings["Rho"]["MAX"]: # Si el valor de Rho es mayor al máximo definido en el archivo de configuración Settings.json
            Vectors_Noise[i].Rho = Settings["Rho"]["MAX"] # Asigna el valor máximo a Rho

        if Vectors_Noise[i].Number_Iterations < Settings["N_Iterations"]["MIN"]: # Si el valor de N_Iterations es menor al mínimo definido en el archivo de configuración Settings.json
            Vectors_Noise[i].Number_Iterations = Settings["N_Iterations"]["MIN"] # Asigna el valor mínimo a N_Iterations
 
        elif Vectors_Noise[i].Number_Iterations > Settings["N_Iterations"]["MAX"]: # Si el valor de N_Iterations es mayor al máximo definido en el archivo de configuración Settings.json
            Vectors_Noise[i].Number_Iterations = Settings["N_Iterations"]["MAX"] # Asigna el valor máximo a N_Iterations

# Función para inicializar el vector de prueba en la población 
def Initialize_Test (Vectors_Objective, Vectors_Test, Vectors_Noise, Factor_Crosses):
    Number_Random = 0 # Variable para almacenar un valor aleatorio 

    for i in range(len(Vectors_Test)):
        Number_Random = random.uniform(0, 1) # Asigna un valor aleatorio entre 0 y 1 a la variable Number_Random

        if Number_Random <= Factor_Crosses: # Si el valor de Number_Random es menor o igual al Factor_Cruza
            Vectors_Test[i].Alpha = Vectors_Noise[i].Alpha # Asigna el valor de Alpha del vector de ruido al vector de prueba
        else:
            Vectors_Test[i].Alpha = Vectors_Objective[i].Alpha # Asigna el valor de Alpha del vector objetivo al vector de prueba
        
        Number_Random = random.uniform(0, 1) # Asigna un valor aleatorio entre 0 y 1 a la variable Number_Random

        if Number_Random <= Factor_Crosses: # Si el valor de Number_Random es menor o igual al Factor_Cruza
            Vectors_Test[i].Beta = Vectors_Noise[i].Beta # Asigna el valor de Beta del vector de ruido al vector de prueba
        else:
            Vectors_Test[i].Beta = Vectors_Objective[i].Beta # Asigna el valor de Beta del vector objetivo al vector de prueba

        Number_Random = random.uniform(0, 1) # Asigna un valor aleatorio entre 0 y 1 a la variable Number_Random

        if Number_Random <= Factor_Crosses: # Si el valor de Number_Random es menor o igual al Factor_Cruza
            Vectors_Test[i].Gamma = Vectors_Noise[i].Gamma # Asigna el valor de Gamma del vector de ruido al vector de prueba
        else:
            Vectors_Test[i].Gamma = Vectors_Objective[i].Gamma # Asigna el valor de Gamma del vector objetivo al vector de prueba

        Number_Random = random.uniform(0, 1) # Asigna un valor aleatorio entre 0.1 y 0.9 a la variable Number_Random 

        if Number_Random <= Factor_Crosses: # Si el valor de Number_Random es menor o igual al Factor_Cruza 
            Vectors_Test[i].Rho = Vectors_Noise[i].Rho # Asigna el valor de Rho del vector de ruido al vector de prueba
        else:
            Vectors_Test[i].Rho = Vectors_Objective[i].Rho # Asigna el valor de Rho del vector objetivo al vector de prueba

        Number_Random = random.uniform(0, 1) # Asigna un valor aleatorio entre 0 y 1 a la variable Number_Random

        if Number_Random <= Factor_Crosses: # Si el valor de Number_Random es menor o igual al Factor_Cruza
            Vectors_Test[i].Number_Iterations = Vectors_Noise[i].Number_Iterations # Asigna el valor de N_Iterations del vector de ruido al vector de prueba
        else:
            Vectors_Test[i].Number_Iterations = Vectors_Objective[i].Number_Iterations # Asigna el valor de N_Iterations del vector objetivo al vector de prueba

        Vectors_Test[i].Type_Evaluation = 3 # Actualiza el tipo de evaluación del vector de prueba a 3 (Prueba)

# Función para actualizar el vector objetivo con el vector de prueba si la función objetivo es menor
def Update_Objetive (Vectors_Objective, Vectors_Test):
    for i in range(len(Vectors_Objective)): # Recorre los vectores objetivo y prueba 
        if Vectors_Objective[i].FO > Vectors_Test[i].FO: # Si la función objetivo del vector objetivo es mayor a la función objetivo del vector de prueba
            Vectors_Objective[i].Alpha = Vectors_Test[i].Alpha # Actualiza el valor de Alpha del vector objetivo con el valor de Alpha del vector de prueba
            Vectors_Objective[i].Beta = Vectors_Test[i].Beta # Actualiza el valor de Beta del vector objetivo con el valor de Beta del vector de prueba
            Vectors_Objective[i].Gamma = Vectors_Test[i].Gamma # Actualiza el valor de Gamma del vector objetivo con el valor de Gamma del vector de prueba
            Vectors_Objective[i].Rho = Vectors_Test[i].Rho # Actualiza el valor de Rho del vector objetivo con el valor de Rho del vector de prueba
            Vectors_Objective[i].Number_Iterations = Vectors_Test[i].Number_Iterations # Actualiza el valor de N_Iterations del vector objetivo con el valor de N_Iterations del vector de prueba
            Vectors_Objective[i].FO = Vectors_Test[i].FO # Actualiza la función objetivo del vector objetivo con la función objetivo del vector de prueba
            Vectors_Objective[i].Type_Evaluation = Vectors_Test[i].Type_Evaluation # Actualiza el tipo de evaluación del vector objetivo con el tipo de evaluación del vector de prueba

# Función para evaluar la función objetivo de un vector 
def Evaluate_FO (Vector_: Vector, Index):
    global Settings # Variable global Settings para acceder a los parámetros del archivo de configuración Settings.json
    
    # Llama a la función VRPTWACO con los parámetros del vector y los parámetros de la instancia del archivo de configuración Settings.json 
    FO , Dict_Information = VRPTWACO(Vector_.Number_Iterations, Settings["N_Ants"],Vector_.Alpha, Vector_.Beta, Vector_.Gamma, Vector_.Rho, Vector_.Type_Evaluation, Index, Settings["Instance"])

    Dict_Information["Alpha"] = Vector_.Alpha # Agrega el valor de Alpha al diccionario de información 
    Dict_Information["Beta"] = Vector_.Beta # Agrega el valor de Beta al diccionario de información
    Dict_Information["Gamma"] = Vector_.Gamma # Agrega el valor de Gamma al diccionario de información
    Dict_Information["Rho"] = Vector_.Rho # Agrega el valor de Rho al diccionario de información

    return FO , Dict_Information # Retorna la función objetivo y el diccionario de información

# Función para cargar los parámetros del archivo de configuración Settings.json
def Load_Settings():
    json_file = open("Config/Settings.json", "r")
    Settings = json.load(json_file)
    json_file.close()

    return Settings

# Función para buscar la mejor solución de la población 
def Search_Best_Soluction (List_FO_Objetive, List_Information_Objetive, List_FO_Test, List_Information_Test):
    Best_FO = math.inf # Inicializa la mejor función objetivo con infinito
    Best_Information = {} # Inicializa el mejor diccionario de información vacío
    
    for i in range(len(List_FO_Objetive)): # Recorre la lista de funciones objetivo de la población objetivo
        if List_FO_Objetive[i] < Best_FO: # Si la función objetivo es menor a la mejor función objetivo
            Best_FO = List_FO_Objetive[i] # Actualiza la mejor función objetivo 
            Best_Information = List_Information_Objetive[i] # Actualiza el mejor diccionario de información 

    for i in range(len(List_FO_Test)): # Recorre la lista de funciones objetivo de la población de prueba
        if List_FO_Test[i] < Best_FO: # Si la función objetivo es menor a la mejor función objetivo
            Best_FO = List_FO_Test[i] # Actualiza la mejor función objetivo
            Best_Information = List_Information_Test[i] # Actualiza el mejor diccionario de información
    
    return Best_FO, Best_Information # Retorna la mejor función objetivo y el mejor diccionario de información

# Función para buscar la peor solución de la población 
def Search_Worse_Soluction (List_FO_Objetive, List_Information_Objetive, List_FO_Test, List_Information_Test):
    Worse_FO = -math.inf # Inicializa la peor función objetivo con -infinito 
    Worse_Information = {} # Inicializa el peor diccionario de información vacío
    
    for i in range(len(List_FO_Objetive)): # Recorre la lista de funciones objetivo de la población objetivo
        if List_FO_Objetive[i] > Worse_FO: # Si la función objetivo es mayor a la peor función objetivo
            Worse_FO = List_FO_Objetive[i] # Actualiza la peor función objetivo
            Worse_Information = List_Information_Objetive[i] # Actualiza el peor diccionario de información

    for i in range(len(List_FO_Test)): # Recorre la lista de funciones objetivo de la población de prueba
        if List_FO_Test[i] > Worse_FO: # Si la función objetivo es mayor a la peor función objetivo
            Worse_FO = List_FO_Test[i] # Actualiza la peor función objetivo
            Worse_Information = List_Information_Test[i] # Actualiza el peor diccionario de información
    
    return Worse_FO, Worse_Information # Retorna la peor función objetivo y el peor diccionario de información

# Función para guardar los resultados de la ejecución en un archivo JSON 
def Save_Execution (Time_Execution, Best_Information, Worse_Information):
    global Settings

    Name_Instance = Settings["Instance"]
    Name, Ext = os.path.splitext(Name_Instance)
    Dict_Execution = {
        "Name_Instance": Name,
        "Customers": Settings["Customers"],
        "Vehicles": Settings["N_Ants"],
        "Routes": Settings["N_Ants"],
        "Time_Execution": Time_Execution, # Tiempo de ejecución
        "Best_Execution": Best_Information, # Mejor información de la ruta 
        "Worse_Execution": Worse_Information # Peor información de la ruta
    }

    Name_File = "Results/Execution_" + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".json" # Nombre del archivo con la fecha actual
    json_file = open(Name_File, "w") 
    json.dump(Dict_Execution, json_file, indent=4) # Guarda el diccionario en el archivo JSON
    json_file.close() 

# Función para guardar las rutas en un archivo CSV 
def Save_Routes (Routes: dict): 
    global Settings # Variable global Settings para acceder a los parámetros del archivo de configuración Settings.json

    Name_File = "Results/Routes_" + str(datetime.datetime.now().strftime("%Y-%m-%d")) + ".csv" # Nombre del archivo con la fecha actual
    csv_file = open(Name_File, "w", newline='')
    writer = csv.writer(csv_file)

    for key in Routes.keys(): # Recorre las rutas
        Route = Routes[key]  # Obtenemos la lista de la ruta directamente
        writer.writerow(Route)  # Escribimos la lista directamente como una fila en el archivo CSV

    csv_file.close()

    return Name_File # Retorna el nombre del archivo 


Start_Program = time.time() # Inicializa el tiempo de inicio del programa

Settings = Load_Settings() # Carga los parámetros del archivo de configuración Settings.json

print(Fore.GREEN + "📃 Algorithm Differential Evolution for VRPTW ACO 🐜")

#print(Settings)

Size_Poblation = 20 # Tamaño de la población
Factor_Mutation = 0.5  # Factor de mutación
Factor_Crosses = 0.5 # Factor de cruza
Number_Iterations_MAX = 5 # Número máximo de iteraciones
Number_Current = 0 # Número actual de iteraciones 

Vectors_Objective = [] # Lista de vectores objetivo
Vectors_Noise = [] # Lista de vectores de ruido 
Vectors_Test = [] # Lista de vectores de prueba

for i in range(Size_Poblation): # Recorre el tamaño de la población 
    Vectors_Objective.append(Vector()) # Añade un vector objetivo a la lista de vectores objetivo 
    Vectors_Noise.append(Vector()) # Añade un vector de ruido a la lista de vectores de ruido
    Vectors_Test.append(Vector()) # Añade un vector de prueba a la lista de vectores de prueba

while Number_Current < Number_Iterations_MAX: # Mientras el número actual de iteraciones sea menor al número máximo de iteraciones

    print(Fore.GREEN + "Generation: ", Number_Current)
    total_steps = Size_Poblation * 3  # Tres bucles con tamaño de población para las barras de progreso

    progress_bar = tqdm(total=total_steps, desc="Processing", unit="step") # Inicializa la barra de progreso

    for i in range(Size_Poblation): # Recorre el tamaño de la población
        Vectors_Noise[i].Reset_Vector() # Reinicia el vector de ruido 
        Vectors_Test[i].Reset_Vector() # Reinicia el vector de prueba

    if Number_Current == 0: # Si el número actual de iteraciones es igual a 0
        for i in range(Size_Poblation): # Recorre el tamaño de la población
            Vectors_Objective[i].Reset_Vector() # Reinicia el vector objetivo
            Vectors_Objective[i].Initialize_Objetive() # Inicializa el vector objetivo

    for i in range(Size_Poblation): # Recorre el tamaño de la población
        Vectors_Objective[i].Update_Type_Evaluation(1) # Actualiza el tipo de evaluación del vector objetivo a 1 (Objetivo) 
    
    Initialize_Noise(Vectors_Objective, Vectors_Noise, Factor_Mutation) # Inicializa el ruido en los vectores de la población 
    Initialize_Test(Vectors_Objective, Vectors_Test, Vectors_Noise, Factor_Crosses) # Inicializa el vector de prueba en la población 

    List_FO_Objetive = [] # Lista de funciones objetivo de la población objetivo 
    List_Information_Objetive = [] # Lista de información de la población objetivo 

    for i in range(Size_Poblation): # Recorre el tamaño de la población
        FO , Information_Evaluation = Evaluate_FO(Vectors_Objective[i], i) # Evalúa la función objetivo del vector objetivo
        List_FO_Objetive.append(FO) # Añade la función objetivo a la lista de funciones objetivo
        List_Information_Objetive.append(Information_Evaluation) # Añade la información a la lista de información 
        progress_bar.update(1) # Actualiza la barra de progreso

    List_FO_Noise = [] # Lista de funciones objetivo de la población de ruido
    List_Information_Noise = [] # Lista de información de la población de ruido

    for i in range(Size_Poblation): # Recorre el tamaño de la población
        FO , Information_Evaluation = Evaluate_FO(Vectors_Noise[i], i) # Evalúa la función objetivo del vector de ruido
        List_FO_Noise.append(FO) # Añade la función objetivo a la lista de funciones objetivo
        List_Information_Noise.append(Information_Evaluation) # Añade la información a la lista de información
        progress_bar.update(1) # Actualiza la barra de progreso

    List_FO_Test = [] # Lista de funciones objetivo de la población de prueba
    List_Information_Test = [] # Lista de información de la población de prueba

    for i in range(Size_Poblation): # Recorre el tamaño de la población
        FO , Information_Evaluation = Evaluate_FO(Vectors_Test[i], i) # Evalúa la función objetivo del vector de prueba
        List_FO_Test.append(FO) # Añade la función objetivo a la lista de funciones objetivo
        List_Information_Test.append(Information_Evaluation) # Añade la información a la lista de información
        progress_bar.update(1) # Actualiza la barra de progreso

    Update_Objetive(Vectors_Objective, Vectors_Test) # Actualiza el vector objetivo con el vector de prueba si la función objetivo es menor 

    progress_bar.close() # Cierra la barra de progreso
    print(Fore.GREEN + "Finish Generation 🚗") 

    Number_Current += 1 # Aumenta el número actual de iteraciones



print(Fore.GREEN + "Finish")
#print(List_FO_Objetive)
#print(List_Information_Objetive)

#print(List_FO_Test)
#print(List_Information_Test)

# Busca la mejor solución de la población y guarda los resultados en un archivo JSON 
FO_Best , Information_Best = Search_Best_Soluction(List_FO_Objetive, List_Information_Objetive, List_FO_Test, List_Information_Test)

print(Fore.GREEN + "Best FO: ", FO_Best)
#print(Information_Best)

# Busca la peor solución de la población y guarda los resultados en un archivo JSON 
FO_Worse , Information_Worse = Search_Worse_Soluction(List_FO_Objetive, List_Information_Objetive, List_FO_Test, List_Information_Test)

print(Fore.GREEN + "Worse FO: ", FO_Worse)
#print(Information_Worse)

End_Program = time.time() # Finaliza el tiempo de ejecución del programa
print(Fore.GREEN + "Time Execution: ", End_Program - Start_Program) # Imprime el tiempo de ejecución del programa 

Save_Execution(End_Program - Start_Program, Information_Best, Information_Worse) # Guarda los resultados de la ejecución en un archivo JSON 
Name_File_Best = Save_Routes(Information_Best["Routes"]) # Guarda las rutas en un archivo CSV 

Generate_JSON(Settings["Instance"], Name_File_Best) # Genera el archivo JSON para la visualización en la página web de la mejor ruta 

