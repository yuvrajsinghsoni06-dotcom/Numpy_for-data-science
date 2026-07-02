from collections import deque
def bfs(graph, root):
    visited = set()
    queue = deque([root])

    while queue:
        current = queue.popleft()
        visited.add(current)
        for i in graph[current]:
            if i not in visited:
                queue.append(i)
        

    return visited
if __name__ == "__main__":
    graph = {0: [1,2,3] , 1: [0,2] , 2: [0,1,4], 3: [0], 4: [2]}
    result = bfs(graph, 0)
    print(result)



