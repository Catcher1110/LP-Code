from PIL import Image
import pyomo.environ as pe
import scipy

im = Image.open('cell.png').convert('L') #convert to grayscale

h = im.height
w = im.width

print('height is: %d \n'%(h)) # height is 127 pixels
print('width is: %d \n'%(w)) # width is 100 pixels

#grayscale values; list of size h*w , where each values is integer in range [0,255]
intensity = list(im.getdata()) # it follows by rows, (i,j) means intensity[100*(i-1) + j - 1]

print(len(intensity)) # the list has the length of 21240 (120 * w)

sigma = 100 # The tuning parameter

# Calculate the existed edges
sourcenode = -1
targetnode = 1000000
Edges = list()

# row_cal = 0
for i in range(len(intensity)):
    # Edges contained Source and Target node
    Edges.append([sourcenode, i])

for j in range(len(intensity)):
    Edges.append([j, targetnode])

for t in range(len(intensity)):
    row_t = int(t/w) + 1
    col_t = (t + 1) % w
    # Four corners in the image
    if t == 0:
        Edges.append([t, t+1])
        Edges.append([t, t+w])
    elif t == w-1:
        Edges.append([t, t-1])
        Edges.append([t, t+w])
    elif t == (h-1)*w:
        Edges.append([t, t+1])
        Edges.append([t, t-w])
    elif t == h*w-1:
        Edges.append([t, t-1])
        Edges.append([t, t-w])
    # Four edges in the image
    elif row_t == 1:
        Edges.append([t, t-1])
        Edges.append([t, t+1])
        Edges.append([t, t+w])
    elif row_t == h:
        Edges.append([t, t-1])
        Edges.append([t, t+1])
        Edges.append([t, t-w])
    elif col_t == 1:
        Edges.append([t, t+1])
        Edges.append([t, t-w])
        Edges.append([t, t+w])
    elif col_t == 0:
        Edges.append([t, t-1])
        Edges.append([t, t-w])
        Edges.append([t, t+w])
    # Nodes in the middle
    else:
        Edges.append([t, t-1])
        Edges.append([t, t+1])
        Edges.append([t, t-w])
        Edges.append([t, t+w])
# print('Row_cal = %d'%(row_cal))
print('The number of edges is %d'%(len(Edges)))

def cal_cost_edge(edge):
    if edge[0] == sourcenode:
        return scipy.exp(-scipy.square(121 - intensity[edge[1]])/sigma)
    elif edge[1] == targetnode:
        return scipy.exp(-scipy.square(33 - intensity[edge[0]])/sigma)
    else:
        # print(edge[1])
        return scipy.exp(-scipy.square(intensity[edge[0]] - intensity[edge[1]])/sigma)

# Calculate the cost for each edge
CostEdges = []
for edge in Edges:
    CostEdges.append(cal_cost_edge(edge))
print('The number of costs is %d'%(len(CostEdges)))
# print(CostEdges)

# Calculate the node can be arrived
Nodes = [i for k in Edges for i in k]
Nodes = list(set(Nodes))
Nodes.sort()
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
model.x = pe.Var(model.edges, domain = pe.NonNegativeReals)
model.y = pe.Var(model.nodes, domain = pe.NonNegativeReals)

# ------CONSTRAINTS-----------
def rule_1(model, edgeid): # d_uv - d_u + d_v >= 0
    y_1 = Edges[edgeid][0] + 1
    if Edges[edgeid][1] == targetnode:
        y_2 = len(Nodes) - 1
    else:
        y_2 = Edges[edgeid][1] + 1
    return model.x[edgeid] - model.y[y_1] + model.y[y_2] >= 0
model.ruleCons1 = pe.Constraint(model.edges, rule = rule_1)

def rule_2(model, nodeid): #d_v + d_sv >= 1
    return model.y[nodeid+1] + model.x[nodeid]>= 1
model.ruleCons2 = pe.Constraint(model.lenintensity, rule = rule_2)

def rule_3(model, nodeid): #-d_u + d_ut >= 0
    return -model.y[nodeid+1] + model.x[nodeid + h*w]>= 0
model.ruleCons3 = pe.Constraint(model.lenintensity, rule = rule_3)

# ------OBJECTIVE-----------

def obj_rule(model):
    return sum(CostEdges[i] * model.x[i] for i in model.edges)
    
model.OBJ = pe.Objective(rule = obj_rule, sense = pe.minimize)

# model.OBJ.pprint()

#----------SOLVING----------
solver = pe.SolverFactory('gurobi') # Specify Solver

results = solver.solve(model, tee = False, keepfiles = False)

print()
print("Status:", results.solver.status)
print("Termination Condition:", results.solver.termination_condition)


# ---------POST-PROCESSING-------------------
print()
nodeofarea = []
for i in range(len(intensity)):
    if model.y[i].value == 1:
        nodeofarea.append(i)       
print("\nObjective function value: ", model.OBJ())

for i in range(len(intensity)):
    if i in nodeofarea:
        pass
    else:
        intensity[i] = 255

# resize final intensities and save as an image
arr = scipy.reshape(intensity,(h,w)).astype('uint8')
final_image = Image.fromarray(arr)
final_image.save('final_image.png')