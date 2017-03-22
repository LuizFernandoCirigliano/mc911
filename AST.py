from node import Node
import json

def visDataForTree(root):
    nodes = []
    edges = []
    n_id = 0
    e_id = 0

    def recDataForTree(node_list, parent_id):
        nonlocal nodes, edges, n_id, e_id

        if node_list is None:
            return

        if type(node_list) == Node:
            node_list = [node_list]

        for node in node_list:
            nodes.append( { "id": n_id, "label": str(node)})

            if parent_id is not None:
                edges.append( { "from": parent_id, "to": n_id, "id" : e_id})

            cur_id = n_id
            n_id += 1
            e_id += 1

            for child in node.children:
                recDataForTree(child, cur_id)


    recDataForTree(root, None)
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
        }\n\
    };\n\
    var network = new vis.Network(container, data, options);\n"

    js_string += "</script>\n"
    return js_string

def make_head():
    head_string = "<head>\n\
    <meta charset=\"utf-8\">\n\
    <title>Hierarchical Layout without Physics</title>\n\
    <script type=\"text/javascript\" src=\"./vis/vis.js\"></script>\n\
    <link href=\"./vis/vis-network.min.css\" rel=\"stylesheet\" type=\"text/css\" />\n\
    <style type=\"text/css\">\n\
        #network{\n\
            width: 1000px;\n\
            height: 400px;\n\
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
    nodes, edges = visDataForTree(root_node)
    html_string = "<html>\n"
    html_string += make_head()
    html_string += "<body> \n\
    <h1>AST Gerada</h1>\n\
    <div id=\"network\" style=\"height:100%\"></div>\n\
    "
    html_string += make_js(nodes, edges)
    html_string += "</body></html>\n"
    return html_string


def test():
    c1 = Node('ID', None, 'x')
    c2 = Node('ID', None, 'y')
    p = Node('expr', [c1,c2], '+')
    html =  make_html(p)
    with open("ast.html", 'w') as html_file:
        html_file.write(html)



if __name__ == '__main__':
    test()