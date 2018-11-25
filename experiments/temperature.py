import numpy as np
from matplotlib import pyplot as plt

X = np.array([400, 450, 900, 390, 550])
# TODO: Write the code as explained in the instructions
T = np.linspace(0.01, 5.0, num=100)
P = []
for x in X:
    tRow=[]
    for t in T:
        denominator=0
        for x_mechane in X:
            denominator += (x_mechane**(-1/t))
        tRow.append((x**(-1/t))/denominator)
    P.append(tRow)

print(P)

for i in range(len(X)):
    plt.plot(T, P[i], label=str(X[i]))

plt.xlabel("T")
plt.ylabel("P")
plt.title("Probability as a function of the temperature")
plt.legend()
plt.grid()
plt.show()
exit()
