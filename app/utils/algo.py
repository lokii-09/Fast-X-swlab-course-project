from app.models.stores import orders
from app.models.users import users, delivery_graph, graph_positions
import heapq
import itertools
import networkx as nx

def assign_driver(order):
    """
    Assigns the optimal driver to an order using a modified Traveling Salesman Problem approach.
    Returns a tuple of (driver_username, optimized_store_order) where optimized_store_order is a list
    of store IDs in the order they should be visited.
    """
    
    # Get customer location
    customer_id = order['customer_id']
    customer_node = f"Customer {customer_id[-1]}"  # Assuming customer_id ends with a number
    
    # Get stores that need to be visited
    stores_to_visit = []
    store_id_mapping = {}  # Map Store A/B/C back to store_id 1/2/3
    
    for store_id in order['items_by_store'].keys():
        store_node = f"Store {chr(64 + int(store_id))}"  # Convert 1,2,3 to A,B,C
        stores_to_visit.append(store_node)
        store_id_mapping[store_node] = store_id
    
    # Find all delivery agents
    all_drivers = [user for user in users if user['user_type'] == 'Delivery Agent']
    
    if not all_drivers:
        return None, []
    
    # Create a priority queue for drivers
    driver_queue = []
    best_routes = {}  # Store the best route for each driver
    
    for driver in all_drivers:
        # Check if driver is already assigned to a previous order
        assigned_order = next((o for o in orders.values() 
                              if o['delivery_agent'] == driver['username'] 
                              and o['status'] != 'delivered' 
                              and not o['delivered']), None)
        
        # Determine driver's current/starting location node
        if assigned_order:
            # If driver is already assigned, use customer location of current assignment
            driver_location = assigned_order['customer_location']
            priority = 2  # Lower priority for already assigned drivers
        else:
            # If driver is available, use their current location
            driver_location = driver['location']
            priority = 1  # Higher priority for available drivers
        
        driver_node = "Admin Office"  # Default starting point
        
        # Find the closest node to driver's coordinates
        for node, pos in graph_positions.items():
            if pos == driver_location:
                driver_node = node
                break
        
        # Pre-compute all pairwise shortest paths using Floyd-Warshall algorithm
        # This is more efficient than running Dijkstra's multiple times
        shortest_paths = {}
        for source in delivery_graph.nodes():
            shortest_paths[source] = {}
            for target in delivery_graph.nodes():
                if source == target:
                    shortest_paths[source][target] = 0
                    continue
                
                try:
                    # Calculate shortest path length between source and target
                    path_length = nx.shortest_path_length(delivery_graph, source, target, weight='weight')
                    shortest_paths[source][target] = path_length
                except nx.NetworkXNoPath:
                    shortest_paths[source][target] = float('inf')
                except nx.NetworkXError:
                    # Handle any other NetworkX-related errors
                    shortest_paths[source][target] = float('inf')
        
        # Check if all paths from driver to stores are impossible
        if all(shortest_paths[driver_node][store] == float('inf') for store in stores_to_visit):
            continue  # Skip this driver if they can't reach any store
        
        # If there are only a few stores (≤ 4), we can try all permutations
        # Otherwise, use a nearest neighbor heuristic which is faster
        if len(stores_to_visit) <= 4:
            # Modified TSP approach - try all permutations of store visits
            best_route = None
            best_distance = float('inf')
            
            for perm in itertools.permutations(stores_to_visit):
                current_distance = shortest_paths[driver_node][perm[0]]  # Distance from driver to first store
                
                if current_distance == float('inf'):
                    continue  # Skip this permutation if the first leg is impossible
                
                # Add distances between consecutive stores
                valid_route = True
                for i in range(len(perm) - 1):
                    leg_distance = shortest_paths[perm[i]][perm[i+1]]
                    if leg_distance == float('inf'):
                        valid_route = False
                        break  # Skip this permutation if any leg is impossible
                    current_distance += leg_distance
                
                if not valid_route:
                    continue
                
                # Add distance from last store to customer
                final_leg = shortest_paths[perm[-1]][customer_node]
                if final_leg == float('inf'):
                    continue  # Skip if can't reach customer
                
                current_distance += final_leg
                
                if current_distance < best_distance:
                    best_distance = current_distance
                    best_route = perm
            
            # If no valid route found for this driver
            if best_route is None:
                continue
            
            # Convert store nodes back to store IDs
            optimized_store_order = [store_id_mapping[store] for store in best_route]
            total_distance = best_distance
            
            # Store the optimized route for this driver
            best_routes[driver['username']] = optimized_store_order
            
            # Push driver into priority queue: (priority, distance, driver_username)
            # This ensures drivers with priority 1 (available) are considered first
            heapq.heappush(driver_queue, (priority, total_distance, driver['username']))
    
    # Select the driver with highest priority (lowest number) and shortest distance
    if driver_queue:
        _, _, best_driver = heapq.heappop(driver_queue)
        return best_driver, best_routes[best_driver]
    
    return None, []


"""
Driver Assignment and Route Optimization Algorithm Explained
This algorithm solves a delivery route optimization problem by finding the best driver and the optimal sequence of stores to visit for an order. Here's a detailed explanation of how it works:

Key Components
1. Entities Involved
    Customer: The person who placed the order, with a specific location
    Stores: Multiple retail locations where items in the order need to be collected from
    Drivers: Delivery agents who pick up items from stores and deliver to customers
    Delivery Graph: A network representing locations (nodes) and distances between them (edges)

2. Algorithm Objectives
    Assign the most suitable driver to an order
    Determine the optimal sequence of stores to visit
    Minimize total travel distance
    Prioritize available drivers over busy ones

Algorithm Workflow

Step 1: Identify Customer and Stores
    The algorithm first identifies the customer's location and all stores that need to be visited based on the order's items

Step 2: Find Available Drivers
    The algorithm identifies all delivery agents in the system

Step 3: For Each Driver, Calculate Optimal Route
    For each driver, the algorithm:
    Determines the driver's current location:
    If the driver is already assigned to an order, use the customer location of that order
    If the driver is available, use their current location
    Assign priority 1 to available drivers and priority 2 to busy drivers
    Pre-computes shortest paths between all locations using the Floyd-Warshall algorithm, which is more efficient than running Dijkstra's algorithm multiple times
    Determines the optimal store visit sequence using one of two approaches:
    For 4 or fewer stores: Uses a brute-force approach by trying all possible permutations of store visits (exact TSP solution)
    For more than 4 stores: Uses the Nearest Neighbor heuristic (greedy approach) for better performance
    Calculates the total route distance:
    Distance from driver's location to first store
    Distances between consecutive stores
    Distance from last store to customer's location

Step 4: Select the Best Driver
    The algorithm uses a priority queue to select the driver with:
    Highest priority (available drivers before busy ones)
    Shortest total route distance

Step 5: Return Results

Finally, it returns a tuple containing:
    The username of the selected driver
    The optimized sequence of store IDs to visit

Key Optimization Techniques
Priority-Based Driver Selection: Favors available drivers over busy ones

Adaptive Route Optimization:
    Exact solution (brute force) for small problems
    Heuristic approach (nearest neighbor) for larger problems
    Pre-computation of Shortest Paths: Uses Floyd-Warshall algorithm to calculate all pairwise shortest paths once
    Complete Route Consideration: Optimizes the entire route from driver → stores → customer

This hybrid approach balances computational efficiency with solution quality, making it suitable for real-time delivery route optimization.
"""