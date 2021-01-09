import numpy as np
import pandas as pd
import pprint
import json
from bson import json_util 
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D


#define federal tax brackets 2020
def fed_tax_rate(income_pre):
    if(income_pre < 1):
        return 0
    else: 
        if(income_pre < 48535):
            return 0.15
        else:
            if(income_pre < 97069):
                return 0.205
            else:
                if(income_pre < 150473):
                    return 0.26
                else:
                    if(income_pre < 214368):
                        return 0.29
                    else:
                        return 0.33

#define provincial (BC) tax brackets 2020
def prov_tax_rate(income_pre):
    if(income_pre < 1):
        return 0
    else:        
        if(income_pre < 41725):
            return 0.0506
        else:
            if(income_pre < 83451):
                return 0.077
            else:
                if(income_pre < 95812):
                    return 0.105
                else:
                    if(income_pre < 116344):
                        return 0.1229
                    else:
                        if(income_pre < 157748):
                            return 0.147
                        else:
                            if(income_pre < 220000):
                                return 0.168
                            else:
                                return 0.205

income = 50000
#console debug variables
print('income: '+str(income))
print('federal tax bracket: '+str(fed_tax_rate(income)*100)+'%')
print('provincial tax bracket: '+str(prov_tax_rate(income)*100)+'%')

#define income and savings rate ranges

delta_i = 1000
delta_p = 0.01
income = np.arange(10000, 250000, delta_i)
RRSP_p = np.arange(0.0, 1.0, delta_p)

income_df = pd.DataFrame(income, index = income)


#generate a data frame of contribution amounts based on income and savings rate
contribution = pd.DataFrame([])

for index, row in income_df.iterrows():
    dummy = row[0]*RRSP_p
    dummy_df = pd.DataFrame(dummy)
    contribution = pd.concat([contribution, dummy_df], axis=1)

contribution.columns = income

#generate a data frame from the previous table with incomes, savings, and an empty columns for values. 

inandcont = pd.DataFrame([])

for label, content in contribution.iteritems():
    dummy = pd.Series([label]*content.size)
    dummy2 = pd.concat([dummy, content], axis=1, ignore_index=True)
    inandcont = pd.concat([inandcont, dummy2], axis=0, ignore_index=True)


evaluation = pd.DataFrame([])
for index, row in inandcont.iterrows():
    dummy = pd.Series((row[0]*(fed_tax_rate(row[0])+prov_tax_rate(row[0])))-(row[0]*(fed_tax_rate(row[1])+prov_tax_rate(row[1])))+(row[1]*(fed_tax_rate(row[1])+prov_tax_rate(row[1]))))
    evaluation = pd.concat([evaluation, dummy], axis=0, ignore_index=True)


#join the dataframes into a correct table
table = pd.concat([inandcont, evaluation], axis=1, ignore_index=True)

table.columns = ["X", "Y", "Z"]


# convert back to percentages of income so the table can be passed as a 2D array. 

table_master = pd.DataFrame([])
for index, row in table.iterrows(): 
    y_values = (row["Y"]/row["X"])*100
    y_values = y_values.round(0)
    dummy = pd.DataFrame([row["X"],y_values, row["Z"].round(0)])
    table_master = pd.concat([table_master, dummy.T], axis=0)

table_master.columns = ["X", "Y", "Z"]

#make the table usable in the bullshit way the plotter needs

plotable_table = table_master.pivot(index = "X", columns = "Y", values = "Z")
plotable_table.round(0)
print(plotable_table)

#define x, y and z of the plot
X = plotable_table.columns
Y = plotable_table.index
Z = plotable_table


#define the contour marker levels
levels = [0, 100, 500, 1000, 2000, 5000, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 150000]

#define plot & subplot
fig, ax = plt.subplots()
CS = ax.contour(X, Y, Z, levels = levels)

#define currency formatter 
fmt = '${x:,.0f}'
format_dollar = mtick.StrMethodFormatter(fmt)

#set labels
ax.set_title('Difference in 2020 Income Taxes Paid (Fed + BC) with RRSP Contribution')
ax.set_ylabel("Income before tax (CAD)")
ax.set_xlabel("Percentage of income contributed to RRSP (%)")

#set ticks
major_ticks_x = np.arange(min(X), max(X), 5)
major_ticks_y = np.arange(min(Y), max(Y), 10000)
ax.set_xticks(major_ticks_x)
ax.set_yticks(major_ticks_y)

#format y axis
ax.yaxis.set_major_formatter(format_dollar) 

#add labels with formatted names
ax.clabel(CS, levels, inline=True, fontsize=8, inline_spacing = 2, fmt=format_dollar, manual = True)

plt.show()
