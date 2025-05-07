import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
import heapq
import json
from datetime import datetime

#formatting time 
def parse_time(time_str):
    return datetime.strptime(time_str.strip(), "%I:%M %p").time()

#loading json tasks
def load_validate_tasks(filename, valid_locations):
    with open(filename, "r") as f:
        data = json.load(f)

    parsed_tasks = []
    for item in data:
        title = item.get("title") or item.get("className") or item.get("taskName")
        start_str = item["startTime"]
        end_str = item["endTime"]
        location = item["location"]
        priority = item.get("priority", "Medium")

        if location not in valid_locations:
            print(f"invalid location '{location} for task '{title}")
            continue

        start = parse_time(start_str)
        end = parse_time(end_str)

        if end <= start:
            print(f"End time must be after start time for task '{title}'")
            continue

        parsed_tasks.append({
            "title": title,
            "start": start,
            "end" : end,
            "location": location
        })
    return parsed_tasks

# Configure style settings
MAIN_BG = "#F5F5F5"  # Main background color
TITLE_COLOR = "#FF6600"  # Orange for titles
BUTTON_BG = "#FFCC99"  # Light orange for buttons
BUTTON_BG_HOVER = "#FFA64D"  # Darker orange for button hover
DIJKSTRA_BUTTON_BG = "#99CCFF"  # Light blue for Dijkstra buttons
DIJKSTRA_BUTTON_BG_HOVER = "#66B2FF"  # Darker blue for Dijkstra button hover
SUCCESS_COLOR = "#008000"  # Green for success messages
ERROR_COLOR = "#B22222"  # Red for error messages

class CampusGraph:
    """Class to handle campus graph data and algorithms"""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.build_graph()
    
    def build_graph(self):
        buildings = ['Pollak', 'TSU', 'SGMH', 'MH', 'ECS', 'SRC', 'LH', 'KHS']
        edges = [
            ('Pollak', 'TSU', 2), ('TSU', 'SRC', 3), ('TSU', 'MH', 4),
            ('MH', 'LH', 5), ('LH', 'SGMH', 6), ('SGMH', 'Pollak', 7),
            ('Pollak', 'ECS', 8), ('ECS', 'KHS', 9), ('KHS', 'SRC', 10),
            ('SRC', 'KHS', 11), ('SRC', 'Pollak', 12), ('LH', 'Pollak', 13),
            ('MH', 'Pollak', 14)
        ]
        for building in buildings:
            self.graph.add_node(building)
        for u, v, w in edges:
            self.graph.add_edge(u, v, weight=w)
    
    def get_buildings(self):
        return list(self.graph.nodes())
    
    def dijkstra(self, source, target):
        """
        Implements Dijkstra's algorithm to find the shortest path between two named nodes
        Returns both the total distance and the complete path
        """
        name_to_index = {name: i for i, name in enumerate(self.graph.nodes)}
        index_to_name = {i: name for name, i in name_to_index.items()}

        n = len(self.graph.nodes)
        graph_list = [[] for _ in range(n)]

        for u, v, data in self.graph.edges(data=True):
            u_idx = name_to_index[u]
            v_idx = name_to_index[v]
            weight = data.get('weight', 1)
            graph_list[u_idx].append((v_idx, weight))
            graph_list[v_idx].append((u_idx, weight))

        # Initialize distances and previous node tracking
        dist = [float('inf')] * n
        prev = [None] * n
        src_idx = name_to_index[source]
        tgt_idx = name_to_index[target]
        dist[src_idx] = 0
        pq = [(0, src_idx)]  # Priority queue (distance, node)

        # Main Dijkstra algorithm
        while pq:
            current_dist, u = heapq.heappop(pq)
            if current_dist > dist[u]:
                continue
            for v, weight in graph_list[u]:
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], v))

        # Reconstruct the path
        path = []
        current = tgt_idx
        if prev[current] is not None or current == src_idx:
            while current is not None:
                path.append(index_to_name[current])
                current = prev[current]
        
        path.reverse()
        return dist[tgt_idx], path


# KMP Search Algorithm
def kmp_search(text, pattern):
    def build_lps(pattern):
        lps = [0] * len(pattern)
        length = 0
        i = 1
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length-1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    lps = build_lps(pattern)
    i = j = 0
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == len(pattern):
            return i - j
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j-1]
            else:
                i += 1
    return -1


class SmartCampusNavigator:
    def __init__(self, root):
        self.root = root
        self.root.title("CSUF Smart Campus Navigator")
        self.root.geometry("800x600")
        self.root.configure(bg=MAIN_BG)
        
        # Initialize campus graph
        self.campus = CampusGraph()
        self.highlighted_building = None
        self.current_path = None
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create main frames for each tab
        self.home_frame = ttk.Frame(self.notebook)
        self.search_frame = ttk.Frame(self.notebook)
        self.dijkstra_frame = ttk.Frame(self.notebook)
        self.activity_frame = ttk.Frame(self.notebook)
        
        # Add frames to notebook
        self.notebook.add(self.home_frame, text="Home")
        self.notebook.add(self.search_frame, text="Search Buildings")
        self.notebook.add(self.dijkstra_frame, text="Find Shortest Path")
        self.notebook.add(self.activity_frame, text="Create a Schedule")
        
        # Setup all tabs
        self.setup_home_tab()
        self.setup_search_tab()
        self.setup_dijkstra_tab()
        self.setup_activity_tab()

    def setup_home_tab(self):
        # Create and place widgets for the home tab
        title = tk.Label(self.home_frame, text="CSUF Smart Campus Navigator", 
                        font=("Helvetica", 16, "bold"), fg=TITLE_COLOR)
        title.pack(pady=30)
        
        welcome_text = """Welcome to the CSUF Smart Campus Navigator!
        
        This application helps you navigate around the CSUF campus.
        
        Features:
        • Search for buildings
        • View the campus map
        • Find the shortest path between buildings
        • Create an ideal schedule
        
        Select a tab above to get started.
        """
        
        welcome = tk.Label(self.home_frame, text=welcome_text, 
                          font=("Helvetica", 12), justify=tk.LEFT)
        welcome.pack(pady=20)
        
        # Add map button to home tab
        map_btn = tk.Button(self.home_frame, text="Show Campus Map", 
                           font=("Helvetica", 12), bg=BUTTON_BG, fg="black", 
                           relief="raised", bd=3, command=lambda: self.show_map())
        map_btn.pack(pady=20, ipadx=20, ipady=10)
        
        # Configure button hover effects
        map_btn.bind("<Enter>", lambda e: map_btn.config(bg=BUTTON_BG_HOVER))
        map_btn.bind("<Leave>", lambda e: map_btn.config(bg=BUTTON_BG))

    def setup_search_tab(self):
        # Create and place widgets for the search tab
        title = tk.Label(self.search_frame, text="Search Buildings", 
                        font=("Helvetica", 16, "bold"), fg=TITLE_COLOR)
        title.pack(pady=20)
        
        instruction = tk.Label(self.search_frame, 
                              text="Enter the name of the building to search:", 
                              font=("Helvetica", 12))
        instruction.pack(pady=10)
        
        # Search entry and button frame
        search_frame = ttk.Frame(self.search_frame)
        search_frame.pack(pady=10)
        
        self.search_entry = tk.Entry(search_frame, font=("Helvetica", 12), width=25)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = tk.Button(search_frame, text="Search", font=("Helvetica", 12), 
                              bg=BUTTON_BG_HOVER, fg="white", command=self.search_building)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Configure button hover effects
        search_btn.bind("<Enter>", lambda e: search_btn.config(bg=BUTTON_BG_HOVER))
        search_btn.bind("<Leave>", lambda e: search_btn.config(bg=BUTTON_BG_HOVER))
        
        # Result display
        self.search_result = tk.Label(self.search_frame, text="", 
                                     font=("Helvetica", 14), fg=SUCCESS_COLOR)
        self.search_result.pack(pady=20)
        
        # Show on map button (initially disabled)
        self.show_on_map_btn = tk.Button(self.search_frame, text="Show on Map", 
                                        font=("Helvetica", 12), bg=BUTTON_BG, 
                                        fg="black", relief="raised", bd=3, state=tk.DISABLED, 
                                        command=lambda: self.show_map())
        self.show_on_map_btn.pack(pady=10)
        
        # Configure button hover effects
        self.show_on_map_btn.bind("<Enter>", lambda e: self.show_on_map_btn.config(bg=BUTTON_BG_HOVER))
        self.show_on_map_btn.bind("<Leave>", lambda e: self.show_on_map_btn.config(bg=BUTTON_BG))

    def setup_dijkstra_tab(self):
        # Create and place widgets for the Dijkstra tab
        title = tk.Label(self.dijkstra_frame, text="Find Shortest Path", 
                        font=("Helvetica", 16, "bold"), fg=TITLE_COLOR)
        title.pack(pady=20)
        
        # Start and end selection
        selection_frame = ttk.Frame(self.dijkstra_frame)
        selection_frame.pack(pady=10)
        
        ttk.Label(selection_frame, text="Start: ").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(selection_frame, text="End: ").grid(row=1, column=0, padx=5, pady=5)
        
        buildings = self.campus.get_buildings()
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        
        start_combo = ttk.Combobox(selection_frame, textvariable=self.start_var, 
                                  values=buildings, width=20)
        start_combo.grid(row=0, column=1, padx=5, pady=5)
        
        end_combo = ttk.Combobox(selection_frame, textvariable=self.end_var, 
                                values=buildings, width=20)
        end_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Calculate button
        calc_btn = tk.Button(self.dijkstra_frame, text="Blammo - Show Distance", 
                            font=("Helvetica", 12, "bold"), bg=DIJKSTRA_BUTTON_BG, fg="black", 
                            relief="raised", bd=3, command=self.calculate_path)
        calc_btn.pack(pady=15)
        
        # Configure button hover effects
        calc_btn.bind("<Enter>", lambda e: calc_btn.config(bg=DIJKSTRA_BUTTON_BG_HOVER))
        calc_btn.bind("<Leave>", lambda e: calc_btn.config(bg=DIJKSTRA_BUTTON_BG))
        
        # Display result
        self.path_result = tk.Label(self.dijkstra_frame, text="", 
                                   font=("Helvetica", 14))
        self.path_result.pack(pady=10)
        
        # Path details
        self.path_details = tk.Label(self.dijkstra_frame, text="", 
                                    font=("Helvetica", 12))
        self.path_details.pack(pady=5)
        
        # Show on map button (initially disabled)
        self.show_path_btn = tk.Button(self.dijkstra_frame, text="Show Path on Map", 
                                      font=("Helvetica", 12), bg=DIJKSTRA_BUTTON_BG, 
                                      relief="raised", bd=3, state=tk.DISABLED, 
                                      command=lambda: self.show_map(True))
        self.show_path_btn.pack(pady=10)
        
        # Configure button hover effects
        self.show_path_btn.bind("<Enter>", lambda e: self.show_path_btn.config(bg=DIJKSTRA_BUTTON_BG_HOVER))
        self.show_path_btn.bind("<Leave>", lambda e: self.show_path_btn.config(bg=DIJKSTRA_BUTTON_BG))
    
    def setup_activity_tab(self):
        self.error_label = tk.Label(
        self.activity_frame,
        text="",
        fg=ERROR_COLOR,
        font=("Helvetica", 10, "italic")
    )
        self.error_label.grid(row=9, column=0, columnspan=2, pady=5)
        #checkbox to load json file
        self.use_json_var = tk.BooleanVar(value=False)
        load_json_checkbox = ttk.Checkbutton(
            self.activity_frame,
            text="Load schedule from JSON file",
            variable=self.use_json_var,
            command=lambda: self.reload_tasks(task_list)
        )
        load_json_checkbox.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Title
        title = tk.Label(self.activity_frame, text="Create a Schedule",
                        font=("Helvetica", 16, "bold"), fg=TITLE_COLOR)
        title.grid(row=1, column=0, columnspan=2, pady=10)

        # Task list display
        task_list_frame = ttk.LabelFrame(self.activity_frame, text="Added Classes/Tasks")
        task_list_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)

        task_list = tk.Listbox(task_list_frame, width=50, height=8, font=("Helvetica", 10))
        task_list.grid(row=0, column=0, padx=5, pady=5)

        # Load tasks if JSON is selected
        self.tasks = []
        if self.use_json_var.get():
            self.tasks = load_validate_tasks("tasks.json", self.campus.get_buildings())
            for task in self.tasks:
                task_list.insert(tk.END, f"• {task['title']} @ {task['location']} ({task['start']} - {task['end']})")

        # Input section
        ttk.Label(self.activity_frame, text="Class name:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        class_name_entry = ttk.Entry(self.activity_frame, width=25)
        class_name_entry.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(self.activity_frame, text="Start time (HH:MM AM or PM):").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        start_time_entry = ttk.Entry(self.activity_frame, width=25)
        start_time_entry.grid(row=4, column=1, padx=5, pady=2)

        ttk.Label(self.activity_frame, text="End time (HH:MM) AM or PM:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        end_time_entry = ttk.Entry(self.activity_frame, width=25)
        end_time_entry.grid(row=5, column=1, padx=5, pady=2)

        ttk.Label(self.activity_frame, text="Building Name:").grid(row=6, column=0, sticky="e", padx=5, pady=2)
        building_entry = ttk.Entry(self.activity_frame, width=25)
        building_entry.grid(row=6, column=1, padx=5, pady=2)
        
        ttk.Label(self.activity_frame, text="Priority: ").grid(row=7, column=0, sticky="e", padx=5, pady=2)
        priority_var = tk.StringVar()
        priority_dropdown = ttk.Combobox(self.activity_frame, textvariable=priority_var, values=["High", "Medium", "Low"], width=23)
        priority_dropdown.grid(row=7, column=1, padx=5, pady=2)
        priority_dropdown.set("Medium")

        # Submit Task
        def submit_task():
            class_name = class_name_entry.get()
            start_time = start_time_entry.get()
            end_time = end_time_entry.get()
            building = building_entry.get()
            priority = priority_var.get()

            if building not in self.campus.get_buildings():
                self.error_label.config(text="Invalid building name. Please enter a valid CSUF building.")
                return

            try:
                start = parse_time(start_time)
                end = parse_time(end_time)
                if end > start:
                    task = {
                        "title": class_name,
                        "start": start,
                        "end": end,
                        "location": building,
                        "priority" : priority

                    }
                    self.tasks.append(task)
                    start_str = start.strftime("%I:%M %p")
                    end_str = end.strftime("%I:%M %p")
                    task_list.insert(tk.END, f"• {class_name} @ {building} ({start_str} - {end_str})")


                    # Clear inputs
                    class_name_entry.delete(0, tk.END)
                    start_time_entry.delete(0, tk.END)
                    end_time_entry.delete(0, tk.END)
                    building_entry.delete(0, tk.END)
                else:
                    self.error_label.config(text="End time must be after start time.")
            except ValueError:
                self.error_label.config(text="Invalid time format.")

        submit_btn = ttk.Button(self.activity_frame, text="Submit Task", command=submit_task)
        submit_btn.grid(row=8, column=0, columnspan=2, pady=10)
    
    def reload_tasks(self, task_list):
        task_list.delete(0, tk.END)
        self.tasks = []
        if self.use_json_var.get():
            self.tasks = load_validate_tasks("tasks.json", self.campus.get_buildings())
            for task in self.tasks:
                start_str = task['start'].strftime("%I:%M %p")
                end_str = task['end'].strftime("%I:%M %p")
                display = f"• {task['title']} @ {task['location']} ({start_str} - {end_str})"
                task_list.insert(tk.END, display)


        #suggesting schedule, implementing activity algorithm
        def activity_selector():
            sorted_tasks = sorted(self.tasks, key=lambda x: x["end"])
            result = []
            last_end = None

            for task in sorted_tasks:
                if last_end is None or task["start"] >= last_end:
                    result.append(task)
                    last_end = task["end"]

            result_win = tk.Toplevel(self.activity_frame)
            result_win.title("Recommended Schedule")

            tk.Label(result_win, text="Recommended Schedule", font=("Helvetica", 14, "bold")).pack(pady=10)

            result_box = tk.Listbox(result_win, width=50, height=10, font=("Helvetica", 10))
            result_box.pack(padx=10, pady=10)

            for task in result:
                start_str = task['start'].strftime("%I:%M %p")
                end_str = task['end'].strftime("%I:%M %p")
                result_box.insert(tk.END, f"• {task['title']} @ {task['location']} ({start_str} - {end_str})")


        suggest_btn = ttk.Button(self.activity_frame, text="Suggest Schedule", command=activity_selector)
        suggest_btn.grid(row=8, column=0, columnspan=2, pady=5)


    def search_building(self):
        building = self.search_entry.get()
        found = False
        found_building = None
        
        for b in self.campus.get_buildings():
            if kmp_search(b.lower(), building.lower()) != -1:
                found = True
                found_building = b
                break
                
        if found:
            self.highlighted_building = found_building
            self.search_result.config(text=f"{found_building} was found!", fg="#008000")
            self.show_on_map_btn.config(state=tk.NORMAL)
        else:
            self.search_result.config(text=f"{building} was not found.", fg="#B22222")
            self.show_on_map_btn.config(state=tk.DISABLED)

    def calculate_path(self):
        start = self.start_var.get()
        end = self.end_var.get()
        
        if not start or not end:
            self.path_result.config(text="Please select both buildings.", fg="#B22222")
            return
            
        if start == end:
            self.path_result.config(text="You're already there!", fg="#008000")
            self.show_path_btn.config(state=tk.DISABLED)
            self.current_path = None
            return
            
        distance, path = self.campus.dijkstra(start, end)
        self.path_result.config(
            text=f"Shortest path from {start} to {end} is {distance} units.", 
            fg="#008000"
        )
        
        path_str = " → ".join(path)
        self.path_details.config(text=f"Path: {path_str}")
        
        self.current_path = path
        self.show_path_btn.config(state=tk.NORMAL)

    def show_map(self, show_path=False):
        pos = nx.spring_layout(self.campus.graph, seed=42, k=0.9)
        
        plt.figure(figsize=(10, 8))
        
        # Draw all edges in light gray
        nx.draw_networkx_edges(self.campus.graph, pos, width=1.0, alpha=0.5, edge_color='gray')
        
        # Draw path edges in blue with increased width if showing path
        if show_path and self.current_path and len(self.current_path) > 1:
            path_edges = [(self.current_path[i], self.current_path[i+1]) 
                          for i in range(len(self.current_path)-1)]
            nx.draw_networkx_edges(self.campus.graph, pos, edgelist=path_edges, 
                                  width=4.0, edge_color='blue', arrows=True, 
                                  arrowstyle='->', arrowsize=20)
        
        # Color nodes appropriately
        node_colors = []
        node_sizes = []
        
        for node in self.campus.graph.nodes:
            if show_path and self.current_path:
                if node == self.current_path[0]:  # Starting node
                    node_colors.append('green')
                    node_sizes.append(3500)
                elif node == self.current_path[-1]:  # Ending node
                    node_colors.append('red')
                    node_sizes.append(3500)
                elif node in self.current_path:  # Path nodes
                    node_colors.append('lightblue')
                    node_sizes.append(3000)
                else:  # Other nodes
                    node_colors.append('pink')
                    node_sizes.append(2500)
            else:
                if node == self.highlighted_building:
                    node_colors.append('red')
                    node_sizes.append(3500)
                else:
                    node_colors.append('pink')
                    node_sizes.append(2500)
        
        # Draw nodes
        nx.draw_networkx_nodes(self.campus.graph, pos, node_color=node_colors, 
                              node_size=node_sizes, edgecolors='black')
        
        # Draw node labels
        nx.draw_networkx_labels(self.campus.graph, pos, font_size=10, font_weight='bold')
        
        # Draw edge weights
        edge_labels = nx.get_edge_attributes(self.campus.graph, 'weight')
        nx.draw_networkx_edge_labels(self.campus.graph, pos, edge_labels=edge_labels, font_size=8)
        
        # Add a title based on what's being shown
        if show_path and self.current_path:
            path_str = " → ".join(self.current_path)
            plt.title(f"Shortest Path: {path_str}", fontsize=14)
            start = self.start_var.get()
            end = self.end_var.get()
            distance, _ = self.campus.dijkstra(start, end)
            plt.figtext(0.5, 0.01, f"Total Distance: {distance} units", 
                       fontsize=12, ha='center')
        else:
            plt.title("CSUF Campus Map", fontsize=14)
            if self.highlighted_building:
                plt.figtext(0.5, 0.01, f"Highlighted Building: {self.highlighted_building}", 
                           fontsize=12, ha='center')
        
        plt.axis('off')
        plt.tight_layout()
        plt.show()

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCampusNavigator(root)
    root.mainloop()