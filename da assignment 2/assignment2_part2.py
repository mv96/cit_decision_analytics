


from ortools.linear_solver import pywraplp
import pandas as pd

# A. Load the input data from the file “Assignment_DA_2_b_data.xlsx” [1 point]. 
#Make sure to use the data from the file in your code, please do not hardcode any
# values that can be read from the file.

flight_sched = pd.read_excel('Assignment_DA_2_b_data.xlsx', 'Flight schedule', index_col=0)
taxi_distances = pd.read_excel('Assignment_DA_2_b_data.xlsx', 'Taxi distances', index_col=0)
term_capacity = pd.read_excel('Assignment_DA_2_b_data.xlsx', 'Terminal capacity', index_col=0)

flights = flight_sched.index.to_list()
runways = taxi_distances.index.to_list()
terminals = taxi_distances.columns.to_list()
times = set()
for flight in flights:
    times.add(flight_sched['Arrival'][flight])
    times.add(flight_sched['Departure'][flight])


# B.  Identify and create the decision variables for the arrival runway allocation [1 point],
# for the departure runway allocation [1 point], and for the terminal allocation [1 point] 
#using the OR Tools wrapper of the CBC_MIXED_INTEGER_PROGRAMMING solver.
#                                     &
# C. Define and create auxiliary variables for the taxi movements between runways
# and terminals for each flight [1 point].

solver = pywraplp.Solver('MIP', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
arr_allocation = {}
dep_allocation = {}
arr_taxi_movement = {}
dep_taxi_movement = {}
for flight in flights:
    for runway in runways:
        arr_allocation[(flight, runway)] = solver.IntVar(0, 1, "Arrival"+flight+"_"+runway)
    for runway in runways:
        dep_allocation[(flight, runway)] = solver.IntVar(0, 1,  "Departure"+flight+"_"+runway)
    # Creation of Auxilary Variables
    for runway in runways: 
        for terminal in terminals:
            arr_taxi_movement[(flight,runway,terminal)] = solver.BoolVar("a"+flight+"_"+runway+"_"+terminal)
            dep_taxi_movement[(flight,runway,terminal)] = solver.BoolVar("d"+flight+"_"+runway+"_"+terminal)
     

# Terminal allocation 
allocation_of_terminal = {}
for terminal in terminals:
    for flight in flights:
        allocation_of_terminal[(terminal, flight)] = solver.BoolVar(terminal+"_"+flight)

# D. Define and implement the constraints that ensure that every flight has exactly two taxi movements


for flight in flights:
    c1 = solver.Constraint(1,1)
    c2 = solver.Constraint(1,1)
    for runway in runways:
        for terminal in terminals:
            c1.SetCoefficient(arr_taxi_movement[(flight,runway,terminal)], 1)
            c2.SetCoefficient(dep_taxi_movement[(flight,runway,terminal)], 1)
# E. Define and implement the constraints that ensure that the taxi movements 
# of a flight are to and from the allocated terminal

for flight in flights:
    for terminal in terminals:
        c1 = solver.Constraint(0,0)
        c2 = solver.Constraint(0,0)
        c1.SetCoefficient(allocation_of_terminal[(terminal, flight)] , -1)
        c2.SetCoefficient(allocation_of_terminal[(terminal, flight)] , 1)
        for runway in runways:
            c1.SetCoefficient(arr_taxi_movement[(flight, runway, terminal)], 1)
            c2.SetCoefficient(dep_taxi_movement[(flight, runway, terminal)], -1)

# F. Define and implement the constraints that ensure that the taxi movements 
#    of a flight include the allocated arrival and departure runways

for flight in flights:
    for runway in runways:
        c1 = solver.Constraint(0,0)
        c2 = solver.Constraint(0,0)
        c1.SetCoefficient(arr_allocation[(flight, runway)], -1)
        c2.SetCoefficient(dep_allocation[(flight, runway)], -1)
        for terminal in terminals:
            c1.SetCoefficient(arr_taxi_movement[(flight,runway,terminal)], 1)
            c2.SetCoefficient(dep_taxi_movement[(flight,runway,terminal)],1)


            



# G. Define and implement the constraints that ensure that each flight has 
#    exactly one allocated arrival runway [1 point] and exactly one allocated departure runway [1 point].
for flight in flights:           
    c = solver.Constraint(1,1)
    d = solver.Constraint(1,1)
    for runway in runways:
        c.SetCoefficient(arr_allocation[(flight,runway)] , 1)
        d.SetCoefficient(dep_allocation[(flight,runway)] , 1)



#H.. Define and implement the constraints the ensure that each flight is allocated 
#    to exactly one terminal [1 point].
for flight in flights:
    c = solver.Constraint(1,1)
    for terminal in terminals:
        c.SetCoefficient(allocation_of_terminal[(terminal, flight)] , 1)           
            
            
            
# I. Define and implement the constraints that ensure that no runway is used by
#    more than one flight during each timeslot
            
            


# J. Define and implement the constraints that ensure that the terminal capacities
#    are not exceeded [1 point].
            
for terminal in terminals:
    for time in times:
        c = solver.Constraint(0, int(term_capacity.loc[terminal]['Gates']))
        for flight in flights:
            if flight_sched.loc[flight]['Departure'] > time and flight_sched.loc[flight]['Arrival'] <= time:
                c.SetCoefficient(allocation_of_terminal[(terminal, flight)] , 1)
            else:
                c.SetCoefficient(allocation_of_terminal[(terminal, flight)] , 0)

# K. Define and implement the objective function [1 point]. Solve the linear 
#    program and determine the optimal total taxi distances for all flights [1 point].

total_taxi_distance = solver.Objective()
for flight in flights:
    for runway in runways:
        for terminal in terminals:
            total_taxi_distance.SetCoefficient( arr_taxi_movement[(flight,runway,terminal)]  , int(taxi_distances.loc[runway][terminal]))
            total_taxi_distance.SetCoefficient( dep_taxi_movement[(flight,runway,terminal)]  , int(taxi_distances.loc[runway][terminal]))

total_taxi_distance.SetMinimization()
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print("The optimal taxi distance is: ", solver.Objective().Value())

# L. Determine the arrival runway allocation [1 point], the departure runway 
#.   allocation [1 point], and the terminal allocation [1 point] for each flight. 
#.   Also determine the taxi distance for each flight [1 point].

    print("Terminal Allocation")
    for flight in flights:
        print(flight)
        for terminal in terminals:
            if allocation_of_terminal[(terminal, flight)].solution_value() == 1:
                print("\t",terminal)
    
        
        
    for flight in flights:
        temp_distance = 0
        print(flight)
        for runway in runways: 
            for terminal in terminals:
                if arr_taxi_movement[(flight,runway,terminal)].solution_value() == 1:
                    print("\t",runway,"--->", terminal)
                    temp_distance += taxi_distances.loc[runway][terminal]
                if dep_taxi_movement[(flight,runway,terminal)].solution_value() == 1:
                    print("\t",terminal, "--->", runway)
                    temp_distance += taxi_distances.loc[runway][terminal]
        print("Taxi Distance for the flight is: ", temp_distance)
        print("Allocation of Runways")
    for flight in flights:
        print(flight)
        for runway in runways:
            if arr_allocation[(flight, runway)].solution_value() == 1 :
                print("\tArrival runway:", runway)
            if dep_allocation[(flight, runway)].solution_value() == 1 :
                print("\tDeparture runway:", runway)
    
            
            
    

