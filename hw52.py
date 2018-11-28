import pyomo.environ as pe
import numpy as np
import matplotlib.pyplot as plt

# data points: first column is sepal length, second column is petal length
y = np.array([[1.3510,    3.1812],
    [1.2415,    0.8904],
    [1.1544,    1.4273],
    [1.4413,    2.1784],
    [1.8031,    2.5864],
    [1.1481,    2.8003],
    [0.4906,    2.8759],
    [1.7572,    2.1668],
    [0.0346,    0.7299],
    [3.1752,    4.0292],
    [1.7248,    7.6037],
    [3.7813,    8.7737],
    [0.1349,    5.9489],
    [1.5826,    8.4022],
    [0.6323,    6.7075],
    [3.2708,    7.0660],
    [2.4513,    6.6778],
    [2.7884,    7.9287],
    [1.5092,    8.7972],
    [2.5907,    6.3642],
    [7.6033,    1.4648],
    [6.8449,    2.6121],
    [5.9557,    1.6544],
    [5.8286,    1.3144],
    [7.9262,    0.5183],
    [6.4419,    1.9715],
    [5.5237,    2.2589],
    [4.9813,    2.1997],
    [7.4259,    0.7300],
    [6.5148,    2.5943]])

# labels on the data points: 1 is indicates that the flower belongs to the first species, -1 indicates that the flower belongs to the second species
z = np.array([1, 1, 1,	1,	1,	1,	1,	1,	1,	1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1])

lamb = 0.01
# Create the model
model = pe.ConcreteModel()
model.dual = pe.Suffix(direction = pe.Suffix.IMPORT)
# ------ SETS ---------
model.dd = pe.Set(initialize = range(2))
model.ddd = pe.Set(initialize = range(3))
model.le = pe.Set(initialize = range(30))
# ------PARAMETERS--------
model.Y = pe.Param(model.le, model.dd, initialize = lambda model, i, j: y[i][j])
model.Z = pe.Param(model.le, initialize = lambda model, i: z[i])
# -------------VARIABLES------------
model.w = pe.Var(model.ddd, domain = pe.Reals)
model.z = pe.Var(model.dd, domain = pe.NonNegativeReals)
model.p = pe.Var(model.le, domain = pe.NonNegativeReals)
# ------CONSTRAINTS-----------
def precedence_rule(model, i):
    return model.p[i] >= 1 - model.Z[i]*(model.w[0] * model.Y[i,0] + model.w[1] * model.Y[i, 1] - model.w[2])
model.precedenceCons = pe.Constraint(model.le, rule = precedence_rule)
def nonnegetive_rule(model, i):
    return model.p[i] >= 0
model.nonnegetiveCons = pe.Constraint(model.le, rule = nonnegetive_rule)
def resource_rule(model, i):
    return model.z[i] >= model.w[i]
model.resourceCons = pe.Constraint(model.dd, rule = resource_rule)
def resource2_rule(model, i):
    return model.z[i] >= -model.w[i]
model.resourceCons = pe.Constraint(model.dd, rule = resource2_rule)
# ------OBJECTIVE-----------
def obj_rule(model):
    temp = sum(model.p[i] for i in model.p)
    return temp + lamb * (model.z[0] + model.z[1])
model.OBJ = pe.Objective(rule = obj_rule, sense = pe.minimize)
model.OBJ.pprint()
#----------SOLVING----------
solver = pe.SolverFactory('gurobi') # Specify Solver
results = solver.solve(model, tee = False, keepfiles = False)
print()
print("Status:", results.solver.status)
print("Termination Condition:",\
             results.solver.termination_condition)
# ---------POST-PROCESSING-------------------
print()
for c in model.w:
    print('w %d is %.3f'%(c+1, model.w[c].value))
for c in model.z:
    print('z %d is %.3f'%(c+1, model.z[c].value))
for c in model.p:
    print('p %d is %.3f'%(c+1, model.p[c].value))

plt.scatter(y[1:10,0],y[1:10,1])
plt.scatter(y[11:30,0],y[11:30,1])
lineX = np.arange(-1, 9, 0.1)
lineY = (model.w[2].value - lineX * model.w[0].value) / model.w[1].value
plt.plot(lineX, lineY)
plt.show()

print('sum p = %.2f'%(sum(model.p[i].value for i in model.p)))

print("\nObjective function value: ", model.OBJ())