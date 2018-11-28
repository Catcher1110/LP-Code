# -*- coding: utf-8 -*-
import pyomo.environ as pe
import numpy as np

'''setA= np.array([[0, 860, 599, 574, 269, 349,  87, 100, 353, 1300],
		        [860, 0  , 268, 347, 596, 541, 779, 961, 925, 859],
	    	    [599, 268, 0  ,  85, 334, 279, 516, 698, 663, 901],
	    	    [574, 347,  85,   0, 309, 254, 492, 674, 595, 981],
	    	    [269, 596, 334, 309,   0,  85, 187, 369, 342, 1138],
	    	    [349, 541, 279, 254,  85,   0, 266, 448, 413, 1083],
        		[87 , 779, 516, 492, 187, 266,   0, 186, 314, 1240],
	          	[100, 961, 698, 674, 369, 448, 186,   0, 373, 1404],
	    	    [353, 925, 663, 595, 342, 413, 314, 373,  0,  1467],
		        [1300, 859, 901, 981, 1138, 1083, 1240, 1404, 1467, 0]])'''

setA= np.array([	[0,860,599,100,353,269,349,87,1300,574],
					[860,0,268,961,925,596,541,779,859,347],
					[599,268,0,698,663,334,279,516,901,85],
					[100,961,698,0,373,369,448,186,1404,674],
					[353,925,663,373,0,342,413,314,1467,595],
					[269,596,334,369,342,0,85,187,1138,309],
					[349,541,279,448,413,85,0,266,1083,254],
					[87,779,516,186,314,187,266,0,1240,492],
					[1300,859,901,1404,1467,1138,1083,1240,0,981],
					[574,347,85,674,595,309,254,492,981,0]  ])

setB=np.array([[setA[0,5],setA[1,5],setA[2,5],setA[3,5],setA[4,5]],
		    [setA[0,6],setA[1,6],setA[2,6],setA[3,6],setA[4,6]],
		    [setA[0,7],setA[1,7],setA[2,7],setA[3,7],setA[4,7]],
		    [setA[0,3],setA[1,3],setA[2,3],100000,setA[4,3]],
		    [setA[0,8],setA[1,8],setA[2,8],setA[3,8],setA[4,8]]])

setC=np.array([[setA[5,0],setA[6,0],setA[7,0],setA[3,0],setA[8,0]],
		    [setA[5,1],setA[6,1],setA[7,1],setA[3,1],setA[8,1]],
		    [setA[5,9],setA[6,9],setA[7,9],setA[3,9],setA[8,9]],
		    [setA[5,4],setA[6,4],setA[7,4],setA[3,4],setA[8,4]],
		    [setA[5,8],setA[6,8],setA[7,8],setA[3,8],100000]])

setD=np.array([[setA[0,5],setA[1,5],setA[9,5],setA[4,5],setA[8,5]],
		    [setA[0,6],setA[1,6],setA[9,6],setA[4,6],setA[8,6]],
		    [setA[0,7],setA[1,7],setA[9,7],setA[4,7],setA[8,7]],
		    [setA[0,3],setA[1,3],setA[9,3],setA[4,3],setA[8,3]],
		    [setA[0,4],setA[1,4],setA[9,4],100000,setA[8,4]]])

setE=np.array([[setA[5,0],setA[6,0],setA[7,0],setA[3,0],setA[4,0]],
    		[setA[5,1],setA[6,1],setA[7,1],setA[3,1],setA[4,1]],
	    	[setA[5,9],setA[6,9],setA[7,9],setA[3,9],setA[4,9]],
		    [setA[5,7],setA[6,7],100000,setA[3,7],setA[4,7]],
		    [setA[5,8],setA[6,8],setA[7,8],setA[3,8],setA[4,8]]])
		
setF=np.array([[setA[0,2],setA[1,2],setA[9,2],setA[7,2],setA[8,2]],
    		[setA[0,9],setA[1,9],100000,setA[7,9],setA[8,9]],
	    	[setA[0,5],setA[1,5],setA[9,5],setA[7,5],setA[8,5]],
		    [setA[0,6],setA[1,6],setA[9,6],setA[7,6],setA[8,6]],
		    [setA[0,8],setA[1,8],setA[9,8],setA[7,8],100000]])


# Create the model= pe.ConcreteModel()
model = pe.ConcreteModel()
model.dual = pe.Suffix(direction = pe.Suffix.IMPORT)

# ------ SETS ---------
model.crew  = pe.Set(initialize = range(5))
model.week  = pe.Set(initialize = range(5))
model.set = pe.Set(initialize = range(5))

# -------------VARIABLES------------
model.x = pe.Var(model.crew,model.crew,model.week,domain = pe.Binary)

# ------PARAMETERS--------
model.setB = pe.Param(model.set, model.set, initialize = lambda model, i,j: setB[i][j])
model.setC = pe.Param(model.set, model.set, initialize = lambda model, i,j: setC[i][j])
model.setD = pe.Param(model.set, model.set, initialize = lambda model, i,j: setD[i][j])
model.setE = pe.Param(model.set, model.set, initialize = lambda model, i,j: setE[i][j])
model.setF = pe.Param(model.set, model.set, initialize = lambda model, i,j: setF[i][j])

# ------CONSTRAINTS-----------
def uniqrow_cons(model,j,k):
	return sum(model.x[i,j,k] for i in range(5)) == 1
	
model.uniqrowCons = pe.Constraint(model.crew,model.week,rule = uniqrow_cons)

def uniqcol_cons(model,i,k):
	return sum(model.x[i,j,k] for j in range(5)) == 1

model.uniqcolCons = pe.Constraint(model.crew,model.week,rule = uniqcol_cons)

# ------OBJECTIVE-----------
def obj_rule(model):
	w = 0
	for j in range(5):
		for i in range(5):
				w = w + model.setB[i,j] * model.x[i,j,0] + model.setC[i,j] * model.x[i,j,1]\
				+ model.setD[i,j] * model.x[i,j,2] + model.setE[i,j] * model.x[i,j,3]\
				+ model.setF[i,j] * model.x[i,j,4]

	return (0.5*7*w)
    
model.OBJ = pe.Objective(rule = obj_rule, sense = pe.minimize)

model.OBJ.pprint()

#----------SOLVING----------
solver = pe.SolverFactory('gurobi') # Specify Solver

results = solver.solve(model, tee=False, keepfiles=False)

print()
print("Status:", results.solver.status)
print("Termination Condition:", results.solver.termination_condition)


# ---------POST-PROCESSING-------------------
print()
for k in model.crew:
    print('The %d th week to %d th week schedule:'%(k+1, k+2))
    for i in model.crew:
        print(model.x[i,0,k].value,model.x[i,1,k].value,\
        model.x[i,2,k].value,model.x[i,3,k].value,model.x[i,4,k].value)

temp1 = 0    
for i in range(5):
    for j in range(5):
        temp1 = temp1 + model.x[i,j,0].value * setB[i,j]
print('Temp1: ',temp1)

temp2 = 0    
for i in range(5):
    for j in range(5):
        temp2 = temp2 + model.x[i,j,1].value * setC[i,j]
print('Temp2: ',temp2)

temp3 = 0    
for i in range(5):
    for j in range(5):
        temp3 = temp3 + model.x[i,j,2].value * setD[i,j]
print('Temp3: ',temp3)

temp4 = 0    
for i in range(5):
    for j in range(5):
        temp4 = temp4 + model.x[i,j,3].value * setE[i,j]
print('Temp4: ',temp4)

temp5 = 0    
for i in range(5):
    for j in range(5):
        temp5 = temp5 + model.x[i,j,4].value * setF[i,j]
print('Temp5: ',temp5)

print()		
print("\nObjective function value: ", model.OBJ())