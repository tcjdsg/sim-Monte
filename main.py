#!/usr/bin/env python

# This is a sample Python script.
import pandas as pd

# libraries
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

##  DIRECTED 有向图
def drawGraph():
    df = pd.DataFrame({'from': ['D', 'A', 'B', 'C', 'A'], 'to': ['A', 'D', 'A', 'E', 'C']})

    # Build your graph. Note that we use the DiGraph function to create the graph!
    # create_using=nx.DiGraph()创建有向图,默认是无向图
    G = nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.DiGraph())

    # Make the graph 有向图
    nx.draw(G, with_labels=True, node_size=1500, alpha=0.3, arrows=True)
    plt.show()

a=[(1,2),(1,3)]
b=(1,2)
if b in a:
    print("true")
