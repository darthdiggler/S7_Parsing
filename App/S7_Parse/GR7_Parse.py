import xml.etree.ElementTree as ET
import re
import os

class GR7_Parse:
    def __init__(self, gr7_file):
        self.file = gr7_file
        self.filename = os.path.basename(gr7_file)
        self.active_file = open(self.file, 'r')
        self.gr7_data = self.active_file.read()

        # Parse the sequences, steps, and transition
        self.seq_list = self.parse_sequences(self.gr7_data)
        for sequence in self.seq_list:
            sequence['step_data'] = self.parse_steps(sequence['sequence_data'])
            sequence['transition_data'] = self.parse_transitions(sequence['sequence_data'])
            # sequence['drawio_xml_data'] = self.create_drawio_xml(sequence['step_data'], sequence['transition_data'])
            # self.graph_diagram(sequence['step_data'], sequence['transition_data'])
            self.graph_column_layout()
            pass

        # Generate the XML data and save as draw.io
        self.drawio_file = '../../Parsed_Data/'  + self.filename[:-4] + 'GR7.drawio'
        self.active_iofile = open(self.drawio_file, 'wb')
        self.active_iofile.write(self.drawio_xml_data)

    def parse_sequences(self, gr7_data):
        sequences = gr7_data.split('END_FUNCTION_BLOCK')
        sequences.pop()

        # Adjusted regex pattern to find multiple matches
        pattern = (r"\(\*\$_COM\s+([^\n]+)\n(.*?)\)\s*\n\(\*\$_CMPSET\s+(.*?)\s*\)\s*\n\(\*\$_SETTINGS\s+(.*?)\s*\)\s*"
                   r"(VAR_INPUT\s+(.*?)\s+END_VAR)?\s*(PERM_CONDITION_AT_BEGIN\s+(.*?)\s+END_PERM_CONDITION)?")

        # Parse Sequence Info
        parsed_sequences = []
        for sequence in sequences:
            # Using finditer to capture matches and their positions
            fb_name = sequence.replace("FUNCTION_BLOCK ",'')
            fb_name = fb_name[0:fb_name.find('\n')]
            matches = re.finditer(pattern, sequence, re.DOTALL)

            # Process each match and get start and end positions
            for match in matches:
                name = match.group(1).strip()  # Extract and strip the name
                comments = match.group(2).strip()  # Extract and strip the comments
                cmpset = match.group(3).strip()
                settings = match.group(4).strip()

                # Extract optional sections and sequence data
                var_input = match.group(6) if match.group(6) else "No VAR_INPUT"
                perm_condition = match.group(8) if match.group(8) else "No PERM_CONDITION_AT_BEGIN"
                match_start, match_end = match.span()
                sequence_data = sequence[match_end:]

                parsed_sequences.append({
                    'fb_name': fb_name,
                    'seq_name': name,
                    'comment': comments,
                    'cmpset': cmpset,
                    'settings': settings,
                    'var_input': var_input,
                    'perm_condition': perm_condition,
                    'sequence_data': sequence_data
                })
        return parsed_sequences

    def parse_steps(self, gr7_data):
        """ This function will parse the steps information from the Step7 gernerated .gr7 file
        and map them into dictionaries by name.

        :param gr7_data:
        :return: parsed_steps
        """
        # Regex pattern to capture step name, number, and comment
        pattern = (r"STEP\s+([A-Za-z0-9_]+)\s+\(\*\$_NUM\s+(\d+)\*\):\s+\(\*\$_COM\s+([^*]+)\*\)\s*(SUPERVISION\s+"
                   r"CONDITION\s*:=\s*(.*?)\s+END_SUPERVISION)?\s*(.*?)(?=END_STEP)")

        matches = re.finditer(pattern, gr7_data, re.DOTALL)

        # Process each match
        parsed_steps = []
        for match in matches:
            step_name = match.group(1).strip()  # Extract and strip the step name
            step_number = match.group(2).strip()  # Extract the step number
            step_comment = match.group(3).strip()  # Extract the comment
            # Extract optional sections
            supervision = match.group(5) if match.group(5) else "No Supervision"
            condition = match.group(6).strip().split('\n') if match.group(6)else "No Condition"
            parsed_steps.append({
                'name': step_name,
                'number': step_number,
                'supervision': supervision,
                'condition': condition,
                'comment': step_comment
            })
        return parsed_steps

    def parse_transitions(self, gr7_data):
        """ This function will parse the transition information from the Step7 gernerated .gr7 file
        and map them into dictionaries by name.

        :param gr7_text:
        :return: parsed_transitions
        """
        # Regex pattern to capture the transition details
        #transition_pattern = r"TRANSITION\s+(\w+)\s+\(\*\$_NUM\s+(\d+)\*\)\s+FROM\s+(\w+)\s+TO\s+\(([\w\s,]+)\)\s*:\s*CONDITION\s*:=\s*([\w\.]+)"
        transition_pattern = r"TRANSITION\s+([A-Za-z0-9_]+)\s+\(\*\$_NUM\s+(\d+)\*\)\s+FROM\s+([A-Za-z0-9_]+)\s+TO\s+([A-Za-z0-9_]+)\s+CONDITION\s*:=\s*(.*?)\s+END_TRANSITION"
        transitions = re.findall(transition_pattern, gr7_data)

        # Parse transitions
        parsed_transitions = []
        for transition in transitions:
            transition_name = transition[0]
            transition_num = transition[1]
            from_states = transition[2].split(", ")
            to_states = transition[3].split(", ")
            condition = transition[4]
            parsed_transitions.append({
                'name': transition_name,
                'number': transition_num,
                'from': from_states,
                'to': to_states,
                'condition': condition
            })
        return parsed_transitions

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

    def graph_diagram(self, steps, transitions):
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
    s7g = GR7_Parse("../../S7_Data/B3Z11502.gr7")
