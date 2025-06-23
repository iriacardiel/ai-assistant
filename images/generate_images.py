import matplotlib.pyplot as plt
from termcolor import colored
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for headless environments

def plot_battlefield(observation: dict):
    entities = observation["data"]
    plt.figure(figsize=(6, 6))
    plt.xlim(0, 9)
    plt.ylim(0, 9)
    plt.grid(True)
    plt.xticks(range(10))
    plt.yticks(range(10))

    for ent in entities:
        x = ent["coordinates"]["x"]
        y = ent["coordinates"]["y"]
        
        if ent['category'] == 'ally':
            color = 'blue'
            marker = 'o'
        else:
            color = 'red'
            marker = 'o' if ent['status'] == 'not destroyed' else 'x'
        
        plt.scatter(x, y, c=color, marker=marker, s=100, label=ent["name"])
        plt.text(x + 0.2, y + 0.2, ent["name"], fontsize=9)

    plt.title("Battlefield (10x10)")
    plt.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    
    """# Pop map
    print(colored("Opening battlefield map window...", "cyan"))
    plt.show()"""
    
    # Saving to file
    filename = f"images/map_{observation['timestamp'].replace(':', '').replace(' ', '_')}.png"
    plt.savefig(filename)
    plt.close()
    print(colored(f"Map saved to {filename}", "cyan"))
    
def draw_mermaid(graph):
    mermaid_code = graph.get_graph(xray=1).draw_mermaid()
    with open("images/graph.mmd", "w") as f:
        f.write(mermaid_code)
    
    
