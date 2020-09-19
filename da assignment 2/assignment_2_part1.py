import pandas as pd
from ortools.linear_solver import pywraplp


#A. Load the input data from the file “Assignment_DA_2_a_data.xlsx” [1 point].
# Note that not all fields are filled, for example Supplier C does not stock Material A.
# Make sure to use the data from the file in your code, please do not hardcode any
# values that can be read from the file.
 
data = pd.read_excel("Assignment_DA_2_a_data.xlsx", sheet_name = None, index_col = 0)
supplier_stock = data["Supplier stock"]
material_costs = data["Raw material costs"]
material_shipping = data["Raw material shipping"]
product_requirements = data["Product requirements"]
production_capacity = data["Production capacity"]
production_cost = data["Production cost"]
customer_demand = data["Customer demand"]
shipping_cost = data["Shipping costs"]
 


suppliers = set(supplier_stock.index.values)
print(suppliers)
raw_materials = set(supplier_stock.columns.values)
print(raw_materials)
factories = set(material_shipping.columns.values)
print(factories)
products = set(product_requirements.index.values)
print(products)
customers = set(customer_demand.columns.values)
print(customers)


# B. Identify and create the decision variables for the orders from the suppliers [1 point],
# for the production volume [1 point], and for the delivery to the customers [1 point]
# using the OR Tools wrapper of the GLOP_LINEAR_PROGRAMMING solver.

solver = pywraplp.Solver('LPWrapper', 
                             pywraplp.Solver.GLOP_LINEAR_PROGRAMMING) 

## orders from suppliers
print("Creating Decision Variables...")
orders_to_suppliers = {}
for supplier in suppliers:
    for material in raw_materials:
        if pd.notna(supplier_stock[material][supplier]):
            for factory in factories:
                orders_to_suppliers[(supplier,material,factory)] = solver.NumVar(0,
                                    solver.infinity(), supplier+"_"+material+"_"+factory)
#
## production volume
manufacture_volume = {}
for factory in factories:
    for product in products:
        manufacture_volume[(factory,product)] = solver.NumVar(0,solver.infinity(),
                                                           factory+"_"+product )
 
#        
# # delivery to customers
customer_shipping = {}

for customer in customers:
    for factory in factories:
        for product in products:
            if pd.notna(production_capacity[factory][product]):
                customer_shipping[(factory,product,customer)] = solver.NumVar(0,
                                    solver.infinity(),factory+"_"+product+"_"+customer )

print("Decision Variables Created!")


print(pd.isna(customer_demand['Customer A']['Product B'] ))
print(pd.notna(supplier_stock['Material B']['Supplier D']))

#C. Define and implement the constraints that ensure factories produce more than 
#they ship to the customers [2 points].


                            ##### Yet to Implement #######

# D. Define and implement the constraints that ensure that customer demand is met [2 points].

for product in products:
    for customer in customers:
        if not pd.isna(customer_demand[customer][product]):
            c = solver.Constraint(customer_demand[customer][product], solver.infinity())
            for factory in factories:
                if pd.notna(production_capacity[factory][product]):
                    c.SetCoefficient(customer_shipping[(factory, product, customer)], 1)



#E.Define and implement the constraints that ensure that suppliers have all 
#ordered items in stock [2 points].


for supplier in suppliers:
    for material in raw_materials:
        if pd.notna(supplier_stock[material][supplier]):
            c = solver.Constraint(supplier_stock[material][supplier], solver.infinity())
            for factory in factories:
                c.SetCoefficient(orders_to_suppliers[(supplier,material,factory)], 1)


                
#'''
# F. Define and implement the constraints that ensure that factories order 
#enough material to be able to manufacture all items [2 points].
#'''

#for factory in factories: 
#    for material in raw_materials: 
#        c = solver.Constraint(0, solver.infinity())
#        for supplier in suppliers:
#            if pd.isna(supplier_stock[material][supplier]):
#                c.SetCoefficient(manufacture_volume[(factory,product)], 0)
#            else:
#                c.SetCoefficient(orders_to_suppliers[(supplier, material, factory)], 1)
#            for product in products:
#                c.SetCoefficient(manufacture_volume[(factory, product)], - product_requirements[material][product])








#'''
#Define and implement the constraints that ensure that the manufacturing 
#capacities are not exceeded [2 points].
#'''
#
for product in products: 
    for factory in factories: 
        if pd.notna(production_capacity[factory][product]):
            c = solver.Constraint(0, production_capacity[factory][product])
            c.SetCoefficient(manufacture_volume[(factory,product)], 1)

#
#
#'''
# H. Define and implement the objective function. Make sure to consider the supplier 
#bills comprising shipping and material costs [2 points], the production cost of
#each factory [2 points], and the cost of delivery to each customer [2 points].
#'''
#
        
print("Constraints Created!!!" )

print("Creating Objective Function...")
cost = solver.Objective()

# shipping cost to customer + Product Manufacturing_cost

for customer in customers:
    for product in products:
        for factory in factories:
            if pd.notna(production_capacity[factory][product]):
                # shipping cost to the customer 
                cost.SetCoefficient(customer_shipping[(factory, product, customer)],
                                    float(shipping_cost[customer][factory]))
                #Production cost of each factory
                cost.SetCoefficient(manufacture_volume[(factory, product)], 
                                                       float(production_cost[factory][product]))



# Raw Material Cost + Raw Material Shipping cost to Factory
for supplier in suppliers: 
    for materials in raw_materials: 
        if pd.notna(supplier_stock[material][supplier]):
            for factory in factories: 
                cost.SetCoefficient(orders_to_suppliers[(supplier, material, factory)], 
                                                        float(material_costs[material][supplier]) +
                                                        float(material_shipping[factory][supplier]))    
            
print("Objective Function Created!!!")           

#I. Solve the linear program and determine the optimal overall cost [1 point].


cost.SetMinimization()
status = solver.Solve()
if status == solver.OPTIMAL:
    print("Optimal Solution Found")
    print("The optimal overall cost is ", solver.Objective().Value())


#J. Determine for each factory how much material has to be ordered from 
#each individual supplier [1 point].
    print("****************************************")                 
    for factory in factories:
        print("\n",factory)
        for supplier in suppliers: 
            print("From ", supplier)
            for material in raw_materials: 
                if pd.notna(supplier_stock[material][supplier]):
                    print("\t", material, "---> ", orders_to_suppliers[(supplier, material, factory)].solution_value() )

                
#            
#            
#            
#K. Determine for each factory what the supplier bill comprising material 
#cost and delivery will be for each supplier [1 point].
#
    print("****************************************")                 
    for factory in factories:
        print("\n",factory)
        for supplier in suppliers: 
            supplier_bill = 0
            raw_material_cost = 0
            mat_shipping_cost = 0
            for material in raw_materials: 
                if pd.notna(supplier_stock[material][supplier]):
                    raw_material_cost += orders_to_suppliers[(supplier, material, factory)].solution_value() * int(material_costs[material][supplier])
                    mat_shipping_cost += orders_to_suppliers[(supplier, material, factory)].solution_value() * int(material_shipping[factory][supplier])
            supplier_bill = raw_material_cost + mat_shipping_cost
            
            print(supplier," bill is: ", supplier_bill)
#   
#            
# L. Determine for each factory how many units of each product are being manufactured
#[1 point]. Also determine the total manufacturing cost for each individual factory [1 point].
    print("****************************************")                 
    for factory in factories:
        print("\nFor ",factory)
        manufacturing_cost = 0
        for product in products:
            if pd.notna(production_capacity[factory][product]):
                
                manufacturing_cost += manufacture_volume[(factory, product)].solution_value() * production_cost[factory][product]
                print(product," manufactured : ", manufacture_volume[(factory, product)].solution_value())
        print(" Total Production cost is ", str(manufacturing_cost))
        
#
#     M. Determine for each customer how many units of each product are being shipped
#     from each factory [1 point]. Also determine the total shipping cost per customer [1
#     point]
    print("****************************************") 
    for customer in customers: 
        print("\n",customer)
        s_cost = 0
        for product in products: 
            if pd.notna(customer_demand[customer][product]):
                print(" ",product)
                for factory in factories: 
                    if pd.notna(production_capacity[factory][product]):
                        print("\t",factory,": ", 
                              customer_shipping[(factory, product, customer)].solution_value())
                        s_cost += customer_shipping[(factory, product, customer)].solution_value() * shipping_cost[customer][factory]
        print("\n Total Shipping Cost: ", s_cost )
                        
                        
                    
                    
                

#    
#N. Determine for each customer the fraction of each material each factory has to order
#for manufacturing products delivered to that particular customer [1 point]. Based on
#this calculate the overall unit cost of each product per customer including the raw
#materials used for the manufacturing of the customer’s specific product, the cost of
#manufacturing for the specific customer and all relevant shipping costs [2 points].
#
    print("****************************************") 
    for customer in customers:
        print("\n", customer)
        for product in products:
            print(product)
            for material in raw_materials:
                print("\t",material)
                no_of_units = 0
                for factory in factories:
                    if pd.notna(production_capacity[factory][product]) and pd.notna(product_requirements[material][product]):
                        no_of_units = customer_shipping[(factory, product, customer)].solution_value() * product_requirements[material][product]
                        print("\t\t", factory, "--->", no_of_units)
    

else: 
    print("No Optimal solution found")