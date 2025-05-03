import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
import heapq
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

# Configure minimalist style settings
PRIMARY_COLOR = "#2979FF"  # Primary accent color
SECONDARY_COLOR = "#757575"  # Secondary color for less emphasis
BG_COLOR = "#FFFFFF"  # Clean white background
PANEL_BG = "#F5F5F5"  # Light gray panel background
TEXT_COLOR = "#212121"  # Dark text for readability
HIGHLIGHT_COLOR = "#FF5722"  # Highlight color for important elements
SUCCESS_COLOR = "#4CAF50"  # Success color
WARNING_COLOR = "#FFC107"  # Warning color
ERROR_COLOR = "#F44336"  # Error color

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


# Style configuration for ttk elements
def configure_styles():
    style = ttk.Style()
    
    # Configure the notebook style
    style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
    style.configure("TNotebook.Tab", background=PANEL_BG, foreground=TEXT_COLOR, 
                   padding=[12, 6], font=("Helvetica", 10))
    style.map("TNotebook.Tab", background=[("selected", BG_COLOR)], 
              foreground=[("selected", PRIMARY_COLOR)])
    
    # Configure frame style
    style.configure("TFrame", background=BG_COLOR)
    
    # Configure label style
    style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 10))
    
    # Configure combobox style
    style.configure("TCombobox", fieldbackground=BG_COLOR, background=BG_COLOR, 
                   foreground=TEXT_COLOR)
    style.map("TCombobox", fieldbackground=[("readonly", BG_COLOR)], 
              selectbackground=[("readonly", PRIMARY_COLOR)])
    
    # Configure buttons
    style.configure("TButton", background=PRIMARY_COLOR, foreground=BG_COLOR, 
                   borderwidth=0, font=("Helvetica", 10))
    style.map("TButton", background=[("active", PRIMARY_COLOR)], 
              foreground=[("active", BG_COLOR)])


class ModernButton(tk.Button):
    """Custom button class with modern, minimalist styling"""
    
    def __init__(self, master=None, **kwargs):
        # Default configuration
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("padx", 15)
        kwargs.setdefault("pady", 8)
        kwargs.setdefault("font", ("Helvetica", 10))
        kwargs.setdefault("cursor", "hand2")
        
        # Initialize the button
        super().__init__(master, **kwargs)
        
        # Store original background
        self.original_bg = kwargs.get("bg", kwargs.get("background", PRIMARY_COLOR))
        self.hover_bg = kwargs.get("activebackground", self.calculate_hover_color(self.original_bg))
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def calculate_hover_color(self, color):
        """Calculate a slightly darker version of the color for hover effect"""
        # Simple method - adjust brightness
        if color == PRIMARY_COLOR: return "#1565C0"  # Darker blue
        if color == HIGHLIGHT_COLOR: return "#E64A19"  # Darker orange
        if color == SUCCESS_COLOR: return "#388E3C"  # Darker green
        if color == ERROR_COLOR: return "#D32F2F"  # Darker red
        return color  # Default fallback
    
    def _on_enter(self, event):
        """Mouse enter event - darken button for hover effect"""
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        """Mouse leave event - restore button"""
        self.config(bg=self.original_bg)


class SmartCampusNavigator:
    def __init__(self, root):
        self.root = root
        self.root.title("CSUF Smart Campus Navigator")
        self.root.geometry("900x650")
        self.root.configure(bg=BG_COLOR)
        
        # Set clean theme for matplotlib
        plt.style.use('default')
        
        # Configure ttk styles
        configure_styles()
        
        # Initialize campus graph
        self.campus = CampusGraph()
        self.highlighted_building = None
        self.current_path = None
        
        # Create main title with minimalist aesthetic
        title_frame = tk.Frame(root, bg=BG_COLOR)
        title_frame.pack(fill=tk.X, pady=(20, 10))
        
        title_text = "CSUF Smart Campus Navigator"
        subtitle_text = ""
        
        title_label = tk.Label(title_frame, text=title_text, font=("Helvetica", 18, "bold"),
                              fg=PRIMARY_COLOR, bg=BG_COLOR)
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text=subtitle_text, font=("Helvetica", 12),
                                 fg=SECONDARY_COLOR, bg=BG_COLOR)
        subtitle_label.pack()
        
        # Create notebook for tabs with clean styling
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create main frames for each tab
        self.home_frame = ttk.Frame(self.notebook)
        self.search_frame = ttk.Frame(self.notebook)
        self.dijkstra_frame = ttk.Frame(self.notebook)
        
        # Add frames to notebook with clean names
        self.notebook.add(self.home_frame, text="Home")
        self.notebook.add(self.search_frame, text="Search")
        self.notebook.add(self.dijkstra_frame, text="Navigation")
        
        # Setup all tabs
        self.setup_home_tab()
        self.setup_search_tab()
        self.setup_dijkstra_tab()
        
        # Add status bar
        self.status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg=PANEL_BG, fg=SECONDARY_COLOR, font=("Helvetica", 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_home_tab(self):
        # Create and place widgets for the home tab
        content_frame = tk.Frame(self.home_frame, bg=BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        welcome_title = tk.Label(content_frame, text="Welcome to Campus Navigator", 
                               font=("Helvetica", 16, "bold"), fg=PRIMARY_COLOR, bg=BG_COLOR)
        welcome_title.pack(pady=(0, 20))
        
        welcome_text = """
        This application helps you navigate the CSUF campus efficiently.
        
        Available features:
        • Search - Find buildings on campus
        • Navigation - Calculate optimal routes between buildings
        • Map View - Visualize the campus network
        
        Select an option from the tabs above or use the Map View button below.
        """
        
        welcome = tk.Label(content_frame, text=welcome_text, 
                          font=("Helvetica", 11), fg=TEXT_COLOR, bg=BG_COLOR, justify=tk.LEFT)
        welcome.pack(pady=10)
        
        # Add map button to home tab
        button_frame = tk.Frame(content_frame, bg=BG_COLOR)
        button_frame.pack(pady=30)
        
        map_btn = ModernButton(button_frame, text="View Map", 
                             bg=PRIMARY_COLOR, fg=BG_COLOR,
                             command=lambda: self.show_map())
        map_btn.pack(side=tk.LEFT, padx=10)
        
        exit_btn = ModernButton(button_frame, text="Exit", 
                              bg=SECONDARY_COLOR, fg=BG_COLOR,
                              command=self.root.quit)
        exit_btn.pack(side=tk.LEFT, padx=10)

    def setup_search_tab(self):
        # Create and place widgets for the search tab
        content_frame = tk.Frame(self.search_frame, bg=BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(content_frame, text="Building Search", 
                        font=("Helvetica", 16, "bold"), fg=PRIMARY_COLOR, bg=BG_COLOR)
        title.pack(pady=(0, 20))
        
        instruction = tk.Label(content_frame, 
                              text="Enter building name to search:", 
                              font=("Helvetica", 12), fg=TEXT_COLOR, bg=BG_COLOR)
        instruction.pack(pady=10)
        
        # Search entry and button frame
        search_frame = tk.Frame(content_frame, bg=BG_COLOR)
        search_frame.pack(pady=10)
        
        self.search_entry = tk.Entry(search_frame, font=("Helvetica", 12), width=25,
                                   bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=PRIMARY_COLOR,
                                   relief="solid", bd=1)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = ModernButton(search_frame, text="Search", 
                                 bg=PRIMARY_COLOR, fg=BG_COLOR,
                                 command=self.search_building)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Result display with clean frame
        result_frame = tk.Frame(content_frame, bg=PANEL_BG, bd=1, relief="solid")
        result_frame.pack(pady=20, fill=tk.X)
        
        result_header = tk.Label(result_frame, text="Search Results", 
                                font=("Helvetica", 10, "bold"), fg=SECONDARY_COLOR, bg=PANEL_BG, anchor=tk.W)
        result_header.pack(fill=tk.X, padx=10, pady=5)
        
        self.search_result = tk.Label(result_frame, text="Enter a building name to search", 
                                     font=("Helvetica", 12), fg=TEXT_COLOR, bg=PANEL_BG, anchor=tk.W)
        self.search_result.pack(fill=tk.X, padx=10, pady=10)
        
        # Show on map button (initially disabled)
        button_frame = tk.Frame(content_frame, bg=BG_COLOR)
        button_frame.pack(pady=20)
        
        self.show_on_map_btn = ModernButton(button_frame, text="Show on Map", 
                                          bg=PRIMARY_COLOR, fg=BG_COLOR,
                                          state=tk.DISABLED, command=lambda: self.show_map())
        self.show_on_map_btn.pack(side=tk.LEFT, padx=10)
        
        reset_btn = ModernButton(button_frame, text="Reset", bg=SECONDARY_COLOR, fg=BG_COLOR,
                               command=lambda: self.search_result.config(
                                   text="Enter a building name to search"))
        reset_btn.pack(side=tk.LEFT, padx=10)

    def setup_dijkstra_tab(self):
        # Create and place widgets for the Navigation tab
        content_frame = tk.Frame(self.dijkstra_frame, bg=BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(content_frame, text="Campus Navigation", 
                        font=("Helvetica", 16, "bold"), fg=PRIMARY_COLOR, bg=BG_COLOR)
        title.pack(pady=(0, 20))
        
        instruction = tk.Label(content_frame, 
                              text="Select start and destination buildings:", 
                              font=("Helvetica", 12), fg=TEXT_COLOR, bg=BG_COLOR)
        instruction.pack(pady=10)
        
        # Start and end selection with clean styling
        selection_frame = tk.Frame(content_frame, bg=BG_COLOR)
        selection_frame.pack(pady=10)
        
        # Source node
        source_frame = tk.Frame(selection_frame, bg=BG_COLOR)
        source_frame.grid(row=0, column=0, padx=15, pady=10)
        
        source_label = tk.Label(source_frame, text="Start:", font=("Helvetica", 10, "bold"),
                               fg=PRIMARY_COLOR, bg=BG_COLOR)
        source_label.pack(anchor=tk.W)
        
        buildings = self.campus.get_buildings()
        self.start_var = tk.StringVar()
        
        start_combo = ttk.Combobox(source_frame, textvariable=self.start_var, 
                                  values=buildings, width=15, style="TCombobox")
        start_combo.pack(pady=5)
        
        # Destination node
        dest_frame = tk.Frame(selection_frame, bg=BG_COLOR)
        dest_frame.grid(row=0, column=1, padx=15, pady=10)
        
        dest_label = tk.Label(dest_frame, text="Destination:", font=("Helvetica", 10, "bold"),
                             fg=PRIMARY_COLOR, bg=BG_COLOR)
        dest_label.pack(anchor=tk.W)
        
        self.end_var = tk.StringVar()
        end_combo = ttk.Combobox(dest_frame, textvariable=self.end_var, 
                                values=buildings, width=15, style="TCombobox")
        end_combo.pack(pady=5)
        
        # Calculate button
        calc_btn = ModernButton(content_frame, text="Find Route", 
                               bg=PRIMARY_COLOR, fg=BG_COLOR,
                               command=self.calculate_path)
        calc_btn.pack(pady=20)
        
        # Clean output display for results
        output_frame = tk.Frame(content_frame, bg=PANEL_BG, bd=1, relief="solid")
        output_frame.pack(fill=tk.X, pady=10)
        
        output_header = tk.Label(output_frame, text="Route Information", 
                                font=("Helvetica", 10, "bold"), fg=SECONDARY_COLOR, bg=PANEL_BG, anchor=tk.W)
        output_header.pack(fill=tk.X, padx=10, pady=5)
        
        self.path_result = tk.Label(output_frame, text="Select start and destination buildings", 
                                   font=("Helvetica", 12), fg=TEXT_COLOR, bg=PANEL_BG, anchor=tk.W)
        self.path_result.pack(fill=tk.X, padx=10, pady=5)
        
        self.path_details = tk.Label(output_frame, text="", 
                                    font=("Helvetica", 11), fg=SECONDARY_COLOR, bg=PANEL_BG, anchor=tk.W)
        self.path_details.pack(fill=tk.X, padx=10, pady=5)
        
        # Show on map button
        button_frame = tk.Frame(content_frame, bg=BG_COLOR)
        button_frame.pack(pady=20)
        
        self.show_path_btn = ModernButton(button_frame, text="View Route on Map", 
                                        bg=PRIMARY_COLOR, fg=BG_COLOR,
                                        state=tk.DISABLED, command=lambda: self.show_map(True))
        self.show_path_btn.pack(side=tk.LEFT, padx=10)
        
        reset_btn = ModernButton(button_frame, text="Reset", bg=SECONDARY_COLOR, fg=BG_COLOR,
                               command=self.reset_path_calc)
        reset_btn.pack(side=tk.LEFT, padx=10)

    def reset_path_calc(self):
        """Reset the path calculation fields"""
        self.start_var.set("")
        self.end_var.set("")
        self.path_result.config(text="Select start and destination buildings")
        self.path_details.config(text="")
        self.show_path_btn.config(state=tk.DISABLED)
        self.current_path = None
        self.status_bar.config(text="Navigation reset")

    def search_building(self):
        building = self.search_entry.get()
        if not building:
            self.search_result.config(text="Please enter a building name", fg=ERROR_COLOR)
            self.status_bar.config(text="Search failed: Empty query")
            return
            
        found = False
        found_building = None
        
        for b in self.campus.get_buildings():
            if kmp_search(b.lower(), building.lower()) != -1:
                found = True
                found_building = b
                break
                
        if found:
            self.highlighted_building = found_building
            self.search_result.config(text=f"Building '{found_building}' found", fg=SUCCESS_COLOR)
            self.show_on_map_btn.config(state=tk.NORMAL)
            self.status_bar.config(text=f"Building found: {found_building}")
        else:
            self.search_result.config(text=f"Building '{building}' not found", fg=ERROR_COLOR)
            self.show_on_map_btn.config(state=tk.DISABLED)
            self.status_bar.config(text=f"Search failed: {building} not found")

    def calculate_path(self):
        start = self.start_var.get()
        end = self.end_var.get()
        
        if not start or not end:
            self.path_result.config(text="Please select both start and destination", fg=ERROR_COLOR)
            self.status_bar.config(text="Route calculation failed: Missing locations")
            return
            
        if start == end:
            self.path_result.config(text="Start and destination are the same", fg=WARNING_COLOR)
            self.path_details.config(text="No route needed")
            self.show_path_btn.config(state=tk.DISABLED)
            self.current_path = None
            self.status_bar.config(text="Route calculation: Same location selected")
            return
            
        distance, path = self.campus.dijkstra(start, end)
        self.path_result.config(
            text=f"Route found: {distance} distance units", 
            fg=SUCCESS_COLOR
        )
        
        path_str = " → ".join(path)
        self.path_details.config(text=f"Path: {path_str}")
        
        self.current_path = path
        self.show_path_btn.config(state=tk.NORMAL)
        self.status_bar.config(text=f"Route calculated: {start} to {end}")

    def show_map(self, show_path=False):
        # Set up a matplotlib figure with clean theme
        fig, ax = plt.subplots(figsize=(10, 8), facecolor=BG_COLOR)
        ax.set_facecolor(BG_COLOR)
        
        # Custom positioning for better visual
        pos = nx.spring_layout(self.campus.graph, seed=42, k=0.9)
        
        # Draw all edges in light gray
        nx.draw_networkx_edges(self.campus.graph, pos, width=1.0, alpha=0.6, 
                              edge_color=SECONDARY_COLOR, ax=ax)
        
        # Draw path edges with highlight color if showing path
        if show_path and self.current_path and len(self.current_path) > 1:
            path_edges = [(self.current_path[i], self.current_path[i+1]) 
                          for i in range(len(self.current_path)-1)]
            
            # Draw path edge
            nx.draw_networkx_edges(self.campus.graph, pos, edgelist=path_edges, 
                                  width=2.5, alpha=1.0, edge_color=PRIMARY_COLOR, 
                                  arrows=True, arrowstyle='->', arrowsize=15, ax=ax)
        
        # Color nodes appropriately with minimalist theme
        node_colors = []
        node_sizes = []
        
        for node in self.campus.graph.nodes:
            if show_path and self.current_path:
                if node == self.current_path[0]:  # Starting node
                    node_colors.append(PRIMARY_COLOR)
                    node_sizes.append(700)
                elif node == self.current_path[-1]:  # Ending node
                    node_colors.append(HIGHLIGHT_COLOR)
                    node_sizes.append(700)
                elif node in self.current_path:  # Path nodes
                    node_colors.append(SUCCESS_COLOR)
                    node_sizes.append(600)
                else:  # Other nodes
                    node_colors.append(SECONDARY_COLOR)
                    node_sizes.append(400)
            else:
                if node == self.highlighted_building:
                    node_colors.append(HIGHLIGHT_COLOR)
                    node_sizes.append(700)
                else:
                    node_colors.append(SECONDARY_COLOR)
                    node_sizes.append(500)
        
        # Draw nodes with clean styling
        nx.draw_networkx_nodes(self.campus.graph, pos, node_color=node_colors, 
                              node_size=node_sizes, edgecolors='white', 
                              linewidths=1, ax=ax)
        
        # Draw node labels with clean font
        nx.draw_networkx_labels(self.campus.graph, pos, font_size=10, 
                              font_color='white', font_weight='bold', 
                              font_family='sans-serif', ax=ax)
        
        # Draw edge weights with clean styling
        edge_labels = nx.get_edge_attributes(self.campus.graph, 'weight')
        nx.draw_networkx_edge_labels(self.campus.graph, pos, edge_labels=edge_labels, 
                                    font_size=8, font_color=TEXT_COLOR, 
                                    font_family='sans-serif', ax=ax)
        
        # Add a title based on what's being shown
        if show_path and self.current_path:
            path_str = " → ".join(self.current_path)
            ax.set_title(f"Route: {path_str}", fontsize=14, 
                       color=PRIMARY_COLOR, fontweight='bold', fontfamily='sans-serif')
            
            start = self.start_var.get()
            end = self.end_var.get()
            distance, _ = self.campus.dijkstra(start, end)
            fig.text(0.5, 0.01, f"Total Distance: {distance} units", 
                    fontsize=12, color=SECONDARY_COLOR, ha='center', fontfamily='sans-serif')
        else:
            ax.set_title("CSUF Campus Map", fontsize=14, 
                       color=PRIMARY_COLOR, fontweight='bold', fontfamily='sans-serif')
            if self.highlighted_building:
                fig.text(0.5, 0.01, f"Highlighted Building: {self.highlighted_building}", 
                        fontsize=12, color=SECONDARY_COLOR, ha='center', fontfamily='sans-serif')
        
        # Update status bar
        if show_path and self.current_path:
            self.status_bar.config(text=f"Showing route: {self.current_path[0]} to {self.current_path[-1]}")
        elif self.highlighted_building:
            self.status_bar.config(text=f"Showing building: {self.highlighted_building}")
        else:
            self.status_bar.config(text="Showing campus map")
        
        plt.axis('off')
        plt.tight_layout()
        plt.show()

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCampusNavigator(root)
    root.mainloop()