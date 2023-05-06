# importing geopy library

import itertools
from geopy.geocoders import Nominatim
import pandas as pd
import numpy as np
from scipy.spatial import distance_matrix
import matplotlib
import matplotlib.pylab as plt
import seaborn as sns
import pulp

# calling the Nominatim tool
loc = Nominatim(user_agent="GetLoc")

# entering the location name

tabr4=[
"Médiouna"
,
"Benslimane"
,
"Berrechid"
,
"Settat"
,
"Sidi Bennour",
"Oued Ed-Dahab",
"Aousserd​",
"Béni Mellal"
,
"Azilal"
,
"Fquih Ben Salah"
,
"Khénifra"
,
"Khouribga​"
,
"Rabat"
,
"Salé"
,
"Skhirate-Témara"
,
"Kénitra"
,
"Khémisset"]

# printing address

#partie 2:

tab3=[]
tab2 =[]
tab4 =[]
for i in tabr4:
    getLoc = loc.geocode(i+" Morocco")
    # print(getLoc.address)

    tab3.append(getLoc.latitude)
    tab2.append(getLoc.longitude)
    tab4.append(i)

    # print("Latitude = ", getLoc.latitude, "\n")
    # print("Longitude = ", getLoc.longitude)
    df = pd.DataFrame({
        'province': np.array(tab4),
        'x': np.array(tab3),
        'y': np.array(tab2),
        'demand': np.random.randint(3, 15, len(tab3)),

    })

n_customer = len(tabr4)
n_point = n_customer
vehicle_capacity = 250
df.loc[0, 'demand'] = 0

print(df)


distances = pd.DataFrame(distance_matrix(df[['x', 'y']].values, df[['x', 'y']].values), index=df.index, columns=df.index).values

fig, ax = plt.subplots(figsize=(20, 20))
sns.heatmap(distances, ax=ax, cmap='Reds', annot=True, fmt='.0f', cbar=True, cbar_kws={"shrink": .3}, linewidths=.1)
plt.title('distance matrix')
plt.show()

# check VRP state

plt.figure(figsize=(20, 20))

# draw problem state
for i, row in df.iterrows():
    if i == 0:
        plt.scatter(row['x'], row['y'], c='r')
        plt.text(row['x'] + 1, row['y'] + 1, 'depot')
    else:
        plt.scatter(row['x'], row['y'], c='black')
        demand = row['demand']
        plt.text(row['x'] + 1, row['y'] + 1, f'{i}({demand})')
from matplotlib.ticker import MultipleLocator
x_minor_locator = MultipleLocator(0.1)
ax = plt.gca()
ax.xaxis.set_minor_locator(x_minor_locator)

y_minor_locator = MultipleLocator(0.1)
ax = plt.gca()
ax.yaxis.set_minor_locator(y_minor_locator)




plt.title('points: id(demand)')
plt.show()

demands = df['demand'].values


# set problem
problem = pulp.LpProblem('cvrp_mip', pulp.LpMinimize)

# set variables
x = pulp.LpVariable.dicts('x', ((i, j) for i in range(n_point) for j in range(n_point)), lowBound=0, upBound=1,
                          cat='Binary')
n_vehicle = pulp.LpVariable('n_vehicle', lowBound=0, upBound=100, cat='Integer')
#

#


# set objective function
problem += pulp.lpSum([distances[i][j] * x[i, j] for i in range(n_point) for j in range(n_point)])

# set constrains
for i in range(n_point):
    problem += x[i, i] == 0

for i in range(1, n_point):
    problem += pulp.lpSum(x[j, i] for j in range(n_point)) == 1
    problem += pulp.lpSum(x[i, j] for j in range(n_point)) == 1

problem += pulp.lpSum(x[i, 0] for i in range(n_point)) == n_vehicle
problem += pulp.lpSum(x[0, i] for i in range(n_point)) == n_vehicle

# eliminate subtour
subtours = []
for length in range(2, n_point):
    subtours += itertools.combinations(range(1, n_point), length)

for st in subtours:
    demand = np.sum([demands[s] for s in st])
    arcs = [x[i, j] for i, j in itertools.permutations(st, 2)]
    problem += pulp.lpSum(arcs) <= np.max([0, len(st) - np.ceil(demand / vehicle_capacity)])

# solve problem
status = problem.solve()

# output status, value of objective function
status, pulp.LpStatus[status], pulp.value(problem.objective)

# check TSP problem and optimized route

plt.figure(figsize=(50, 50))

# draw problem state
for i, row in df.iterrows():
    if i == 0:
        plt.scatter(row['x'], row['y'], c='r')
        plt.text(row['x'] + 1, row['y'] + 1, 'depot')
    else:
        plt.scatter(row['x'], row['y'], c='black')
        demand = row['demand']
        plt.text(row['x'] + 1, row['y'] + 1, f'{i}({demand})')

from matplotlib.ticker import MultipleLocator
x_minor_locator = MultipleLocator(0.1)
ax = plt.gca()
ax.xaxis.set_minor_locator(x_minor_locator)

y_minor_locator = MultipleLocator(0.1)
ax = plt.gca()
ax.yaxis.set_minor_locator(y_minor_locator)






# draw optimal route
cmap = matplotlib.cm.get_cmap('Dark2')
routes = [(i, j) for i in range(n_point) for j in range(n_point) if pulp.value(x[i, j]) == 1]

for v in range(int(pulp.value(n_vehicle))):

    # identify the route of each vehicle
    vehicle_route = [routes[v]]
    while vehicle_route[-1][1] != 0:
        for p in routes:
            if p[0] == vehicle_route[-1][1]:
                vehicle_route.append(p)
                print(vehicle_route)
                break

    # draw for each vehicle
    arrowprops = dict(arrowstyle='->', connectionstyle='arc3', edgecolor=cmap(v))
    for i, j in vehicle_route:
        plt.annotate('', xy=[df.iloc[j]['x'], df.iloc[j]['y']], xytext=[df.iloc[i]['x'], df.iloc[i]['y']],
                     arrowprops=arrowprops)


plt.show()
print(problem.solve())

