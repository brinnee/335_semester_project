import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
import heapq
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl

# Configure cyberpunk style settings
DARK_BG = "#121212"  # Nearly black background
PANEL_BG = "#1E1E1E"  # Dark panel background
NEON_BLUE = "#00FFFF"  # Cyan neon blue
NEON_PINK = "#FF00FF"  # Magenta neon pink
NEON_GREEN = "#39FF14"  # Electric green
NEON_ORANGE = "#FF9500"  # Neon orange
NEON_PURPLE = "#BD00FF"  # Neon purple
TEXT_COLOR = "#FFFFFF"  # White text
SECONDARY_TEXT = "#AAAAAA"  # Light gray 

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
    style.configure("TNotebook", background=DARK_BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=PANEL_BG, foreground=TEXT_COLOR, 
                   padding=[10, 5], font=("Consolas", 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", DARK_BG)], 
              foreground=[("selected", NEON_BLUE)])
    
    # Configure frame style
    style.configure("TFrame", background=DARK_BG)
    
    # Configure label style
    style.configure("TLabel", background=DARK_BG, foreground=TEXT_COLOR, font=("Consolas", 10))
    
    # Configure combobox style
    style.configure("TCombobox", fieldbackground=PANEL_BG, background=PANEL_BG, 
                   foreground=TEXT_COLOR, arrowcolor=NEON_GREEN)
    style.map("TCombobox", fieldbackground=[("readonly", PANEL_BG)], 
              selectbackground=[("readonly", NEON_BLUE)])


class NeonButton(tk.Button):
    """Custom button class with neon glow effect"""
    
    def __init__(self, master=None, **kwargs):
        # Default configuration
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("padx", 15)
        kwargs.setdefault("pady", 8)
        kwargs.setdefault("font", ("Consolas", 10, "bold"))
        kwargs.setdefault("cursor", "hand2")
        
        # Initialize the button
        super().__init__(master, **kwargs)
        
        # Store original background
        self.original_bg = kwargs.get("bg", kwargs.get("background", PANEL_BG))
        self.hover_bg = kwargs.get("activebackground", self.calculate_hover_color(self.original_bg))
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def calculate_hover_color(self, color):
        """Calculate a brighter version of the color for hover effect"""
        # Simple method - can be improved with proper color manipulation
        if color == NEON_BLUE: return "#80FFFF"
        if color == NEON_PINK: return "#FF80FF"
        if color == NEON_GREEN: return "#80FF80"
        if color == NEON_ORANGE: return "#FFAA40"
        if color == NEON_PURPLE: return "#D580FF"
        return color  # Default fallback
    
    def _on_enter(self, event):
        """Mouse enter event - brighten button"""
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        """Mouse leave event - restore button"""
        self.config(bg=self.original_bg)


class SmartCampusNavigator:
    def __init__(self, root):
        self.root = root
        self.root.title("CSUF Smart Campus Navigator // CYBERPUNK EDITION")
        self.root.geometry("900x650")
        self.root.configure(bg=DARK_BG)
        
        # Set dark theme for matplotlib
        plt.style.use('dark_background')
        
        # Configure ttk styles
        configure_styles()
        
        # Initialize campus graph
        self.campus = CampusGraph()
        self.highlighted_building = None
        self.current_path = None
        
        # Create main title with cyberpunk aesthetic
        title_frame = tk.Frame(root, bg=DARK_BG)
        title_frame.pack(fill=tk.X, pady=(20, 10))
        
        title_text = "CSUF SMART CAMPUS NAVIGATOR"
        subtitle_text = "// CYBERPUNK EDITION 2.0"
        
        title_label = tk.Label(title_frame, text=title_text, font=("Consolas", 18, "bold"),
                              fg=NEON_BLUE, bg=DARK_BG)
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text=subtitle_text, font=("Consolas", 12),
                                 fg=NEON_PINK, bg=DARK_BG)
        subtitle_label.pack()
        
        # Create notebook for tabs with dark styling
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create main frames for each tab
        self.home_frame = ttk.Frame(self.notebook)
        self.search_frame = ttk.Frame(self.notebook)
        self.dijkstra_frame = ttk.Frame(self.notebook)
        
        # Add frames to notebook with cyberpunk names
        self.notebook.add(self.home_frame, text="HOME_SYS")
        self.notebook.add(self.search_frame, text="FIND_NODE")
        self.notebook.add(self.dijkstra_frame, text="PATH_CALC")
        
        # Setup all tabs
        self.setup_home_tab()
        self.setup_search_tab()
        self.setup_dijkstra_tab()
        
        # Add status bar
        self.status_bar = tk.Label(root, text="SYSTEM READY", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg=PANEL_BG, fg=NEON_GREEN, font=("Consolas", 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_home_tab(self):
        # Create and place widgets for the home tab
        content_frame = tk.Frame(self.home_frame, bg=DARK_BG)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        welcome_title = tk.Label(content_frame, text="[ WELCOME TO THE GRID ]", 
                               font=("Consolas", 16, "bold"), fg=NEON_ORANGE, bg=DARK_BG)
        welcome_title.pack(pady=(0, 20))
        
        welcome_text = """
        >>> CAMPUS NAVIGATION SYSTEM ONLINE <<<
        
        SELECT MODULE:
        • FIND_NODE - Search for buildings in the campus network
        • PATH_CALC - Calculate optimal routes between nodes
        • MAP_VIEW - Visualize the entire campus network
        
        [ SYSTEM V2.0 - POWERED BY NETRUNNER OS ]
        """
        
        welcome = tk.Label(content_frame, text=welcome_text, 
                          font=("Consolas", 11), fg=TEXT_COLOR, bg=DARK_BG, justify=tk.LEFT)
        welcome.pack(pady=10)
        
        # Add map button to home tab
        button_frame = tk.Frame(content_frame, bg=DARK_BG)
        button_frame.pack(pady=30)
        
        map_btn = NeonButton(button_frame, text="LAUNCH MAP_VIEW", 
                           bg=NEON_BLUE, fg=TEXT_COLOR,
                           command=lambda: self.show_map())
        map_btn.pack(side=tk.LEFT, padx=10)
        
        exit_btn = NeonButton(button_frame, text="EXIT", 
                            bg=NEON_PINK, fg=TEXT_COLOR,
                            command=self.root.quit)
        exit_btn.pack(side=tk.LEFT, padx=10)

    def setup_search_tab(self):
        # Create and place widgets for the search tab
        content_frame = tk.Frame(self.search_frame, bg=DARK_BG)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(content_frame, text="// NODE SEARCH PROTOCOL", 
                        font=("Consolas", 16, "bold"), fg=NEON_GREEN, bg=DARK_BG)
        title.pack(pady=(0, 20))
        
        instruction = tk.Label(content_frame, 
                              text="INPUT TARGET NODE IDENTIFIER:", 
                              font=("Consolas", 12), fg=TEXT_COLOR, bg=DARK_BG)
        instruction.pack(pady=10)
        
        # Search entry and button frame
        search_frame = tk.Frame(content_frame, bg=DARK_BG)
        search_frame.pack(pady=10)
        
        self.search_entry = tk.Entry(search_frame, font=("Consolas", 12), width=25,
                                   bg=PANEL_BG, fg=NEON_BLUE, insertbackground=NEON_BLUE)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = NeonButton(search_frame, text="SCAN", 
                               bg=NEON_GREEN, fg=TEXT_COLOR,
                               command=self.search_building)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Result display with terminal-like frame
        result_frame = tk.Frame(content_frame, bg=PANEL_BG, bd=1, relief="solid")
        result_frame.pack(pady=20, fill=tk.X)
        
        result_header = tk.Label(result_frame, text="// SCAN RESULTS", 
                                font=("Consolas", 10), fg=NEON_PURPLE, bg=PANEL_BG, anchor=tk.W)
        result_header.pack(fill=tk.X, padx=10, pady=5)
        
        self.search_result = tk.Label(result_frame, text="> AWAITING SEARCH QUERY...", 
                                     font=("Consolas", 12), fg=NEON_BLUE, bg=PANEL_BG, anchor=tk.W)
        self.search_result.pack(fill=tk.X, padx=10, pady=10)
        
        # Show on map button (initially disabled)
        button_frame = tk.Frame(content_frame, bg=DARK_BG)
        button_frame.pack(pady=20)
        
        self.show_on_map_btn = NeonButton(button_frame, text="VISUALIZE NODE", 
                                       bg=NEON_BLUE, fg=TEXT_COLOR,
                                       state=tk.DISABLED, command=lambda: self.show_map())
        self.show_on_map_btn.pack(side=tk.LEFT, padx=10)
        
        reset_btn = NeonButton(button_frame, text="RESET", bg=NEON_PINK, fg=TEXT_COLOR,
                             command=lambda: self.search_result.config(
                                 text="> AWAITING SEARCH QUERY..."))
        reset_btn.pack(side=tk.LEFT, padx=10)

    def setup_dijkstra_tab(self):
        # Create and place widgets for the Dijkstra tab
        content_frame = tk.Frame(self.dijkstra_frame, bg=DARK_BG)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(content_frame, text="// OPTIMAL PATH CALCULATOR", 
                        font=("Consolas", 16, "bold"), fg=NEON_ORANGE, bg=DARK_BG)
        title.pack(pady=(0, 20))
        
        instruction = tk.Label(content_frame, 
                              text="SELECT SOURCE AND DESTINATION NODES:", 
                              font=("Consolas", 12), fg=TEXT_COLOR, bg=DARK_BG)
        instruction.pack(pady=10)
        
        # Start and end selection with cyberpunk styling
        selection_frame = tk.Frame(content_frame, bg=DARK_BG)
        selection_frame.pack(pady=10)
        
        # Source node
        source_frame = tk.Frame(selection_frame, bg=DARK_BG)
        source_frame.grid(row=0, column=0, padx=15, pady=10)
        
        source_label = tk.Label(source_frame, text="SOURCE:", font=("Consolas", 10),
                               fg=NEON_BLUE, bg=DARK_BG)
        source_label.pack(anchor=tk.W)
        
        buildings = self.campus.get_buildings()
        self.start_var = tk.StringVar()
        
        start_combo = ttk.Combobox(source_frame, textvariable=self.start_var, 
                                  values=buildings, width=15, style="TCombobox")
        start_combo.pack(pady=5)
        
        # Destination node
        dest_frame = tk.Frame(selection_frame, bg=DARK_BG)
        dest_frame.grid(row=0, column=1, padx=15, pady=10)
        
        dest_label = tk.Label(dest_frame, text="DESTINATION:", font=("Consolas", 10),
                             fg=NEON_PINK, bg=DARK_BG)
        dest_label.pack(anchor=tk.W)
        
        self.end_var = tk.StringVar()
        end_combo = ttk.Combobox(dest_frame, textvariable=self.end_var, 
                                values=buildings, width=15, style="TCombobox")
        end_combo.pack(pady=5)
        
        # Calculate button
        calc_btn = NeonButton(content_frame, text="CALCULATE OPTIMAL PATH", 
                             bg=NEON_ORANGE, fg=TEXT_COLOR,
                             command=self.calculate_path)
        calc_btn.pack(pady=20)
        
        # Terminal-like output display for results
        output_frame = tk.Frame(content_frame, bg=PANEL_BG, bd=1, relief="solid")
        output_frame.pack(fill=tk.X, pady=10)
        
        output_header = tk.Label(output_frame, text="// PATH CALCULATION RESULTS", 
                                font=("Consolas", 10), fg=NEON_PURPLE, bg=PANEL_BG, anchor=tk.W)
        output_header.pack(fill=tk.X, padx=10, pady=5)
        
        self.path_result = tk.Label(output_frame, text="> AWAITING NODE SELECTION...", 
                                   font=("Consolas", 12), fg=NEON_GREEN, bg=PANEL_BG, anchor=tk.W)
        self.path_result.pack(fill=tk.X, padx=10, pady=5)
        
        self.path_details = tk.Label(output_frame, text="", 
                                    font=("Consolas", 11), fg=TEXT_COLOR, bg=PANEL_BG, anchor=tk.W)
        self.path_details.pack(fill=tk.X, padx=10, pady=5)
        
        # Show on map button
        button_frame = tk.Frame(content_frame, bg=DARK_BG)
        button_frame.pack(pady=20)
        
        self.show_path_btn = NeonButton(button_frame, text="VISUALIZE PATH", 
                                      bg=NEON_BLUE, fg=TEXT_COLOR,
                                      state=tk.DISABLED, command=lambda: self.show_map(True))
        self.show_path_btn.pack(side=tk.LEFT, padx=10)
        
        reset_btn = NeonButton(button_frame, text="RESET", bg=NEON_PINK, fg=TEXT_COLOR,
                             command=self.reset_path_calc)
        reset_btn.pack(side=tk.LEFT, padx=10)

    def reset_path_calc(self):
        """Reset the path calculation fields"""
        self.start_var.set("")
        self.end_var.set("")
        self.path_result.config(text="> AWAITING NODE SELECTION...")
        self.path_details.config(text="")
        self.show_path_btn.config(state=tk.DISABLED)
        self.current_path = None
        self.status_bar.config(text="PATH CALCULATION RESET")

    def search_building(self):
        building = self.search_entry.get()
        if not building:
            self.search_result.config(text="> ERROR: EMPTY SEARCH QUERY", fg=NEON_PINK)
            self.status_bar.config(text="SEARCH FAILED: EMPTY QUERY")
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
            self.search_result.config(text=f"> TARGET NODE [{found_building}] LOCATED", fg=NEON_GREEN)
            self.show_on_map_btn.config(state=tk.NORMAL)
            self.status_bar.config(text=f"NODE FOUND: {found_building}")
        else:
            self.search_result.config(text=f"> ERROR: NODE [{building}] NOT FOUND IN DATABASE", fg=NEON_PINK)
            self.show_on_map_btn.config(state=tk.DISABLED)
            self.status_bar.config(text=f"SEARCH FAILED: {building} NOT FOUND")

    def calculate_path(self):
        start = self.start_var.get()
        end = self.end_var.get()
        
        if not start or not end:
            self.path_result.config(text="> ERROR: SOURCE OR DESTINATION NODE NOT SPECIFIED", fg=NEON_PINK)
            self.status_bar.config(text="PATH CALCULATION FAILED: MISSING NODES")
            return
            
        if start == end:
            self.path_result.config(text="> ALERT: SOURCE AND DESTINATION NODES ARE IDENTICAL", fg=NEON_ORANGE)
            self.path_details.config(text="> No path calculation necessary.")
            self.show_path_btn.config(state=tk.DISABLED)
            self.current_path = None
            self.status_bar.config(text="PATH CALCULATION: IDENTICAL NODES")
            return
            
        distance, path = self.campus.dijkstra(start, end)
        self.path_result.config(
            text=f"> OPTIMAL PATH FOUND: DISTANCE = {distance} UNITS", 
            fg=NEON_GREEN
        )
        
        path_str = " → ".join(path)
        self.path_details.config(text=f"> PATH: {path_str}")
        
        self.current_path = path
        self.show_path_btn.config(state=tk.NORMAL)
        self.status_bar.config(text=f"PATH CALCULATED: {start} TO {end}")

    def show_map(self, show_path=False):
        # Set up a custom matplotlib figure with dark theme
        fig, ax = plt.subplots(figsize=(10, 8), facecolor=DARK_BG)
        ax.set_facecolor(DARK_BG)
        
        # Custom positioning for better visual
        pos = nx.spring_layout(self.campus.graph, seed=42, k=0.9)
        
        # Create a custom colormap for edges
        edge_cmap = LinearSegmentedColormap.from_list(
            "edge_cmap", ["#333333", NEON_BLUE], N=100)
        
        # Draw all edges in dark gray
        nx.draw_networkx_edges(self.campus.graph, pos, width=1.0, alpha=0.4, 
                              edge_color='#333333', ax=ax)
        
        # Draw path edges with neon effect if showing path
        if show_path and self.current_path and len(self.current_path) > 1:
            path_edges = [(self.current_path[i], self.current_path[i+1]) 
                          for i in range(len(self.current_path)-1)]
            
            # Draw glow effect (larger, more transparent edge)
            nx.draw_networkx_edges(self.campus.graph, pos, edgelist=path_edges, 
                                  width=8.0, alpha=0.3, edge_color=NEON_GREEN, 
                                  arrows=False, ax=ax)
            
            # Draw main edge
            nx.draw_networkx_edges(self.campus.graph, pos, edgelist=path_edges, 
                                  width=2.5, alpha=1.0, edge_color=NEON_GREEN, 
                                  arrows=True, arrowstyle='->', arrowsize=20, ax=ax)
        
        # Color nodes appropriately with cyberpunk theme
        node_colors = []
        node_sizes = []
        
        for node in self.campus.graph.nodes:
            if show_path and self.current_path:
                if node == self.current_path[0]:  # Starting node
                    node_colors.append(NEON_BLUE)
                    node_sizes.append(800)
                elif node == self.current_path[-1]:  # Ending node
                    node_colors.append(NEON_PINK)
                    node_sizes.append(800)
                elif node in self.current_path:  # Path nodes
                    node_colors.append(NEON_GREEN)
                    node_sizes.append(600)
                else:  # Other nodes
                    node_colors.append('#444444')
                    node_sizes.append(400)
            else:
                if node == self.highlighted_building:
                    node_colors.append(NEON_ORANGE)
                    node_sizes.append(800)
                else:
                    node_colors.append('#666666')
                    node_sizes.append(500)
        
        # Draw nodes with glow effect
        # First draw larger, more transparent nodes for glow
        nx.draw_networkx_nodes(self.campus.graph, pos, node_color=node_colors, 
                              node_size=[s * 1.5 for s in node_sizes], alpha=0.3, 
                              edgecolors='none', ax=ax)
        
        # Then draw actual nodes
        nx.draw_networkx_nodes(self.campus.graph, pos, node_color=node_colors, 
                              node_size=node_sizes, edgecolors='white', 
                              linewidths=1, ax=ax)
        
        # Draw node labels with cyberpunk font
        nx.draw_networkx_labels(self.campus.graph, pos, font_size=10, 
                              font_color='white', font_weight='bold', 
                              font_family='monospace', ax=ax)
        
        # Draw edge weights with neon color
        edge_labels = nx.get_edge_attributes(self.campus.graph, 'weight')
        nx.draw_networkx_edge_labels(self.campus.graph, pos, edge_labels=edge_labels, 
                                    font_size=8, font_color=NEON_BLUE, 
                                    font_family='monospace', ax=ax)
        
        # Add a title based on what's being shown
        if show_path and self.current_path:
            path_str = " → ".join(self.current_path)
            ax.set_title(f"OPTIMAL PATH: {path_str}", fontsize=14, 
                        color=NEON_GREEN, fontweight='bold', fontfamily='monospace')
            
            start = self.start_var.get()
            end = self.end_var.get()
            distance, _ = self.campus.dijkstra(start, end)
            fig.text(0.5, 0.01, f"TOTAL DISTANCE: {distance} UNITS", 
                    fontsize=12, color=NEON_BLUE, ha='center', fontfamily='monospace')
        else:
            ax.set_title("CSUF CAMPUS NETWORK MAP", fontsize=14, 
                        color=NEON_ORANGE, fontweight='bold', fontfamily='monospace')
            if self.highlighted_building:
                fig.text(0.5, 0.01, f"HIGHLIGHTED NODE: {self.highlighted_building}", 
                        fontsize=12, color=NEON_BLUE, ha='center', fontfamily='monospace')
        
        # Add grid lines for cyberpunk effect
        ax.grid(True, linestyle='--', alpha=0.1, color=NEON_BLUE)
        
        # Update status bar
        if show_path and self.current_path:
            self.status_bar.config(text=f"DISPLAYING PATH: {self.current_path[0]} TO {self.current_path[-1]}")
        elif self.highlighted_building:
            self.status_bar.config(text=f"DISPLAYING NODE: {self.highlighted_building}")
        else:
            self.status_bar.config(text="DISPLAYING CAMPUS NETWORK MAP")
        
        plt.axis('off')
        plt.tight_layout()
        plt.show()

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCampusNavigator(root)
    root.mainloop()