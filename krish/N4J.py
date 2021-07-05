from py2neo import Graph, Node, Relationship

graph = Graph(password='abc123')

graph.delete_all()

def push_data(dct):
    nodes = {}

    if dct == None:
        return

    for pg in dct:
        if pg not in nodes.keys():
            nodes[pg] = Node('pg', name=pg)
            graph.create(nodes[pg])

        connected_nodes = dct[pg]

        for cn in connected_nodes:
            if cn not in nodes.keys():
                nodes[cn] = Node('pg', name=cn)
                graph.create(nodes[cn])

            graph.create(Relationship(nodes[pg], ' ', nodes[cn]))
