import xml.etree.ElementTree as ET

class DrawIO:
    def __init__(self, drawio_file):
        # Generate the XML data and save as draw.io
        self.drawio_file = '../../Parsed_Data/'  + self.filename[:-4] + 'GR7.drawio'
        self.active_iofile = open(self.drawio_file, 'wb')
        self.active_iofile.write(self.drawio_xml_data)

    def create_drawio_xml_old(self, steps, transitions):
        """ This function will generate the xml data with step 7 steps and transitions information

        :param steps:
        :param transitions:
        :return: xml_data
        """
        # Create an XML structure compatible with draw.io
        root = ET.Element("mxGraphModel")
        diagram = ET.SubElement(root, "root")

        # Create default parent
        default_parent = ET.SubElement(diagram, "mxCell", {
            'id': '0'
        })
        layer = ET.SubElement(diagram, "mxCell", {
            'id': '1',
            'parent': '0'
        })

        # Add each step as a draw.io node
        for idx, step in enumerate(steps):
            shape = ET.SubElement(diagram, "mxCell", {
                'id': str(idx + 2),
                'value': f'{step["name"]} - {step["comment"]}',
                'style': 'rounded=1;whiteSpace=wrap;html=1;',  # Process block style
                'vertex': '1',
                'parent': '1'
            })
            geo = ET.SubElement(shape, "mxGeometry", {
                'x': str(40 * idx),  # Spacing out the nodes for simplicity
                'y': str(40 * idx),
                'width': '120',
                'height': '60',
                'as': 'geometry'
            })

        # Convert the XML tree to a string and return
        return ET.tostring(root, encoding='utf-8', method='xml')

    def create_drawio_xml(self, steps, transitions):
        """Converts step and transition data to draw.io XML format."""

        # Initial XML template for draw.io
        xml_template = '<mxGraphModel><root><mxCell id="0" /><mxCell id="1" parent="0" />'

        # Template for creating a step (node)
        node_template = '<mxCell id="{id}" value="{name}" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" \
                         parent="1"><mxGeometry x="{x}" y="{y}" width="80" height="40" as="geometry" /></mxCell>'

        # Template for creating a transition (edge)
        edge_template = '<mxCell id="e{id}" value="{condition}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;\
                         orthogonalLoop=1;" edge="1" parent="1" source="{from_id}" target="{to_id}">\
                         <mxGeometry relative="1" as="geometry" /></mxCell>'

        # Starting positions for layout (modify these values for layout adjustments)
        current_x = 100
        current_y = 100
        spacing_x = 200  # Horizontal space between steps
        spacing_y = 150  # Vertical space between steps

        # Create nodes for steps
        nodes = {}
        edges = []
        node_id = 2
        for step in steps:
            step_name = step['number']
            if step_name not in nodes:
                # Add the step node (using current_x and current_y for positioning)
                nodes[step_name] = {"id": node_id, "x": current_x, "y": current_y}
                xml_template += node_template.format(id=node_id, name=step_name, x=current_x, y=current_y)
                node_id += 1
                current_y += spacing_y  # Move down for the next step

                # Reset x for steps in a new column
                if current_y > 500:
                    current_y = 100
                    current_x += spacing_x

        # Create edges for transitions
        for transition in transitions:
            from_state = transition['from']
            to_states = transition['to']
            condition = transition['condition']

            # for to_state in to_states:
            #     from_id = nodes[from_state]['number']
            #     to_id = nodes[to_state]['number']
            #     edges.append(edge_template.format(id=node_id, condition=condition, from_id=from_id, to_id=to_id))
            #     node_id += 1

        # Append the edges (transitions) to the XML template
        # for edge in edges:
        #     xml_template += edge

        # Close the XML
        xml_template += '''        </root>
        </mxGraphModel>'''

        return xml_template

    def test_graph_diagram(self, steps, transitions):
        import networkx as nx
        import matplotlib.pyplot as plt

        # Create a graph with NetworkX
        G = nx.Graph()

        # Add nodes
        G.add_nodes_from(['A', 'B', 'C', 'D', 'E'])
        # Add edges (connections between nodes)
        G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'), ('D', 'E')])

        # Generate a force-directed layout (spring layout)
        pos = nx.spring_layout(G)

        # Draw the graph
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=12, font_color='black',
                edge_color='gray')
        plt.show()
        pass

    def graph_column_layout(self):
        import networkx as nx
        import matplotlib.pyplot as plt
        G = nx.DiGraph()
        G.add_edges_from([
            ('Root', 'A'),
            ('Root', 'B'),
            ('A', 'C'),
            ('A', 'D'),
            ('B', 'E'),
            ('B', 'F'),
            ('C', 'G'),
            ('D', 'H'),
            ('E', 'I'),
        ])
        pos = {}  # Dictionary to store positions of nodes
        layers = {}  # Dictionary to track which layer (column) each node is in

        def assign_layers(node, layer=0):
            """ Recursively assign nodes to columns (layers) """
            if node not in layers:
                layers[node] = layer
            else:
                layers[node] = max(layers[node], layer)

            neighbors = list(G.successors(node))
            if neighbors:
                for i, neighbor in enumerate(neighbors):
                    # Assign each child to the next layer
                    assign_layers(neighbor, layer + 1 + i)

        # Start assigning layers from the root
        root = [n for n, d in G.in_degree() if d == 0][0]
        assign_layers(root)

        # Calculate the positions of nodes
        max_layer = max(layers.values())
        for node, layer in layers.items():
            same_layer_nodes = [n for n, l in layers.items() if l == layer]
            y_pos = same_layer_nodes.index(node)  # Place nodes in different rows in the same column
            pos[node] = (layer, -y_pos)  # X is the layer (column), Y is the row

        # Draw the graph
        plt.figure(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10, font_color='black',
                edge_color='gray')
        plt.show()
        pass


if __name__ == "__main__":
    # Sample input from the previously decoded content
    drawio = DrawIO("../../S7_Data/B3Z11502.gr7")
