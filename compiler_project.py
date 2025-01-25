import re
import matplotlib.pyplot as plt
import networkx as nx

# Lexical Analysis
def lexical_analysis(code):
    """
    Performs lexical analysis on the given code.
    Returns a list of tokens.
    """
    pattern = r"(?P<Keyword>\bint\b|\bstring\b|\bbool\b|\bif\b|\belse\b|\bfor\b|\bwhile\b|\bfloat\b|\bdouble\b|\bchar\b)|(?P<Identifier>[a-zA-Z_]\w*)|(?P<Number>\b\d+\b)|(?P<FloatNumber>\b\d+\.\d+\b)|(?P<StringLiteral>\"[^\"]*\")|(?P<Operator>[=+\-*/;(){}])|(?P<Punctuation>[,.;])"
    regex = re.compile(pattern)
    matches = regex.finditer(code)

    tokens = []
    for match in matches:
        for group_name in regex.groupindex.keys():
            if match.group(group_name):
                tokens.append((group_name, match.group(group_name)))
    return tokens

# Syntax Analysis
def syntax_analysis(tokens):
    """
    Performs syntax analysis and builds a parse tree if the syntax is correct.
    Validates type and value consistency during syntax analysis.
    """
    parse_tree = {"<declaration>": []}

    if (len(tokens) == 5 and
        tokens[0][0] == "Keyword" and
        tokens[1][0] == "Identifier" and
        tokens[2][0] == "Operator" and tokens[2][1] == "=" and
        tokens[4][0] == "Operator" and tokens[4][1] == ";"):

        variable_type = tokens[0][1]  # e.g., int, string, float
        value_token = tokens[3]       # (Token Type, Value)

        # Validate type and value consistency
        if variable_type == "int" and value_token[0] != "Number":
            print("Syntax error: A string literal cannot be assigned to an integer variable.")
            return None
        elif variable_type == "string" and value_token[0] != "StringLiteral":
            print("Syntax error: Invalid value for string variable.")
            return None
        elif variable_type == "float" and value_token[0] not in ["Number", "FloatNumber"]:
            print("Syntax error: Invalid value for float variable.")
            return None

        # Build the parse tree
        parse_tree["<declaration>"].append({"<type>": f"{tokens[0][0]}: {tokens[0][1]}"} )
        parse_tree["<declaration>"].append({"<identifier>": f"{tokens[1][0]}: {tokens[1][1]}"} )
        parse_tree["<declaration>"].append({"<assignment_operator>": f"{tokens[2][0]}: {tokens[2][1]}"} )
        parse_tree["<declaration>"].append({"<value>": f"{tokens[3][0]}: {tokens[3][1]}"} )
        parse_tree["<declaration>"].append({"<semicolon>": f"{tokens[4][0]}: {tokens[4][1]}"} )
        return parse_tree

    print("Syntax error: Invalid syntax.")
    return None

# Semantic Analysis
def semantic_analysis(variable_type, value_token):
    """
    Performs semantic analysis based on variable type and value.
    Ensures the value matches the declared data type.
    """
    if variable_type == "int":
        try:
            int(value_token)  # Check if value is an integer
            return True, "No semantic errors found."
        except ValueError:
            return False, f"Semantic error: '{value_token}' is not a valid integer."
    elif variable_type == "string":
        if value_token.startswith('"') and value_token.endswith('"'):
            return True, "No semantic errors found."
        return False, f"Semantic error: '{value_token}' is not a valid string (must be in double quotes)."
    elif variable_type == "float":
        try:
            float(value_token)  # Check if value is a float
            return True, "No semantic errors found."
        except ValueError:
            return False, f"Semantic error: '{value_token}' is not a valid float."
    else:
        return False, f"Semantic error: Unsupported type '{variable_type}'."

# Function to display results
def display_results(line):
    """
    Displays the lexical analysis, syntax analysis, semantic analysis, and parse tree for a single line of input.
    """
    print(f"\nInput Code: {line}")

    # Lexical Analysis
    tokens = lexical_analysis(line)
    print("\nLexical Analysis:")
    for token in tokens:
        print(f"{token[0]}: {token[1]}")

    # Handle semantic analysis separately, even if syntax is incorrect
    print("\nSemantic Analysis:")
    # Check if the first token is a valid keyword and if the value is valid for the type
    if len(tokens) >= 4:  # Ensure enough tokens for variable assignment (e.g., 'int x = 5;')
        variable_type = tokens[0][1]  # e.g., 'int', 'string', etc.
        value_token = tokens[3][1]    # The value assigned (e.g., 5, "Alice", etc.)

        # Perform semantic analysis regardless of syntax error
        is_semantic_correct, semantic_message = semantic_analysis(variable_type, value_token)
        print(semantic_message)

    # Syntax Analysis (if the format is correct, we will print the parse tree)
    print("\nSyntax Analysis:")
    parse_tree = syntax_analysis(tokens)
    if parse_tree:
        print("Syntax is correct.")

        # Print Parse Tree
        print("\nParse Tree:")
        for key, children in parse_tree.items():
            print(f"{key}:")
            for child in children:
                for subkey, subvalue in child.items():
                    print(f"  {subkey}: {subvalue}")
        plot_parse_tree(parse_tree)
    else:
        print("Syntax error: Invalid syntax.")

# Function to plot the parse tree
def plot_parse_tree(parse_tree):
    """
    Plots the parse tree using matplotlib and networkx.
    """
    graph = nx.DiGraph()

    # Helper function to add nodes and edges recursively
    def add_nodes_edges(tree, parent=None):
        for key, children in tree.items():
            graph.add_node(key)
            if parent:
                graph.add_edge(parent, key)
            for child in children:
                for subkey, subvalue in child.items():
                    graph.add_node(subvalue)
                    graph.add_edge(key, subvalue)

    add_nodes_edges(parse_tree)

    # Layout for hierarchical tree
    def hierarchy_pos(G, root, width=1., vert_gap=0.5, vert_loc=0, xcenter=0.5):
        pos = {root: (xcenter, vert_loc)}
        children = list(G.successors(root))
        if not children:
            return pos
        dx = width / len(children)
        nextx = xcenter - width / 2 - dx / 2
        for child in children:
            nextx += dx
            pos.update(hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                     vert_loc=vert_loc - vert_gap, xcenter=nextx))
        return pos

    pos = hierarchy_pos(graph, root="<declaration>")
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold")
    plt.title("Parse Tree")
    plt.show()

# Main function
def main():
    print("\nEnter your code line by line (type 'done' to finish):")
    while True:
        line = input(">> ").strip()
        if line.lower() == "done":
            print("Exiting program...")
            break
        elif line:
            display_results(line)
        else:
            print("Empty input, please enter a valid line of code.")

if __name__ == "__main__":
    main()
