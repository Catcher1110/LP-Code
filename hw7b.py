from PIL import Image
import pyomo.environ as pe
import scipy

im = Image.open('tower.png').convert('L') #convert to grayscale

h = im.height
w = im.width

print('height is: %d \n'%(h)) # height is 120 pixels
print('width is: %d \n'%(w)) # width is 177 pixels

#grayscale values; list of size h*w , where each values is integer in range [0,255]
intensity = list(im.getdata()) # it follows by rows, (i,j) means intensity[120*(i-1) + j - 1]

print(len(intensity)) # the list has the length of 21240 (120 * w)

# YOUR CODE GOES HERE
pathfile = open('pathfile.txt','a')

# Calculate the existed edges
sourcenode = w * (1-1) + (50 - 1)
targetnode = 1000000
Startnode = list([sourcenode])
Edges = list()

for t in range(2, 122):
    tempEdges = list()
    if t != 121:
        for i in Startnode:
            icol = (i + 1)%w
            if icol != 1 and icol != w:
                tempEdges.append([i, w * (t-1) + (icol - 2)])
                tempEdges.append([i, w * (t-1) + (icol - 1)])
                tempEdges.append([i, w * (t-1) + (icol)])
            elif icol == 1:
                tempEdges.append([i, w * (t-1) + (icol - 1)])
                tempEdges.append([i, w * (t-1) + (icol)])
            elif icol == w:
                tempEdges.append([i, w * (t-1) + (icol - 2)])
                tempEdges.append([i, w * (t-1) + (icol - 1)])
            
        Startnode = list()
        for j in tempEdges:
            Startnode.append(j[1])
        Startnode = list(set(Startnode))
        Startnode.sort()

    elif t == 121:
        for i in Startnode:
            tempEdges.append([i, targetnode])
    Edges = Edges + tempEdges

print('The number of edges is %d'%(len(Edges)))

# Calculate the cost for each edge
CostEdges = []
for edge in Edges:
    if edge[1] != targetnode:
        CostEdges.append(abs(intensity[edge[0]] - intensity[edge[1]]))
    else:
        CostEdges.append(0)
print('The number of costs is %d'%(len(CostEdges)))
# print(CostEdges)

Nodes = [i for k in Edges for i in k]
Nodes = list(set(Nodes))
Nodes.sort() # Nodes represent the node can arrive

print('There are %d node can arrive.'%(len(Nodes)))

# Create the model
model = pe.ConcreteModel()

model.dual = pe.Suffix(direction = pe.Suffix.IMPORT)

# ------ SETS ---------
model.nodes = pe.Set(initialize = range(len(Nodes)))
model.edges = pe.Set(initialize = range(len(Edges)))
model.lenintensity = pe.Set(initialize = range(len(intensity)))
model.h = pe.Set(initialize = range(h))
model.w = pe.Set(initialize = range(w))

# ------PARAMETERS--------
model.intensity = pe.Param(model.lenintensity, initialize = lambda model, t: intensity[t])

# -------------VARIABLES------------
model.y = pe.Var(model.nodes, domain = pe.Reals)

# ------CONSTRAINTS-----------
def dual_rule(model, edgeid):
    temp_edge = Edges[edgeid]
    return (model.y[Nodes.index(temp_edge[1])] - model.y[Nodes.index(temp_edge[0])] <= CostEdges[edgeid])

model.callsCons = pe.Constraint(model.edges, rule = dual_rule)

# ------OBJECTIVE-----------
def obj_rule(model):
    return model.y[len(Nodes)-1] - model.y[0]
    
model.OBJ = pe.Objective(rule = obj_rule, sense = pe.maximize)

model.OBJ.pprint()

#----------SOLVING----------
solver = pe.SolverFactory('gurobi') # Specify Solver

results = solver.solve(model, tee = False, keepfiles = False)

print()
print("Status:", results.solver.status)
print("Termination Condition:", results.solver.termination_condition)

# ---------POST-PROCESSING-------------------
print("\nObjective function value: ", model.OBJ())