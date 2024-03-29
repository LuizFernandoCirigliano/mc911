import json

blue = '#42d9f4'
red = '#ff9696'
yellow = '#eeff00'


def vis_data_for_tree(root):
    nodes = []
    edges = []
    n_id = 0
    e_id = 0

    def rec_data_for_tree(node, parent_id, label=None):
        if not node:
            return

        nonlocal nodes, edges, n_id, e_id

        color = yellow if node is None else blue if node.is_valid else red
        node_dict = {
                      "id": n_id,
                      "label": str(node),
                      "color": color
                    }
        if not node.is_valid:
            err_msg = "\n".join([issue.message() for issue in node.issues])\
                            if len(node.issues) > 0 else "invalid children"

            node_dict['title'] = err_msg

        nodes.append(node_dict)

        if parent_id is not None:
            d = {"from": parent_id, "to": n_id, "id": e_id}
            if label:
                d['label'] = label
            edges.append(d)

        cur_id = n_id
        n_id += 1
        e_id += 1

        children, labels = node.children, node.labels
        for i, child in enumerate(children):
            label = labels[i] if labels else None
            rec_data_for_tree(child, cur_id, label)

    rec_data_for_tree(root, None)
    return json.dumps(nodes), json.dumps(edges)


def make_js(nodes, edges):
    js_string = "<script>"
    js_string += "var nodes = {0}\n".format(nodes)
    js_string += "var edges = {0}\n".format(edges)

    js_string += "var data = {\n\
        nodes: nodes,\n\
        edges: edges\n\
    };\n\
    // create a network\n\
    var container = document.getElementById('network');\n\
    var options = {\n\
        layout: {\n\
            hierarchical: {\n\
                direction: \"UD\",\n\
                sortMethod: \"directed\"\n\
            }\n\
        },\n\
        physics: {\n\
            enabled: false\n\
        }\n\
    };\n\
    var network = new vis.Network(container, data, options);\n"

    js_string += "</script>\n"
    return js_string


def make_head():
    head_string = "<head>\n\
    <meta charset=\"utf-8\">\n\
    <title>Hierarchical Layout without Physics</title>\n\
    <script type=\"text/javascript\" src=\"../vis/vis.js\"></script>\n\
    <link href=\"../vis/vis-network.min.css\" rel=\"stylesheet\" type=\"text/css\" />\n\
    <style type=\"text/css\">\n\
        #network{\n\
            width: 100%;\n\
            bottom: 90%\n\
            border: 1px solid lightgray;\n\
        }\n\
\n\
        td {\n\
            vertical-align:top;\n\
        }\n\
        table {\n\
            width:800px;\n\
        }\n\
    </style>\n\
    </head> \n"
    return head_string


def make_html(root_node):
    nodes, edges = vis_data_for_tree(root_node)
    html_string = "<html>\n"
    html_string += make_head()
    html_string += "<body> \n\
    <h1>AST Gerada</h1>\n\
    <div id=\"network\"></div>\n\
    "
    html_string += make_js(nodes, edges)
    html_string += "</body></html>\n"
    return html_string
