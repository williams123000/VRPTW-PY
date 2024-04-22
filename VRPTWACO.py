import sys
import math
import copy
import random
from decimal import Decimal, getcontext
from Modules.TXT_CSV import Convert
from colorama import Fore

class Vehicle:
    def __init__(self, ID, Capacity, Capacity_Remaining, Time_Consumed, Time_MAX):
        self.ID = ID
        self.Capacity = Capacity
        self.Capacity_Remaining = Capacity_Remaining
        self.Time_Consumed = Time_Consumed
        self.Time_MAX = Time_MAX

    def Print_Data(self):
        print("ID: ", self.ID)
        print("Capacity: ", self.Capacity)
        print("Capacity Remaining: ", self.Capacity_Remaining)
        print("Time Consumed: ", self.Time_Consumed)
        print("Time MAX: ", self.Time_MAX)

class Customer:
    def __init__(self, ID, X, Y, Demand, Ready_Time, Due_Date, Service_Time):
        self.ID = ID
        self.X = X
        self.Y = Y
        self.Demand = Demand
        self.Ready_Time = Ready_Time
        self.Due_Date = Due_Date
        self.Service_Time = Service_Time

    def Print_Data(self):
        print("ID: ", self.ID)
        print("X: ", self.X)
        print("Y: ", self.Y)
        print("Demand: ", self.Demand)
        print("Ready Time: ", self.Ready_Time)
        print("Due Date: ", self.Due_Date)
        print("Service Time: ", self.Service_Time)

    
class Instance:
    def __init__(self, Name_Instance, Number_Customers, Number_Vehicles, Capacity_Vehicles):
        self.Name_Instance = Name_Instance
        self.Number_Customers = Number_Customers
        self.Number_Vehicles = Number_Vehicles
        self.Capacity_Vehicles = Capacity_Vehicles

    def Print_Data(self):
        print("Name of Instance: ", self.Name_Instance)
        print("Number of Customers: ", self.Number_Customers)
        print("Number of Vehicles: ", self.Number_Vehicles)
        print("Capacity of Vehicles: ", self.Capacity_Vehicles)

    

class Parameters:
    def __init__(self, Number_Iterations, Number_Ants, Alpha, Beta, Gamma, Rho, Type_Vector, Number_Iteration_Vector):
        self.Number_Iterations = Number_Iterations
        self.Number_Ants = Number_Ants
        self.Alpha = Alpha
        self.Beta = Beta
        self.Gamma = Gamma
        self.Rho = Rho
        self.Type_Vector = Type_Vector
        self.Number_Iteration_Vector = Number_Iteration_Vector

    def Print_Data(self):
        print("Number of Iterations: ", self.Number_Iterations)
        print("Number of Ants: ", self.Number_Ants)
        print("Alpha: ", self.Alpha)
        print("Beta: ", self.Beta)
        print("Gamma: ", self.Gamma)
        print("Rho: ", self.Rho)
        print("Type of Vector: ", self.Type_Vector)
        print("Number of Iteration Vector: ", self.Number_Iteration_Vector)

def Extract_Instance(Name_Instance_):
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
    #Instance_.Print_Data()

    return Instance_

def Create_Customers(Name_Instance_):
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

        Customer_ = Customer(ID, X, Y, Demand, Ready_Time, Due_Date, Service_Time)
        Customers.append(Customer_)

    return Customers

def Create_Vehicles(Instance_ : Instance, Deposit: Customer, Parameters_ : Parameters):
    Vehicles = []

    for i in range(int(Parameters_.Number_Ants)):
        Vehicle_ = Vehicle(i, Instance_.Capacity_Vehicles, 0, 0, Deposit.Due_Date)
        #Vehicle_.Print_Data()
        Vehicles.append(Vehicle_)

    return Vehicles

def Initialize_Pheromones(Instance_ : Instance):
    Pheromone = []

    for i in range(Instance_.Number_Customers):
        Pheromone.append([])

    for i in range(Instance_.Number_Customers):
        for j in range(Instance_.Number_Customers):
            if i == j:
                Pheromone[i].append(0.0)
            else:
                Pheromone[j].append(1.0)

    return Pheromone

def Save_Pheromones(Matrix_Pheromones):
    with open("Pheromones/Pheromones.csv", "w") as file:
        for i in range(len(Matrix_Pheromones)):
            for j in range(len(Matrix_Pheromones[i])):
                if j == len(Matrix_Pheromones[i]) - 1:
                    file.write(str(Matrix_Pheromones[i][j]))
                else:
                    file.write(str(Matrix_Pheromones[i][j]) + ",")
            file.write("\n")

def Calculate_Distance(Origin: Customer, Destination: Customer):
    return ((Destination.X - Origin.X)**2 + (Destination.Y - Origin.Y)**2)**0.5

def Time_Traveled (Distance):
    Velocity = 1
    return Distance/Velocity

def Initialize_Visibility(Customers):
    Visibility = []

    for i in range(len(Customers)): 
        Visibility.append([])

    for i in range(len(Customers)): 
        for j in range(len(Customers)): 
            if i == j:
                Visibility[i].append(0.00)
            else:
                Distance = round(1/(Calculate_Distance(Customers[i], Customers[j])),2)
                Visibility[i].append(Distance)
            

    return Visibility

def Save_Visibility(Visibility):
    with open("Visibility/Visibility.csv", "w") as file:
        for i in range(len(Visibility)):
            for j in range(len(Visibility[i])):
                if j == len(Visibility[i]) - 1:
                    file.write(str(Visibility[i][j]))
                else:
                    file.write(str(Visibility[i][j]) + ",")
            file.write("\n")

def Calculate_Numerator(Origin: Customer, Destination: Customer, Alpha, Beta, Gamma, Matrix_Pheromones, Visibility):
    ID_Origin = Origin.ID
    ID_Destination = Destination.ID

    Value_Visibility = Visibility[ID_Origin][ID_Destination]
    Value_Pheromone = Matrix_Pheromones[ID_Origin][ID_Destination]

    Due_Time = Destination.Due_Date

    Value_Times = 1.0 / Due_Time if Due_Time > 0 else 0.0

    Numerator = (Value_Pheromone**Alpha) * (Value_Visibility**Beta) * (Value_Times**Gamma)

    return Numerator

def Define_Probabilities(Numerators, Denominator):
    Probabilities = []

    for i in range(len(Numerators)):
        if i == 0:
            Probabilities.append(Numerators[i]/Denominator)
        else:
            Probabilities.append(Probabilities[i-1] + (Numerators[i]/Denominator))
        
    return Probabilities

def Select_Probability(Probabilities):
    Random = random.random() 

    for index in range(len(Probabilities)):
        if Random < Probabilities[index]:
            break

    return index


def Calculate_Probabilities(Ant, Customers , List_Taboo, Vehicle_: Vehicle, Matrix_Pheromones, Visibility, Params: Parameters):    
    Origin = copy.deepcopy(Ant[-1])

    Possible_Destinations = []

    for Destination in Customers:
        if Destination not in List_Taboo:

            Distance_Traveled = Calculate_Distance(Origin, Destination)
            Time_Traveled_ = Time_Traveled(Distance_Traveled)
            Distance_Traveled_Deposit = Calculate_Distance(Destination, Customers[0])
            Time_Traveled_Deposit = Time_Traveled(Distance_Traveled_Deposit)

            if Vehicle_.Time_Consumed + Time_Traveled_ >= Destination.Ready_Time and Vehicle_.Time_Consumed + Time_Traveled_  <= Destination.Due_Date:
                if Vehicle_.Capacity_Remaining + Destination.Demand <= Vehicle_.Capacity:
                    if Vehicle_.Time_Consumed + Time_Traveled_ + Destination.Service_Time + Time_Traveled_Deposit <= Vehicle_.Time_MAX:
                        Possible_Destinations.append(Destination)

    if not Possible_Destinations:
        #print("No possible destinations")
        return False
    else:

        Numerators = []
        Denominator = 0.0

        for Destination in Possible_Destinations:
            Numerator = Calculate_Numerator(Origin, Destination, float(Params.Alpha), float(Params.Beta), float(Params.Gamma) , Matrix_Pheromones, Visibility)
            Numerators.append(Numerator)
            Denominator += Numerator

        Probabilities = Define_Probabilities(Numerators, Denominator)
        
        Index_Select = Select_Probability(Probabilities)
        
        Destination_Selected = Possible_Destinations[Index_Select]

        Ant.append(Destination_Selected)
        List_Taboo.append(Destination_Selected)

        Distance_Traveled = Calculate_Distance(Origin, Destination_Selected)
        Time_Traveled_ = Time_Traveled(Distance_Traveled)

        Vehicle_.Time_Consumed = Vehicle_.Time_Consumed + Time_Traveled_ + Destination_Selected.Service_Time
        
        Vehicle_.Capacity_Remaining += Destination_Selected.Demand

        return True

def Print_Ants(Ants):
    for Ant in Ants:
        for Customer_ in Ant:
            print(Customer_.ID, end=" ")
        print()

    
def Calculate_Distance_Ant(Ant):
    Distance = 0.0

    for i in range(len(Ant)-1):
        Distance += Calculate_Distance(Ant[i], Ant[i+1])

    return Distance

def Update_Pheromone(Delta, Rho, Ants, Matrix_Pheromones):
    for i in range(len(Matrix_Pheromones)):
        for j in range(len(Matrix_Pheromones[i])):
            Matrix_Pheromones[i][j] = (1 - Rho) * Matrix_Pheromones[i][j]

    
    for Ant in Ants:
        for i in range(len(Ant)-1):
            ID_Origin = Ant[i].ID
            ID_Destination = Ant[i+1].ID
            Matrix_Pheromones[ID_Origin][ID_Destination] += Delta

    for i in range(len(Matrix_Pheromones)):
        for j in range(len(Matrix_Pheromones[i])):
            if i == j:
                Matrix_Pheromones[i][j] = 0.0

    return Matrix_Pheromones
    
def Update_Dicc_Routes(Dicc_Routes, Ants, FO, Number_Iteration):
    i = 0
    Dict_Iteration = {}
    Dict = {}
    Dict_Iteration["FO"] = FO

    for Ant in Ants:
        Dict["Route " + str(i)] = []
        for Customer_ in Ant:
            Dict["Route " + str(i)].append(Customer_.ID)

        i += 1

    Dict_Iteration["Routes"] = Dict

    Dicc_Routes["Iteration " + str(Number_Iteration)] = Dict_Iteration

def Select_Best_Solution_Dict(Dict):
    Best_Solution = math.inf
    Dict_Best_Solution = {}

    for key in Dict:
        if Dict[key]["FO"] < Best_Solution:
            Dict_Best_Solution = Dict[key]
            Best_Solution = Dict[key]["FO"]

    return Dict_Best_Solution
    

def Save_Solution_CSV(Dict):
    
    with open("Solutions/Solution.csv", "w") as file:
        
        file.write(str(Dict["FO"])+"\n")
        for key in Dict["Routes"]:
            for ID in range(len(Dict["Routes"][key])):
                if ID == len(Dict["Routes"][key])-1:
                    file.write(str(Dict["Routes"][key][ID]) + "\n")
                else:
                    file.write(str(Dict["Routes"][key][ID]) + ",")

def VRPTWACO (Number_Iterations_ , Number_Ants_ , Alpha_ , Beta_ , Gamma_ , Rho_ , Type_Vector_ , Number_Iteration_Vector_ , Name_Instance_):
    print(Fore.BLUE + "VRPTWACO")
    Params = Parameters(Number_Iterations_, Number_Ants_, Alpha_, Beta_, Gamma_, Rho_, Type_Vector_, Number_Iteration_Vector_)
    Params.Print_Data()

    Instance_ = Extract_Instance(Name_Instance_)

    Customers = Create_Customers( Name_Instance_)

    Vehicles = Create_Vehicles(Instance_, Customers[0], Params)

    Matrix_Pheromones = Initialize_Pheromones(Instance_)

    Save_Pheromones(Matrix_Pheromones)

    Visibility = Initialize_Visibility(Customers)

    Save_Visibility(Visibility)

    Best_Distance = math.inf

    Best_Solution_Route = []

    Params.Number_Iterations = int(Params.Number_Iterations)

    Number_Iteration = 0

    Dicc_Routes = {}

    while Number_Iteration < Params.Number_Iterations: 
        
        List_Taboo = []
        
        Vehicles_ = copy.deepcopy(Vehicles)

        Ants = [] # Lista de hormigas que son las rutas

        for Ant in range(int(Params.Number_Ants)):
            Ants.append([])
            Ants[Ant].append(Customers[0]) # Se añade el depósito a cada una de la ruta

        List_Taboo.append(Customers[0]) # Se añade el depósito a la lista de tabú

        Number_Try = 0

        Number_Ants = 0

        Try = True

        Number_Try = 0

        for j in range(100):
            
            

            if Try == False:
                break

            while True:
                Ant_Gen = random.randint(0,9)

                # Retorna True si se añadió un cliente a la ruta de la hormiga y False si no se añadió
                Result = Calculate_Probabilities(Ants[Ant_Gen], Customers, List_Taboo, Vehicles_[Ant_Gen], Matrix_Pheromones, Visibility, Params)

                if not Result:
                    Number_Try += 1

                    if Number_Try == 10: # Si la hormiga no puede añadir un cliente a la ruta, se cambia de hormiga
                        Try = False
                        
                        break       
                else:
                    Number_Try = 0 # Si se añadió un cliente a la ruta, se reinicia el contador de intentos
                    Try = True

        if len(List_Taboo) == Instance_.Number_Customers:

            for Ant in Ants:
                Ant.append(Customers[0])

            Distance_Ants = []
            for Ant in Ants:
                Distance_Ants.append(Calculate_Distance_Ant(Ant))

            FO = sum(Distance_Ants)

            if FO < Best_Distance:
                Best_Distance = FO
                Best_Solution_Route = Ants

            print("Best Distance: ", Best_Distance)

            Number_Iteration += 1

            Delta = 1.0 / Best_Distance

            Matrix_Pheromones = Update_Pheromone(Delta, float(Params.Rho), Ants, Matrix_Pheromones)

            Save_Pheromones(Matrix_Pheromones)

            Update_Dicc_Routes(Dicc_Routes, Ants, FO, Number_Iteration)

            

        if not Try:      
            Number_Iteration += 1
            Params.Number_Iterations += 1
            continue
        

    Best_Solution = Select_Best_Solution_Dict(Dicc_Routes)
    Save_Solution_CSV(Best_Solution)

    return Best_Distance, Best_Solution