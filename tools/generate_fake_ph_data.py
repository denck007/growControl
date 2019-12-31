import random

low = 1
high = 9
spacing = 1/8

with open("random_ph_data.csv",'w') as f:
    for ii in range(50):
        f.write("{:.4f}\n".format(random.randrange(low*1/spacing,high*1/spacing,1)*spacing))