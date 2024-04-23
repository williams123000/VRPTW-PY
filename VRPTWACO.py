"""
Autor: Williams Chan Pescador
Descripción: Script principal que contiene la implementación del algoritmo VRPTWACO. Este algoritmo se encarga de resolver el problema de ruteo de vehículos con ventanas de tiempo y capacidad.
Utiliza la metaheurística de colonia de hormigas para encontrar la mejor solución al problema.
De las instancias de prueba de Solomon, se utilizan los archivos .txt para extraer los datos y convertirlos a un formato .csv.
Se utilizan los archivos .csv para extraer los datos de la instancia y crear las rutas de los vehículos.
Algoritmo VRPTWACO: Vehicle Routing Problem with Time Windows and Ant Colony Optimization

"""

import sys
import math
import copy
import random
from decimal import Decimal, getcontext 
from Modules.TXT_CSV import Convert # Importar la función Convert del script TXT_CSV.py
from colorama import Fore

# Clase para los vehículos 
class Vehicle:
    # Constructor de la clase
    def __init__(self, ID, Capacity, Capacity_Remaining, Time_Consumed, Time_MAX):
        self.ID = ID # Identificador del vehículo
        self.Capacity = Capacity # Capacidad del vehículo
        self.Capacity_Remaining = Capacity_Remaining # Capacidad restante del vehículo
        self.Time_Consumed = Time_Consumed # Tiempo consumido por el vehículo
        self.Time_MAX = Time_MAX # Tiempo máximo del vehículo

    # Método para imprimir los datos del vehículo
    def Print_Data(self):
        print("ID: ", self.ID)
        print("Capacity: ", self.Capacity)
        print("Capacity Remaining: ", self.Capacity_Remaining)
        print("Time Consumed: ", self.Time_Consumed)
        print("Time MAX: ", self.Time_MAX)

# Clase para los clientes
class Customer:
    # Constructor de la clase
    def __init__(self, ID, X, Y, Demand, Ready_Time, Due_Date, Service_Time):
        self.ID = ID # Identificador del cliente
        self.X = X # Coordenada X del cliente
        self.Y = Y # Coordenada Y del cliente
        self.Demand = Demand # Demanda del cliente
        self.Ready_Time = Ready_Time # Tiempo de inicio de la ventana de tiempo
        self.Due_Date = Due_Date # Tiempo final de la ventana de tiempo
        self.Service_Time = Service_Time # Tiempo de servicio del cliente

    # Método para imprimir los datos del cliente
    def Print_Data(self):
        print("ID: ", self.ID)
        print("X: ", self.X)
        print("Y: ", self.Y)
        print("Demand: ", self.Demand)
        print("Ready Time: ", self.Ready_Time)
        print("Due Date: ", self.Due_Date)
        print("Service Time: ", self.Service_Time)

# Clase para las instancias
class Instance:
    # Constructor de la clase
    def __init__(self, Name_Instance, Number_Customers, Number_Vehicles, Capacity_Vehicles):
        self.Name_Instance = Name_Instance # Nombre de la instancia
        self.Number_Customers = Number_Customers # Número de clientes
        self.Number_Vehicles = Number_Vehicles # Número de vehículos
        self.Capacity_Vehicles = Capacity_Vehicles # Capacidad de los vehículos

    # Método para imprimir los datos de la instancia
    def Print_Data(self):
        print("Name of Instance: ", self.Name_Instance)
        print("Number of Customers: ", self.Number_Customers)
        print("Number of Vehicles: ", self.Number_Vehicles)
        print("Capacity of Vehicles: ", self.Capacity_Vehicles)

    
# Clase para los parámetros
class Parameters:
    # Constructor de la clase
    def __init__(self, Number_Iterations, Number_Ants, Alpha, Beta, Gamma, Rho, Type_Vector, Number_Iteration_Vector):
        self.Number_Iterations = Number_Iterations # Número de iteraciones
        self.Number_Ants = Number_Ants # Número de hormigas
        self.Alpha = Alpha # Parámetro Alpha
        self.Beta = Beta # Parámetro Beta
        self.Gamma = Gamma # Parámetro Gamma
        self.Rho = Rho # Parámetro Rho
        self.Type_Vector = Type_Vector # Tipo de vector 
        self.Number_Iteration_Vector = Number_Iteration_Vector # Número de iteraciones del vector

    # Método para imprimir los datos de los parámetros
    def Print_Data(self):
        print("Number of Iterations: ", self.Number_Iterations)
        print("Number of Ants: ", self.Number_Ants)
        print("Alpha: ", self.Alpha)
        print("Beta: ", self.Beta)
        print("Gamma: ", self.Gamma)
        print("Rho: ", self.Rho)
        print("Type of Vector: ", self.Type_Vector)
        print("Number of Iteration Vector: ", self.Number_Iteration_Vector)

# Función para extraer los datos de la instancia
def Extract_Instance(Name_Instance_):
    # Convertir el archivo .txt a .csv para poder leer los datos de la instancia en un formato más amigable y manipulable 
    Convert(Name_Instance_)


    # Abrir el archivo
    with open("Instances/" + str(Name_Instance_), "r") as file:
        lines = file.readlines()

    # Extraer los datos de la primera y última línea
    Name_Instance = lines[0].strip()
    Line_Capacity = lines[1].strip().split(",")
    Num_Vehicles = int(Line_Capacity[0])
    Capacity = int(Line_Capacity[1])

    # Extraer los datos de la última línea
    Last_Line = lines[-1].strip().split(",")
    Num_Customers = int(Last_Line[0])

    # Crear la instancia
    Instance_ = Instance(Name_Instance, Num_Customers+1, Num_Vehicles, Capacity) # +1 para incluir el depósito

    return Instance_

# Función para crear los clientes de la instancia 
def Create_Customers(Name_Instance_):
    # Convertir el archivo .txt a .csv para poder leer los datos de la instancia en un formato más amigable y manipulable
    Convert(Name_Instance_) 

    # Abrir el archivo
    with open("Instances/" + str(Name_Instance_) , "r") as file:
        lines = file.readlines()

    Customers = []

    for i in range(2, len(lines)):
        Line = lines[i].strip().split(",")
        ID = int(Line[0])
        X = int(Line[1])
        Y = int(Line[2])
        Demand = int(Line[3])
        Ready_Time = int(Line[4])
        Due_Date = int(Line[5])
        Service_Time = int(Line[6])

        Customer_ = Customer(ID, X, Y, Demand, Ready_Time, Due_Date, Service_Time) # Crear el cliente con los datos extraídos de la instancia 
        Customers.append(Customer_) # Añadir el cliente a la lista de clientes

    return Customers

# Función para crear los vehículos de la instancia 
def Create_Vehicles(Instance_ : Instance, Deposit: Customer, Parameters_ : Parameters):
    Vehicles = [] # Lista de vehículos 
    for i in range(int(Parameters_.Number_Ants)):
        Vehicle_ = Vehicle(i, Instance_.Capacity_Vehicles, 0, 0, Deposit.Due_Date) # Crear el vehículo con los datos extraídos de la instancia
        #Vehicle_.Print_Data()
        Vehicles.append(Vehicle_) # Añadir el vehículo a la lista de vehículos

    return Vehicles

# Función para inicializar las feromonas 
def Initialize_Pheromones(Instance_ : Instance):
    Pheromone = [] # Matriz de feromonas

    for i in range(Instance_.Number_Customers):
        Pheromone.append([]) # Añadir una lista vacía a la matriz de feromonas

    for i in range(Instance_.Number_Customers):
        for j in range(Instance_.Number_Customers):
            if i == j:
                Pheromone[i].append(0.0) # Añadir 0.0 si el origen y el destino son iguales
            else:
                Pheromone[j].append(1.0) # Añadir 1.0 si el origen y el destino son diferentes

    return Pheromone

# Función para guardar las feromonas en un archivo CSV
def Save_Pheromones(Matrix_Pheromones):
    with open("Pheromones/Pheromones.csv", "w") as file:
        for i in range(len(Matrix_Pheromones)):
            for j in range(len(Matrix_Pheromones[i])):
                if j == len(Matrix_Pheromones[i]) - 1:
                    file.write(str(Matrix_Pheromones[i][j]))
                else:
                    file.write(str(Matrix_Pheromones[i][j]) + ",")
            file.write("\n")

# Función para calcular la distancia entre dos clientes
def Calculate_Distance(Origin: Customer, Destination: Customer):
    return ((Destination.X - Origin.X)**2 + (Destination.Y - Origin.Y)**2)**0.5

# Función para calcular el tiempo de viaje entre dos clientes
def Time_Traveled (Distance):
    Velocity = 1
    return Distance/Velocity

# Función para inicializar la visibilidad
def Initialize_Visibility(Customers):
    Visibility = [] # Matriz de visibilidad

    for i in range(len(Customers)): 
        Visibility.append([]) # Añadir una lista vacía a la matriz de visibilidad

    for i in range(len(Customers)): 
        for j in range(len(Customers)): 
            if i == j:
                Visibility[i].append(0.00) # Añadir 0.0 si el origen y el destino son iguales
            else:
                Distance = round(1/(Calculate_Distance(Customers[i], Customers[j])),2) # Calcular la distancia entre los clientes y redondearla a 2 decimales 
                Visibility[i].append(Distance) # Añadir la distancia a la matriz de visibilidad
            

    return Visibility

# Función para guardar la visibilidad en un archivo CSV
def Save_Visibility(Visibility):
    with open("Visibility/Visibility.csv", "w") as file:
        for i in range(len(Visibility)):
            for j in range(len(Visibility[i])):
                if j == len(Visibility[i]) - 1:
                    file.write(str(Visibility[i][j])) 
                else:
                    file.write(str(Visibility[i][j]) + ",")
            file.write("\n")

# Función para calcular el numerador de la probabilidad de selección
def Calculate_Numerator(Origin: Customer, Destination: Customer, Alpha, Beta, Gamma, Matrix_Pheromones, Visibility):
    ID_Origin = Origin.ID # ID del origen
    ID_Destination = Destination.ID # ID del destino 

    Value_Visibility = Visibility[ID_Origin][ID_Destination] # Visibilidad entre el origen y el destino
    Value_Pheromone = Matrix_Pheromones[ID_Origin][ID_Destination] # Feromona entre el origen y el destino

    Due_Time = Destination.Due_Date # Tiempo final de la ventana de tiempo del destino 

    Value_Times = 1.0 / Due_Time if Due_Time > 0 else 0.0 # Tiempo de viaje entre el origen y el destino 

    Numerator = (Value_Pheromone**Alpha) * (Value_Visibility**Beta) * (Value_Times**Gamma) # Calcular el numerador de la probabilidad de selección

    return Numerator

# Función para definir las probabilidades de selección
def Define_Probabilities(Numerators, Denominator):
    Probabilities = [] # Lista de probabilidades

    for i in range(len(Numerators)):
        if i == 0:
            Probabilities.append(Numerators[i]/Denominator) # Añadir la probabilidad a la lista de probabilidades si es el primer elemento 
        else:
            Probabilities.append(Probabilities[i-1] + (Numerators[i]/Denominator)) # Añadir la probabilidad a la lista de probabilidades si no es el primer elemento 
        
    return Probabilities

# Función para seleccionar una probabilidad 
def Select_Probability(Probabilities):
    Random = random.random()  # Número aleatorio entre 0 y 1

    for index in range(len(Probabilities)):
        if Random < Probabilities[index]: # Si el número aleatorio es menor que la probabilidad, se selecciona el índice
            break

    return index

# Función para calcular las probabilidades de selección de los clientes 
def Calculate_Probabilities(Ant, Customers , List_Taboo, Vehicle_: Vehicle, Matrix_Pheromones, Visibility, Params: Parameters):    
    Origin = copy.deepcopy(Ant[-1]) # Copiar el último cliente de la ruta de la hormiga

    Possible_Destinations = [] # Lista de posibles destinos

    for Destination in Customers: # Recorrer los clientes
        if Destination not in List_Taboo: # Si el cliente no está en la lista de tabú

            Distance_Traveled = Calculate_Distance(Origin, Destination) # Calcular la distancia entre el origen y el destino
            Time_Traveled_ = Time_Traveled(Distance_Traveled) # Calcular el tiempo de viaje entre el origen y el destino 
            Distance_Traveled_Deposit = Calculate_Distance(Destination, Customers[0]) # Calcular la distancia entre el destino y el depósito
            Time_Traveled_Deposit = Time_Traveled(Distance_Traveled_Deposit) # Calcular el tiempo de viaje entre el destino y el depósito

            # Verificar si el tiempo consumido por el vehículo más el tiempo de viaje entre el origen y el destino es mayor o igual 
            # al tiempo de inicio de la ventana de tiempo del destino y si el tiempo consumido por el vehículo más el tiempo de viaje 
            # entre el origen y el destino es menor o igual al tiempo final de la ventana de tiempo del destino
            if Vehicle_.Time_Consumed + Time_Traveled_ >= Destination.Ready_Time and Vehicle_.Time_Consumed + Time_Traveled_  <= Destination.Due_Date: 
                # Verificar si la capacidad restante del vehículo más la demanda del destino es menor o igual a la capacidad del vehículo
                if Vehicle_.Capacity_Remaining + Destination.Demand <= Vehicle_.Capacity: 
                    # Verificar si se cumple la restricción de tiempo máximo del vehículo para llegar al destino y regresar al depósito
                    if Vehicle_.Time_Consumed + Time_Traveled_ + Destination.Service_Time + Time_Traveled_Deposit <= Vehicle_.Time_MAX:
                        Possible_Destinations.append(Destination) # Añadir el destino a la lista de posibles destinos

    if not Possible_Destinations: # Si no hay posibles destinos retornar False
        #print("No possible destinations")
        return False
    else: # Si hay posibles destinos

        Numerators = [] # Lista de numeradores
        Denominator = 0.0

        for Destination in Possible_Destinations: # Recorrer los posibles destinos
            # Calcular el numerador de la probabilidad de selección y añadirlo a la lista de numeradores 
            Numerator = Calculate_Numerator(Origin, Destination, float(Params.Alpha), float(Params.Beta), float(Params.Gamma) , Matrix_Pheromones, Visibility)
            Numerators.append(Numerator)
            Denominator += Numerator

        Probabilities = Define_Probabilities(Numerators, Denominator) # Definir las probabilidades de selección 
        
        Index_Select = Select_Probability(Probabilities) # Seleccionar una probabilidad 
        
        Destination_Selected = Possible_Destinations[Index_Select] # Seleccionar el destino con la probabilidad seleccionada 

        Ant.append(Destination_Selected) # Añadir el destino a la ruta de la hormiga 
        List_Taboo.append(Destination_Selected) # Añadir el destino a la lista de tabú 

        Distance_Traveled = Calculate_Distance(Origin, Destination_Selected) # Calcular la distancia entre el origen y el destino que se seleccionó
        Time_Traveled_ = Time_Traveled(Distance_Traveled) # Calcular el tiempo de viaje entre el origen y el destino que se seleccionó

        Vehicle_.Time_Consumed = Vehicle_.Time_Consumed + Time_Traveled_ + Destination_Selected.Service_Time # Actualizar el tiempo consumido por el vehículo 
         
        Vehicle_.Capacity_Remaining += Destination_Selected.Demand # Actualizar la capacidad restante del vehículo

        # Retornar True si se añadió un cliente a la ruta de la hormiga
        return True

# Función para imprimir las rutas de las hormigas
def Print_Ants(Ants):
    for Ant in Ants:
        for Customer_ in Ant:
            print(Customer_.ID, end=" ")
        print()

# Función para calcular la distancia de la ruta de la hormiga
def Calculate_Distance_Ant(Ant):
    Distance = 0.0

    for i in range(len(Ant)-1):
        Distance += Calculate_Distance(Ant[i], Ant[i+1]) # Calcular la distancia entre los clientes de la ruta de la hormiga

    return Distance

# Función para actualizar las feromonas
def Update_Pheromone(Delta, Rho, Ants, Matrix_Pheromones):
    for i in range(len(Matrix_Pheromones)):
        for j in range(len(Matrix_Pheromones[i])):
            Matrix_Pheromones[i][j] = (1 - Rho) * Matrix_Pheromones[i][j] # Actualizar las feromonas con la fórmula dada

    
    for Ant in Ants:
        for i in range(len(Ant)-1):
            ID_Origin = Ant[i].ID # ID del origen
            ID_Destination = Ant[i+1].ID # ID del destino
            Matrix_Pheromones[ID_Origin][ID_Destination] += Delta # Actualizar las feromonas con el valor de Delta donde el origen y el destino son los clientes de la ruta de la hormiga

    for i in range(len(Matrix_Pheromones)):
        for j in range(len(Matrix_Pheromones[i])):
            if i == j:
                Matrix_Pheromones[i][j] = 0.0 # Añadir 0.0 si el origen y el destino son iguales 

    return Matrix_Pheromones

# Función para actualizar el diccionario de rutas 
def Update_Dicc_Routes(Dicc_Routes, Ants, FO, Number_Iteration):
    i = 0
    Dict_Iteration = {} # Diccionario de la iteración
    Dict = {} # Diccionario de las rutas
    Dict_Iteration["FO"] = FO # Añadir la función objetivo al diccionario de la iteración

    for Ant in Ants:
        Dict["Route " + str(i)] = [] # Añadir una lista vacía al diccionario de las rutas
        for Customer_ in Ant:
            Dict["Route " + str(i)].append(Customer_.ID) # Añadir el ID del cliente a la lista de la ruta de la hormiga 

        i += 1

    Dict_Iteration["Routes"] = Dict # Añadir el diccionario de las rutas al diccionario de la iteración 

    Dicc_Routes["Iteration " + str(Number_Iteration)] = Dict_Iteration # Añadir el diccionario de la iteración al diccionario de rutas 

# Función para seleccionar la mejor solución del diccionario de rutas
def Select_Best_Solution_Dict(Dict):
    Best_Solution = math.inf # Numero infinito 
    Dict_Best_Solution = {} # Diccionario de la mejor solución 

    for key in Dict:
        if Dict[key]["FO"] < Best_Solution: # Si la función objetivo de la iteración es menor que la mejor solución
            Dict_Best_Solution = Dict[key] # Actualizar la mejor solución
            Best_Solution = Dict[key]["FO"] # Actualizar la mejor solución 

    return Dict_Best_Solution
    
# Función para guardar la mejor solución en un archivo CSV
def Save_Solution_CSV(Dict):
    
    with open("Solutions/Solution.csv", "w") as file:
        file.write(str(Dict["FO"])+"\n")
        for key in Dict["Routes"]:
            for ID in range(len(Dict["Routes"][key])):
                if ID == len(Dict["Routes"][key])-1:
                    file.write(str(Dict["Routes"][key][ID]) + "\n")
                else:
                    file.write(str(Dict["Routes"][key][ID]) + ",")

# Función principal del algoritmo VRPTWACO 
def VRPTWACO (Number_Iterations_ , Number_Ants_ , Alpha_ , Beta_ , Gamma_ , Rho_ , Type_Vector_ , Number_Iteration_Vector_ , Name_Instance_):
    
    # Crear los parámetros con los datos ingresados por el script Differential_Evolution.py
    Params = Parameters(Number_Iterations_, Number_Ants_, Alpha_, Beta_, Gamma_, Rho_, Type_Vector_, Number_Iteration_Vector_)
    #Params.Print_Data()

    
    Instance_ = Extract_Instance(Name_Instance_) # Extraer los datos de la instancia

    Customers = Create_Customers( Name_Instance_) # Crear los clientes de la instancia 

    Vehicles = Create_Vehicles(Instance_, Customers[0], Params) # Crear los vehículos de la instancia 

    Matrix_Pheromones = Initialize_Pheromones(Instance_) # Inicializar las feromonas

    Save_Pheromones(Matrix_Pheromones) # Guardar las feromonas en un archivo CSV

    Visibility = Initialize_Visibility(Customers) # Inicializar la visibilidad

    Save_Visibility(Visibility) # Guardar la visibilidad en un archivo CSV

    Best_Distance = math.inf # Numero infinito 

    Best_Solution_Route = [] # Lista de la mejor solución de la ruta

    Params.Number_Iterations = int(Params.Number_Iterations) # Convertir el número de iteraciones a entero 

    Number_Iteration = 0

    Dicc_Routes = {} # Diccionario de las rutas

    while Number_Iteration < Params.Number_Iterations: # Mientras el número de iteraciones sea menor al número de iteraciones ingresado por el script Differential_Evolution.py
        
        List_Taboo = [] # Lista de tabú 
        
        Vehicles_ = copy.deepcopy(Vehicles) # Copiar los vehículos 

        Ants = [] # Lista de hormigas que son las rutas

        for Ant in range(int(Params.Number_Ants)): # Recorrer el número de hormigas
            Ants.append([])
            Ants[Ant].append(Customers[0]) # Se añade el depósito a cada una de la ruta

        List_Taboo.append(Customers[0]) # Se añade el depósito a la lista de tabú

        Number_Try = 0 # Contador de intentos 

        Number_Ants = 0

        Try = True # Variable booleana para verificar si se añadió un cliente a la ruta de la hormiga

        Number_Try = 0 

        for j in range(100): # Mientras el número de intentos sea menor a 100 

            if Try == False: # Si no se añadió un cliente a la ruta de la hormiga 
                break

            while True: # Mientras sea verdadero 
                Ant_Gen = random.randint(0,2) # Se selecciona una hormiga aleatoria 

                # Retorna True si se añadió un cliente a la ruta de la hormiga y False si no se añadió
                Result = Calculate_Probabilities(Ants[Ant_Gen], Customers, List_Taboo, Vehicles_[Ant_Gen], Matrix_Pheromones, Visibility, Params)

                if not Result: # Si no se añadió un cliente a la ruta de la hormiga
                    Number_Try += 1 # Se incrementa el contador de intentos

                    if Number_Try == 10: # Si la hormiga no puede añadir un cliente a la ruta, se cambia de hormiga
                        Try = False
                        
                        break       
                else:
                    Number_Try = 0 # Si se añadió un cliente a la ruta, se reinicia el contador de intentos
                    Try = True

        if len(List_Taboo) == Instance_.Number_Customers: # Si la lista de tabú es igual al número de clientes de la instancia 

            for Ant in Ants:
                Ant.append(Customers[0]) # Se añade el depósito al final de la ruta de la hormiga

            Distance_Ants = [] # Lista de distancias de las rutas de las hormigas

            for Ant in Ants: # Recorrer las rutas de las hormigas
                Distance_Ants.append(Calculate_Distance_Ant(Ant)) # Calcular la distancia de la ruta de la hormiga y añadirla a la lista de distancias de las rutas de las hormigas 

            FO = sum(Distance_Ants) # Calcular la función objetivo sumando las distancias de las rutas de las hormigas 

            if FO < Best_Distance: # Si la función objetivo es menor que la mejor distancia
                Best_Distance = FO # Actualizar la mejor distancia 
                Best_Solution_Route = Ants

            #print("Best Distance: ", Best_Distance)

            Number_Iteration += 1 # Incrementar el número de iteraciones 

            Delta = 1.0 / Best_Distance # Calcular el valor de Delta con respecto a la mejor distancia

            Matrix_Pheromones = Update_Pheromone(Delta, float(Params.Rho), Ants, Matrix_Pheromones) # Actualizar las feromonas después de cada iteración 

            Save_Pheromones(Matrix_Pheromones) # Guardar las feromonas en un archivo CSV

            Update_Dicc_Routes(Dicc_Routes, Ants, FO, Number_Iteration) # Actualizar el diccionario de rutas 

            

        if not Try: # Si no se añadió un cliente a la ruta de la hormiga
            Number_Iteration += 1 # Incrementar el número de iteraciones
            Params.Number_Iterations += 1 # Incrementar el número de iteraciones
            continue # Continuar con la siguiente iteración
        

    Best_Solution = Select_Best_Solution_Dict(Dicc_Routes) # Seleccionar la mejor solución del diccionario de rutas
    Save_Solution_CSV(Best_Solution) # Guardar la mejor solución en un archivo CSV

    return Best_Distance, Best_Solution # Retornar la mejor distancia y la mejor solución 