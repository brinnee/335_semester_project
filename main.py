import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt

# Use Dijkstra’s algorithm to find the shortest path between campus buildings.

# Use Activity Selection (Greedy) to optimize a student’s daily task schedule.

# KMP Search
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

# GUI
class SmartCampusNavigator:
    def __init__(self, root):
        self.root = root
        self.root.title("CSUF Smart Campus Navigator")
        self.root.geometry("400x350")
        self.root.configure(bg="#F5F5F5")

        self.graph = nx.Graph()
        self.build_graph()
        self.highlighted_building = None

        title = tk.Label(root, text="CSUF Smart Campus Navigator", font=("Helvetica", 16, "bold"), fg="#FF6600", bg="#F5F5F5")
        title.pack(pady=20)

        search_btn = tk.Button(root, text="What building are you looking for?", font=("Helvetica", 12), bg="#FFCC99", fg="black", relief="raised", bd=3, command=self.search_building_name)
        search_btn.pack(pady=10, ipadx=10, ipady=5)

        map_btn = tk.Button(root, text="Show CSUF Campus Map", font=("Helvetica", 12), bg="#FFCC99", fg="black", relief="raised", bd=3, command=self.show_map)
        map_btn.pack(pady=10, ipadx=10, ipady=5)

        restart_btn = tk.Button(root, text="Restart", font=("Helvetica", 12), bg="#FF9999", fg="black", relief="raised", bd=3, command=self.restart)
        restart_btn.pack(pady=10, ipadx=10, ipady=5)

        search_btn.bind("<Enter>", lambda e: search_btn.config(bg="#FFA64D"))
        search_btn.bind("<Leave>", lambda e: search_btn.config(bg="#FFCC99"))

        map_btn.bind("<Enter>", lambda e: map_btn.config(bg="#FFA64D"))
        map_btn.bind("<Leave>", lambda e: map_btn.config(bg="#FFCC99"))

        restart_btn.bind("<Enter>", lambda e: restart_btn.config(bg="#FF6666"))
        restart_btn.bind("<Leave>", lambda e: restart_btn.config(bg="#FF9999"))

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

    def search_building_name(self):
        popup = tk.Toplevel(self.root)
        popup.title("Search Building")
        popup.geometry("350x150")
        popup.configure(bg="#FFF0E0")
        popup.grab_set()

        label = tk.Label(popup, text="Enter the name of the building to search:", font=("Helvetica", 12), bg="#FFF0E0")
        label.pack(pady=10)

        entry = tk.Entry(popup, font=("Helvetica", 12), width=25)
        entry.pack(pady=5)

        def on_search():
            building = entry.get()
            found = False
            for b in self.graph.nodes:
                if kmp_search(b.lower(), building.lower()) != -1:
                    self.highlighted_building = b
                    popup.destroy()
                    self.show_found_popup(b)
                    found = True
                    break
            if not found:
                self.show_fancy_popup(f"{building} is not found.", f"{building} is not found.", success=False)
                popup.destroy()

        search_btn = tk.Button(popup, text="Search", font=("Helvetica", 12), bg="#FFA64D", fg="white", command=on_search)
        search_btn.pack(pady=10)

        entry.focus()

    def show_found_popup(self, building):
        fancy = tk.Toplevel(self.root)
        fancy.title("Found 🎉")
        fancy.geometry("350x220")
        fancy.configure(bg="#E0FFE0")
        fancy.grab_set()

        label = tk.Label(fancy, text=f"{building} was found!", font=("Helvetica", 14, "bold"), bg="#E0FFE0", fg="#008000")
        label.pack(pady=20)

        show_btn = tk.Button(fancy, text="Show on Map", font=("Helvetica", 12), bg="#FFA64D", fg="white", width=12, command=lambda: [fancy.destroy(), self.show_map()])
        show_btn.pack(pady=5)

        ok_btn = tk.Button(fancy, text="Exit", font=("Helvetica", 12), bg="#FFA64D", fg="white", width=12, command=fancy.destroy)
        ok_btn.pack(pady=5)

    def show_fancy_popup(self, message, title, success=True):
        fancy = tk.Toplevel(self.root)
        fancy.title(title)
        fancy.geometry("350x180")
        fancy.configure(bg="#E0FFE0" if success else "#FFE0E0")
        fancy.grab_set()

        label = tk.Label(fancy, text=message, font=("Helvetica", 14, "bold"), bg=fancy["bg"], fg="#008000" if success else "#B22222")
        label.pack(pady=20)

        ok_btn = tk.Button(fancy, text="Exit", font=("Helvetica", 12), bg="#FFA64D", fg="white", width=10, command=fancy.destroy)
        ok_btn.pack(pady=10)

    def show_map(self):
        pos = nx.spring_layout(self.graph, seed=42, k=0.9)

        node_colors = []
        for node in self.graph.nodes:
            if node == self.highlighted_building:
                node_colors.append('red')
            else:
                node_colors.append('pink')

        nx.draw(self.graph, pos, with_labels=True, node_color=node_colors, node_size=3000, font_size=10, font_weight='bold', edgecolors='black')

        labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels)

        plt.title("CSUF Campus Map")
        plt.show()

    def restart(self):
        self.highlighted_building = None
        self.show_map()

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCampusNavigator(root)
    root.mainloop()
