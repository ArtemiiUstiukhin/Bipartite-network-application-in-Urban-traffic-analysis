import networkx as nx
import random as rnd
import matplotlib.pyplot as plt
import community as community_louvain
import matplotlib.cm as cm
import math
from networkx.algorithms import community
from networkx.algorithms import bipartite
from networkx.algorithms.community import greedy_modularity_communities


def getNextHop(M, N, prevHop, allK):
    temp = prevHop.split('.')
    m = int(temp[0])
    n = int(temp[1])
    k = int(temp[2])
    if k == 1:
        m -= 1
    elif k == 2:
        n += 1
    elif k == 3:
        m += 1
    elif k == 4:
        n -= 1

    if m == M:
        if 3 in allK:
            allK.remove(3)
    elif m == 0 or m == 1:
        if 1 in allK:
            allK.remove(1)

    if n == N:
        if 2 in allK:
            allK.remove(2)
    elif n == 0:
        if 4 in allK:
           allK.remove(4)

    if m == M and n == N:
        if 2 not in allK:
            allK.append(2)

    k = rnd.choice(allK)
    return str(m) + "." + str(n) + "." + str(k)

def isFinalHop(M, N, hop):
    temp = hop.split('.')
    m = int(temp[0])
    n = int(temp[1])
    k = int(temp[2])
    if m == M and n == N and k == 2:
        return True

    if n == 1 and k == 4:
        return True

    if rnd.randint(1, 50) == 1:
        return True

    return False

def generateRandomCarPath(M, N):
    path = []

    initialHop = str(0) + "." + str(rnd.randint(1, N)) + "." + str(3)
    hop = getNextHop(M, N, initialHop, [1, 2, 3, 4])
    path.append(hop)

    count = 0
    while not isFinalHop(M, N, hop) and count < M+N:
        allK = [1, 2, 3, 4]
        k = int(hop.split('.')[2])
        reverse = ((k - 1) + 2) % 4 + 1
        if rnd.randint(1, 100) == 1:
            allK = [((k - 1) + 2) % 4 + 1]
        else:
            allK.remove(reverse)

        hop = getNextHop(M, N, hop, allK)
        path.append(hop)
        count += 1

    return path

def reachDestination(M, N, path, initialPoint, endPoint):

    horDiff = int(endPoint.split('.')[1]) - int(initialPoint.split('.')[1])
    verDiff = int(endPoint.split('.')[0]) - int(initialPoint.split('.')[0])

    initialK = int(initialPoint.split('.')[2])
    if initialK == 1:
        verDiff += 1
    elif initialK == 2:
        horDiff -= 1
    elif initialK == 3:
        verDiff -= 1
    elif initialK == 4:
        horDiff += 1

    horK = 2 if horDiff > 0 else 4
    verK = 3 if verDiff > 0 else 1

    horLim = 0 if horDiff == 0 else int(horDiff / abs(horDiff))
    verLim = 0 if verDiff == 0 else int(verDiff / abs(verDiff))

    hop = initialPoint

    while horDiff != horLim or verDiff != verLim:
        if rnd.randint(1, 100) > 70:
            if horDiff != horLim:
                hop = getNextHop(M, N, hop, [horK])
                path.append(hop)
                horDiff -= int(horDiff / abs(horDiff))
            elif verDiff != verLim:
                hop = getNextHop(M, N, hop, [verK])
                path.append(hop)
                verDiff -= int(verDiff / abs(verDiff))
        else:
            if verDiff != verLim:
                hop = getNextHop(M, N, hop, [verK])
                path.append(hop)
                verDiff -= int(verDiff / abs(verDiff))
            elif horDiff != horLim:
                hop = getNextHop(M, N, hop, [horK])
                path.append(hop)
                horDiff -= int(horDiff / abs(horDiff))

    if verLim == 0 or horLim == 0:
        path.append(endPoint)
    else:
        endK = int(endPoint.split('.')[2])
        secondK = horK if endK % 2 == 0 else verK
        firstK = verK if endK % 2 == 0 else horK
        hop = getNextHop(M, N, hop, [firstK])
        path.append(hop)
        hop = getNextHop(M, N, hop, [secondK])
        path.append(hop)
        path.append(endPoint)


def generateCarPath(M, N):
    path = []

    initialPoint = str(0) + "." + str(rnd.randint(1, N)) + "." + str(3)
    midPoint =  str(rnd.randint(2, M-1)) + "." + str(rnd.randint(2, N-1)) + "." + str(rnd.randint(1, 4))
    endPoint = str(rnd.randint(2, M - 1)) + "." + str(1) + "." + str(4)
    if rnd.randint(1, 10) == 1:
        endPoint = str(M) + "." + str(N) + "." + str(2)
    if rnd.randint(1, 100) == 1:
        endPoint = str(rnd.randint(2, M - 1)) + "." + str(rnd.randint(2, N - 1)) + "." + str(rnd.randint(1, 4))


    reachDestination(M, N, path, initialPoint, midPoint)
    reachDestination(M, N, path, midPoint, endPoint)

    return path

def generateModelCarGraph(M, N, isRandom):
    B = nx.Graph()

    for i in range(M):
        for j in range(N):
            for k in range(4):
                if ((i + 1) == M and (k + 1) == 3) or ((j + 1) == N and (k + 1) == 2):
                    continue

                node = str(i + 1) + "." + str(j + 1) + "." + str(k + 1)
                B.add_node(node, bipartite=1)

    node = str(M) + "." + str(N) + "." + str(2)
    B.add_node(node, bipartite=1)
    K = 50
    for i in range((M*N)*K):
        car = "car" + str(i)
        B.add_node(car, bipartite=0)
        path = generateRandomCarPath(M, N) if isRandom else generateCarPath(M, N)
        for p in path:
            B.add_edge(car, p)

    return B

def generateGraph(n):
    k = 1 / (0.0762 * n + 1.52 * math.sqrt(n) + 7.575) # experimental
    return bipartite.random_graph(n * 50, n * 4, k)

def drawCommonGraph(G, partition):
    # draw the graph
    pos = nx.spring_layout(G)
    # color the nodes according to their partition
    cmap = cm.get_cmap('gist_rainbow', max(partition.values()) + 1)
    nx.draw_networkx_nodes(G, pos, partition.keys(), node_size=40,
        cmap = cmap, node_color = list(partition.values()))
    nx.draw_networkx_labels(G, pos, font_size=5)
    nx.draw_networkx_edges(G, pos, alpha=0.5)

def drawbipartiteGraph(G, partition):
    pos = nx.multipartite_layout(G, subset_key="bipartite")
    # color the nodes according to their partition
    cmap = cm.get_cmap('gist_rainbow', max(partition.values()) + 1)
    nx.draw_networkx_nodes(G, pos, partition.keys(),
                           node_size=10,
                           cmap=cmap,
                           node_color=list(partition.values()),
                           label=True)
    nx.draw_networkx_labels(G, pos, font_size=5)
    nx.draw_networkx_edges(G, pos)

def calculateLouvainDendrogram(G):
    dendo = community_louvain.generate_dendrogram(G)
    for level in range(len(dendo) - 1):
        t = community_louvain.partition_at_level(dendo, level)
        print("partition at level", level,
              "contains", len(set(t.values())), "communities",
              "with", len(t.values()), "values",
              "and", len(G.edges), "edges",
              "modularity", community_louvain.modularity(t, G))

def drawInducedGraph(G):
    part = community_louvain.best_partition(G)
    inducedGraph = community_louvain.induced_graph(part, G)
    part2 = community_louvain.best_partition(inducedGraph)
    drawCommonGraph(inducedGraph, part2)

def calculateInducedGraph():
    n = 20
    G1 = generateModelCarGraph(n, n, False)
    plt.figure(1)
    drawInducedGraph(G1)

    G2 = generateModelCarGraph(n, n, True)
    plt.figure(2)
    drawInducedGraph(G2)

    plt.show()

def calculateBestPartition(G):
    t = community_louvain.best_partition(G)
    print("partition contains", len(set(t.values())), "communities",
          "with", len(t.values()), "values",
          "and", len(G.edges), "edges",
          "modularity", community_louvain.modularity(t, G))

def calculatePartitioning(dimensions):
    for i in dimensions:
        print("Model", i, "x", i)
        print("Real car model")

        G1 = generateModelCarGraph(i, i, False)
        calculateBestPartition(G1)
        # uncomment to calculate Graph Dendrogram
        # calculateLouvainDendrogram(G1)

        print("Random car model")
        G2 = generateModelCarGraph(i, i, True)
        calculateBestPartition(G2)
        # uncomment to calculate Graph Dendrogram
        # calculateLouvainDendrogram(G2)

        print("Random Graph")

        G3 = generateGraph(i * i)
        calculateBestPartition(G3)
        # uncomment to calculate Graph Dendrogram
        # calculateLouvainDendrogram(G3)


calculatePartitioning([3, 5, 10, 30, 50, 70])

# uncomment for the InducedGraph calculation
# calculateInducedGraph() #



