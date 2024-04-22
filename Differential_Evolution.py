import random
import json
import math
from VRPTWACO import VRPTWACO
from colorama import Fore
import time
import datetime
from tqdm import tqdm

class Vector:
    def __init__(self):
        self.Alpha = 0.0
        self.Beta = 0.0
        self.Gamma = 0.0
        self.Rho = 0.0
        self.Number_Iterations = 0
        self.FO = 0.0
        self.Type_Evaluation = 0

    def Reset_Vector(self):
        self.Alpha = 0.0
        self.Beta = 0.0
        self.Gamma = 0.0
        self.Rho = 0.0
        self.Number_Iterations = 0
        self.FO = 0.0
        self.Type_Evaluation = 0

    def Print_Vector(self):
        print("Alpha: ", self.Alpha)
        print("Beta: ", self.Beta)
        print("Gamma: ", self.Gamma)
        print("Rho: ", self.Rho)
        print("Number_Iterations: ", self.Number_Iterations)
        print("FO: ", self.FO)
        print("Type_Evaluation: ", self.Type_Evaluation)

    def Initialize_Objetive (self):
        global Settings

        self.Alpha = random.uniform(Settings["Alpha"]["MIN"], Settings["Alpha"]["MAX"])
        self.Beta = random.uniform(Settings["Beta"]["MIN"], Settings["Beta"]["MAX"])
        self.Gamma = random.uniform(Settings["Gamma"]["MIN"], Settings["Gamma"]["MAX"])
        self.Rho = random.uniform(Settings["Rho"]["MIN"], Settings["Rho"]["MAX"])
        self.Number_Iterations = random.randint(Settings["N_Iterations"]["MIN"], Settings["N_Iterations"]["MAX"])
        self.FO = 0.0
        self.Type_Evaluation = 1


    
    def Update_Type_Evaluation(self, Type_Evaluation):
        self.Type_Evaluation = Type_Evaluation


def Initialize_Noise (Vectors_Objective, Vectors_Noise, Factor_Mutation):
    A = 0
    B = 0
    C = 0

    for i in range(len(Vectors_Noise)):
        A = 0
        B = 0
        C = 0

        while A == B or A == C or B == C :
            A = random.randint(0, len(Vectors_Objective)-1)
            B = random.randint(0, len(Vectors_Objective)-1)
            C = random.randint(0, len(Vectors_Objective)-1)

        Vectors_Noise[i].Alpha = Vectors_Objective[C].Alpha + (Factor_Mutation * (Vectors_Objective[B].Alpha - Vectors_Objective[A].Alpha))
        Vectors_Noise[i].Beta = Vectors_Objective[C].Beta + (Factor_Mutation * (Vectors_Objective[B].Beta - Vectors_Objective[A].Beta))
        Vectors_Noise[i].Gamma = Vectors_Objective[C].Gamma + (Factor_Mutation * (Vectors_Objective[B].Gamma - Vectors_Objective[A].Gamma))
        Vectors_Noise[i].Rho = Vectors_Objective[C].Rho + (Factor_Mutation * (Vectors_Objective[B].Rho - Vectors_Objective[A].Rho))
        Vectors_Noise[i].Number_Iterations = int(Vectors_Objective[C].Number_Iterations + (Factor_Mutation * (Vectors_Objective[B].Number_Iterations - Vectors_Objective[A].Number_Iterations)))

        Vectors_Noise[i].Type_Evaluation = 2

        if Vectors_Noise[i].Alpha < Settings["Alpha"]["MIN"]:
            Vectors_Noise[i].Alpha = Settings["Alpha"]["MIN"]

        elif Vectors_Noise[i].Alpha > Settings["Alpha"]["MAX"]:
            Vectors_Noise[i].Alpha = Settings["Alpha"]["MAX"]

        if Vectors_Noise[i].Beta < Settings["Beta"]["MIN"]:
            Vectors_Noise[i].Beta = Settings["Beta"]["MIN"]
        
        elif Vectors_Noise[i].Beta > Settings["Beta"]["MAX"]:
            Vectors_Noise[i].Beta = Settings["Beta"]["MAX"]

        if Vectors_Noise[i].Gamma < Settings["Gamma"]["MIN"]:
            Vectors_Noise[i].Gamma = Settings["Gamma"]["MIN"]

        elif Vectors_Noise[i].Gamma > Settings["Gamma"]["MAX"]:
            Vectors_Noise[i].Gamma = Settings["Gamma"]["MAX"]

        if Vectors_Noise[i].Rho < Settings["Rho"]["MIN"]:
            Vectors_Noise[i].Rho = Settings["Rho"]["MIN"]
        
        elif Vectors_Noise[i].Rho > Settings["Rho"]["MAX"]:
            Vectors_Noise[i].Rho = Settings["Rho"]["MAX"]

        if Vectors_Noise[i].Number_Iterations < Settings["N_Iterations"]["MIN"]:
            Vectors_Noise[i].Number_Iterations = Settings["N_Iterations"]["MIN"]

        elif Vectors_Noise[i].Number_Iterations > Settings["N_Iterations"]["MAX"]:
            Vectors_Noise[i].Number_Iterations = Settings["N_Iterations"]["MAX"]

def Initialize_Test (Vectors_Objective, Vectors_Test, Vectors_Noise, Factor_Crosses):
    Number_Random = 0

    for i in range(len(Vectors_Test)):
        Number_Random = random.uniform(0, 1)

        if Number_Random <= Factor_Crosses:
            Vectors_Test[i].Alpha = Vectors_Noise[i].Alpha
        else:
            Vectors_Test[i].Alpha = Vectors_Objective[i].Alpha
        
        Number_Random = random.uniform(0, 1)

        if Number_Random <= Factor_Crosses:
            Vectors_Test[i].Beta = Vectors_Noise[i].Beta
        else:
            Vectors_Test[i].Beta = Vectors_Objective[i].Beta

        Number_Random = random.uniform(0, 1)

        if Number_Random <= Factor_Crosses:
            Vectors_Test[i].Gamma = Vectors_Noise[i].Gamma
        else:
            Vectors_Test[i].Gamma = Vectors_Objective[i].Gamma

        Number_Random = random.uniform(0.1, 0.9)

        if Number_Random <= Factor_Crosses:
            Vectors_Test[i].Rho = Vectors_Noise[i].Rho
        else:
            Vectors_Test[i].Rho = Vectors_Objective[i].Rho

        Number_Random = random.uniform(0, 1)

        if Number_Random <= Factor_Crosses:
            Vectors_Test[i].Number_Iterations = Vectors_Noise[i].Number_Iterations
        else:
            Vectors_Test[i].Number_Iterations = Vectors_Objective[i].Number_Iterations

        Vectors_Test[i].Type_Evaluation = 3

def Update_Objetive (Vectors_Objective, Vectors_Test):
    for i in range(len(Vectors_Objective)):
        if Vectors_Objective[i].FO > Vectors_Test[i].FO:
            Vectors_Objective[i].Alpha = Vectors_Test[i].Alpha
            Vectors_Objective[i].Beta = Vectors_Test[i].Beta
            Vectors_Objective[i].Gamma = Vectors_Test[i].Gamma
            Vectors_Objective[i].Rho = Vectors_Test[i].Rho
            Vectors_Objective[i].Number_Iterations = Vectors_Test[i].Number_Iterations
            Vectors_Objective[i].FO = Vectors_Test[i].FO
            Vectors_Objective[i].Type_Evaluation = Vectors_Test[i].Type_Evaluation

def Evaluate_FO (Vector_: Vector, Index):
    global Settings
    
    FO , Dict_Information = VRPTWACO(Vector_.Number_Iterations, Settings["N_Ants"],Vector_.Alpha, Vector_.Beta, Vector_.Gamma, Vector_.Rho, Vector_.Type_Evaluation, Index, Settings["Instance"])

    Dict_Information["Alpha"] = Vector_.Alpha
    Dict_Information["Beta"] = Vector_.Beta
    Dict_Information["Gamma"] = Vector_.Gamma
    Dict_Information["Rho"] = Vector_.Rho
    
    return FO , Dict_Information

    
def Load_Settings():

    json_file = open("Config/Settings.json", "r")
    
    Settings = json.load(json_file)
    json_file.close()

    return Settings

def Search_Best_Soluction (List_FO_Objetive, List_Information_Objetive, List_FO_Test, List_Information_Test):
    Best_FO = math.inf
    Best_Information = {}
    
    for i in range(len(List_FO_Objetive)):
        if List_FO_Objetive[i] < Best_FO:
            Best_FO = List_FO_Objetive[i]
            Best_Information = List_Information_Objetive[i]

    for i in range(len(List_FO_Test)):
        if List_FO_Test[i] < Best_FO:
            Best_FO = List_FO_Test[i]
            Best_Information = List_Information_Test[i]
    
    return Best_FO, Best_Information

def Search_Worse_Soluction (List_FO_Objetive, List_Information_Objetive, List_FO_Test, List_Information_Test):
    Worse_FO = -math.inf
    Worse_Information = {}
    
    for i in range(len(List_FO_Objetive)):
        if List_FO_Objetive[i] > Worse_FO:
            Worse_FO = List_FO_Objetive[i]
            Worse_Information = List_Information_Objetive[i]

    for i in range(len(List_FO_Test)):
        if List_FO_Test[i] > Worse_FO:
            Worse_FO = List_FO_Test[i]
            Worse_Information = List_Information_Test[i]
    
    return Worse_FO, Worse_Information

def Save_Execution (Time_Execution, Best_Information, Worse_Information):
    Dict_Execution = {
        "Time_Execution": Time_Execution,
        "Best_Execution": Best_Information,
        "Worse_Execution": Worse_Information
    }

    Name_File = "Results/Execution_" + str(datetime.datetime.now().strftime("%Y-%m-%d")) + ".json"
    json_file = open(Name_File, "x")
    json.dump(Dict_Execution, json_file, indent=4)
    json_file.close()

Start_Program = time.time()

Settings = Load_Settings()

print(Fore.GREEN + "📃 Algorithm Differential Evolution for VRPTW ACO 🐜")
#print(Fore.GREEN + "Settings Loaded")
#print(Settings)

Size_Poblation = 1
Factor_Mutation = 0.5
Factor_Crosses = 0.5
Number_Iterations_MAX = 5
Number_Current = 0

Vectors_Objective = []
Vectors_Noise = []
Vectors_Test = []

for i in range(Size_Poblation):
    Vectors_Objective.append(Vector())
    Vectors_Noise.append(Vector())
    Vectors_Test.append(Vector())

while Number_Current < Number_Iterations_MAX:
    print(Fore.GREEN + "Generation: ", Number_Current)

    total_steps = Size_Poblation * 3  # Tres bucles con tamaño de población

    progress_bar = tqdm(total=total_steps, desc="Processing", unit="step")

    for i in range(Size_Poblation):
        Vectors_Noise[i].Reset_Vector()
        Vectors_Test[i].Reset_Vector()

    if Number_Current == 0:
        for i in range(Size_Poblation):
            Vectors_Objective[i].Reset_Vector()
            Vectors_Objective[i].Initialize_Objetive()

    for i in range(Size_Poblation):
        Vectors_Objective[i].Update_Type_Evaluation(1)
    
    Initialize_Noise(Vectors_Objective, Vectors_Noise, Factor_Mutation)
    Initialize_Test(Vectors_Objective, Vectors_Test, Vectors_Noise, Factor_Crosses)

    List_FO_Objetive = []
    List_Information_Objetive = []

    for i in range(Size_Poblation):
        FO , Information_Evaluation = Evaluate_FO(Vectors_Objective[i], i)
        List_FO_Objetive.append(FO)
        List_Information_Objetive.append(Information_Evaluation)
        progress_bar.update(1)

    List_FO_Noise = []
    List_Information_Noise = []

    for i in range(Size_Poblation):
        FO , Information_Evaluation = Evaluate_FO(Vectors_Noise[i], i)
        List_FO_Noise.append(FO)
        List_Information_Noise.append(Information_Evaluation)
        progress_bar.update(1)

    List_FO_Test = []
    List_Information_Test = []

    for i in range(Size_Poblation):
        FO , Information_Evaluation = Evaluate_FO(Vectors_Test[i], i)
        List_FO_Test.append(FO)
        List_Information_Test.append(Information_Evaluation)
        progress_bar.update(1)

    Update_Objetive(Vectors_Objective, Vectors_Test)

    # Termina la barra de progreso
    progress_bar.close()

    Number_Current += 1



print(Fore.GREEN + "Finish")
print(List_FO_Objetive)
print(List_Information_Objetive)

print(List_FO_Test)
print(List_Information_Test)

FO_Best , Information_Best = Search_Best_Soluction(List_FO_Objetive, List_Information_Objetive, List_FO_Test, List_Information_Test)

print(Fore.GREEN + "Best FO: ", FO_Best)
print(Information_Best)

FO_Worse , Information_Worse = Search_Worse_Soluction(List_FO_Objetive, List_Information_Objetive, List_FO_Test, List_Information_Test)

print(Fore.GREEN + "Worse FO: ", FO_Worse)
print(Information_Worse)


End_Program = time.time()
print(Fore.GREEN + "Time Execution: ", End_Program - Start_Program)

Save_Execution(End_Program - Start_Program, Information_Best, Information_Worse)