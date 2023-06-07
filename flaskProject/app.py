from flask import Flask, render_template, request
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import spacy
import networkx as nx
import matplotlib.pyplot as plt

app = Flask(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def get_page_summary(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()

    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    summary = sentences[0]  # Extract the first sentence as the summary

    return summary


def create_links(results):
    graph = nx.Graph()

    for i, url in enumerate(results):
        summary = get_page_summary(url)
        graph.add_node(f"Node{i}", summary=summary)

        for j in range(i):
            if are_related(graph.nodes[f"Node{j}"]['summary'], summary):
                graph.add_edge(f"Node{j}", f"Node{i}")

    return graph


def are_related(summary1, summary2):
    # Implement your logic to determine the relationship between summaries
    # Here, we're assuming a simple condition that checks if they share a common keyword
    keywords1 = set(summary1.lower().split())
    keywords2 = set(summary2.lower().split())

    return len(keywords1.intersection(keywords2)) > 0


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        question = request.form['question']
        num_results = int(request.form['num_results'])

        results = list(search(question, num_results=num_results * 2))
        graph = create_links(results)

        # Plot the graph
        pos = nx.spring_layout(graph, seed=42)
        plt.figure(figsize=(10, 8))
        nx.draw_networkx(graph, pos, with_labels=True, node_color='lightblue', font_size=10, node_size=1200)

        # Save the plot as an image
        plot_path = "static/graph.png"
        plt.savefig(plot_path)

        return render_template('index.html', plot_path=plot_path)

    return render_template('index.html', plot_path=None)


if __name__ == '__main__':
    app.run(debug=True)