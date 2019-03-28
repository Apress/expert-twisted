import os
import graphviz

dot = graphviz.Digraph()

for dirpath, dirnames, files in os.walk('.'):
    dot.node(dirpath, label=os.path.basename(dirpath) + "/")
    for f in files:
        fpath = os.path.join(dirpath, f)
        dot.node(fpath, label=f)
        dot.edge(dirpath, fpath)
    for d in dirnames:
        dpath = os.path.join(dirpath, d)
        dot.node(dpath, label=os.path.basename(d) + "/")
        dot.edge(dirpath, dpath)


print '\n'.join(dot)
