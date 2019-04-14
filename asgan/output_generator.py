import asgan.fasta_parser as fp
import networkx as nx


def assembly_graph_save_dot(graph, out_dir, out_file):
    with open("{}/{}".format(out_dir, out_file), "w") as f:
        f.write("digraph {\n")
        f.write("  node [shape=point]\n")
        f.write("  edge [penwidth=5, color=green, fontsize=20]\n")

        for (node_from, node_to, data) in graph.edges(data=True):
            edge_color = ["green", "black"][data["is_repeat"]]
            f.write("  {} -> {} [label=\"{}\", color=\"{}\"]\n".format(
                node_from, node_to, data["name"], edge_color))

        f.write("}\n")


def save_raw_hits(raw_hits, out_dir, out_file):
    raw_hits.sort(key=lambda hit: (hit.query_name, hit.query_start))
    out_file = "{}/{}".format(out_dir, out_file)

    with open(out_file, "w") as f:
        for raw_hit in raw_hits:
            f.write(str(raw_hit) + "\n")


def output_blocks_info(synteny_blocks_query, synteny_blocks_target, out_dir, out_file):
    def _output_blocks_info(synteny_blocks):
        for seq, blocks in synteny_blocks.items():
            blocks.sort(key=lambda block: block.start)

            for block in blocks:
                f.write(str(block) + "\n")

            f.write("\n")

    with open("{}/{}".format(out_dir, out_file), "w") as f:
        f.write("Query:\n\n")
        _output_blocks_info(synteny_blocks_query)

        f.write("\nTarget:\n\n")
        _output_blocks_info(synteny_blocks_target)


def adjacency_graph_save_dot(adjacency_graph, out_dir, out_file, block_attributes=None):
    def get_edge_color(edge_name):
        if block_attributes is None:
            if edge_name.startswith("+") or edge_name.startswith("-"):
                return "green"
            else:
                return "black"
        else:
            edge_color = block_attributes["color"].get(edge_name)

        if edge_color is None:
            return "black"

        return edge_color

    def get_edge_label(edge_name):
        if edge_name.startswith("+") or edge_name.startswith("-"):
            return edge_name

        return ""

    def get_edge_style(edge_name):
        if block_attributes is None:
            return "solid"
        else:
            edge_style = block_attributes["style"].get(edge_name)

            if edge_style is None:
                return "solid"

            return edge_style

    def contains_synteny_blocks(component):
        for (_, _, data) in component.edges(data=True):
            if data["name"].startswith("+") or data["name"].startswith("-"):
                return True

        return False

    with open("{}/{}".format(out_dir, out_file), "w") as f:
        f.write("digraph {\n")
        f.write("  node [shape=point, width=0.06]\n")
        f.write("  edge [fontsize=20]\n")
        f.write("  graph[center=true, margin=0.5, ")
        f.write("nodesep=0.45, ranksep=0.35]\n")

        for component in nx.weakly_connected_component_subgraphs(adjacency_graph, copy=False):
            if not contains_synteny_blocks(component):
                continue

            for node_from, node_to, data in component.edges(data=True):
                edge_color = get_edge_color(data["name"])
                edge_label = get_edge_label(data["name"])
                edge_style = get_edge_style(data["name"])
                edge_penwidth = 3 if edge_color == "black" else 6

                f.write("  {} -> {} [".format(node_from, node_to))
                f.write("label=\"{}\", ".format(edge_label))
                f.write("color=\"{}\", ".format(edge_color))
                f.write("style=\"{}\", ".format(edge_style))
                f.write("penwidth=\"{}\"]\n".format(edge_penwidth))

        f.write("}\n")


def breakpoint_graph_save_dot(graph, max_matching, out_dir, out_file):
    def get_edge_color(node_from, node_to):
        if (node_from, node_to) in max_matching:
            return "green"

        if (node_to, node_from) in max_matching:
            return "green"

        return "black"

    with open("{}/{}".format(out_dir, out_file), "w") as f:
        f.write("graph {\n")
        f.write("  edge [penwidth=5]\n")
        f.write("  node [fontsize=20]\n")

        for node, data in graph.nodes(data=True):
            f.write("  {} [label=\"{}\"]\n".format(node, data["label"]))

        for (node_from, node_to) in graph.edges():
            color = get_edge_color(node_from, node_to)
            f.write("  {} -- {} [color={}]\n".format(
                node_from, node_to, color))

        f.write("}\n")


def path_components_save_dot(paths, unused_edges, out_dir):
    def save(out_file, with_unused_edges=False):
        with open("{}/{}.gv".format(out_dir, out_file), "w") as f:
            f.write("graph {\n")
            f.write("  node [fontsize=20]\n")
            f.write("  edge [penwidth=5]\n")

            for (node, data) in paths.nodes(data=True):
                f.write("  {} [label=\"{}\"]\n".format(node, data["label"]))

            for (node_from, node_to) in paths.edges():
                f.write("  {} -- {} [color=green] \n".format(node_from, node_to))

            if with_unused_edges:
                for (node_from, node_to) in unused_edges:
                    f.write("  {} -- {} [style=dashed]\n".format(node_from, node_to))

            f.write("}\n")

    save("paths")
    save("paths_with_unused_edges", with_unused_edges=True)


def save_path_sequences(paths_query, paths_target, out_dir):
    def write_path(path, f):
        for block in path:
            f.write(str(block) + "\n")

    with open("{}/synteny_paths.txt".format(out_dir), "w") as f:
        f.write("Query:\n\n")
        for path in paths_query:
            write_path(path, f)
            f.write("\n")

        f.write("Target:\n\n")
        for path in paths_target:
            write_path(path, f)
            f.write("\n")


def path_sequences_save_fasta(paths_query, sequences_fasta_query,
                              paths_target, sequences_fasta_target,
                              out_dir):
    def complement(seq):
        complement_nt = {"A": "T", "T": "A", "C": "G", "G": "C"}
        complement_seq = ""

        for nt in reversed(seq):
            complement_seq += complement_nt[nt]

        return complement_seq

    sequences_query = fp.make_fasta_dict(sequences_fasta_query)
    sequences_target = fp.make_fasta_dict(sequences_fasta_target)

    path_query = paths_query[0]
    path_target = paths_target[0]

    sequence_query = ""
    sequence_target = ""

    for block in path_query:
        sequence = sequences_query[block.sequence_name[:-1]]

        if block.sequence_name[-1] == "+":
            sequence_query += sequence[block.start:block.end + 1]
        else:
            sequence_query += complement(sequence)[block.start:block.end + 1]

    for block in path_target:
        sequence = sequences_target[block.sequence_name[:-1]]

        if block.sequence_name[-1] == "+":
            sequence_target += sequence[block.start:block.end + 1]
        else:
            sequence_target += complement(sequence)[block.start:block.end + 1]

    with open("{}/path-query-1.fasta".format(out_dir), "w") as f:
        f.write(">query_path1\n")
        f.write(sequence_query + "\n")

    with open("{}/path-target-1.fasta".format(out_dir), "w") as f:
        f.write(">target_path1\n")
        f.write(sequence_target + "\n")


def output_stats(stats, out_dir):
    with open("{}/stats.txt".format(out_dir), "w") as f:
        # header
        f.write("\tQuery       \tTarget\n")

        # wcc
        number_wcc_query = pretty_number(stats["number_wcc_query"])
        number_wcc_target = pretty_number(stats["number_wcc_target"])
        f.write("cc\t{}\t{}\n\n".format(number_wcc_query, number_wcc_target))

        # sequences
        number_sequences_query = pretty_number(stats["number_sequences_query"])
        number_sequences_target = pretty_number(stats["number_sequences_target"])
        sequences_total_length_query = pretty_number(stats["sequences_total_length_query"])
        sequences_total_length_target = pretty_number(stats["sequences_total_length_target"])
        sequences_n50_query = pretty_number(stats["sequences_n50_query"])
        sequences_n50_target = pretty_number(stats["sequences_n50_target"])
        sequences_l50_query = pretty_number(stats["sequences_l50_query"])
        sequences_l50_target = pretty_number(stats["sequences_l50_target"])

        f.write("seqs\t{}\t{}\n".format(number_sequences_query, number_sequences_target))
        f.write("tlen\t{}\t{}\n".format(sequences_total_length_query, sequences_total_length_target))
        f.write("N50\t{}\t{}\n".format(sequences_n50_query, sequences_n50_target))
        f.write("L50\t{}\t{}\n\n".format(sequences_l50_query, sequences_l50_target))

        # blocks
        number_blocks_query = pretty_number(stats["number_blocks"])
        number_blocks_target = pretty_number(stats["number_blocks"])
        blocks_total_length_query = pretty_number(stats["blocks_total_length_query"])
        blocks_total_length_target = pretty_number(stats["blocks_total_length_target"])
        blocks_n50_query = pretty_number(stats["blocks_n50_query"])
        blocks_n50_target = pretty_number(stats["blocks_n50_target"])
        blocks_l50_query = pretty_number(stats["blocks_l50_query"])
        blocks_l50_target = pretty_number(stats["blocks_l50_target"])

        f.write("blocks\t{}\t{}\n".format(number_blocks_query, number_blocks_target))
        f.write("tlen\t{}\t{}\n".format(blocks_total_length_query, blocks_total_length_target))
        f.write("N50\t{}\t{}\n".format(blocks_n50_query, blocks_n50_target))
        f.write("L50\t{}\t{}\n\n".format(blocks_l50_query, blocks_l50_target))

        # paths
        number_paths_query = pretty_number(stats["number_paths"])
        number_paths_target = pretty_number(stats["number_paths"])
        paths_total_length_query = pretty_number(stats["paths_total_length_query"])
        paths_total_length_target = pretty_number(stats["paths_total_length_target"])
        paths_n50_query = pretty_number(stats["paths_n50_query"])
        paths_n50_target = pretty_number(stats["paths_n50_target"])
        paths_l50_query = pretty_number(stats["paths_l50_query"])
        paths_l50_target = pretty_number(stats["paths_l50_target"])

        f.write("paths\t{}\t{}\n".format(number_paths_query, number_paths_target))
        f.write("tlen\t{}\t{}\n".format(paths_total_length_query, paths_total_length_target))
        f.write("N50\t{}\t{}\n".format(paths_n50_query, paths_n50_target))
        f.write("L50\t{}\t{}\n\n".format(paths_l50_query, paths_l50_target))

        # link types and united components
        f.write("link types: {} {} {} {}\n".format(*stats["link_types"]))
        f.write("uc: {}\n".format(stats["number_united_components"]))


def pretty_number(number, min_width=12, fill=" "):
    digits = []
    number = str(number)
    is_neg = False

    if number.startswith("-"):
        is_neg = True
        number = number[1:]

    start = int(round(len(number) % 3, 0))

    if start != 0:
        digits.append(number[:start])
    digits.extend([number[i:i+3] for i in range(start, len(number), 3)])

    number = "\'".join(digits)
    if is_neg:
        number = "-" + number

    if min_width is not None and len(number) < min_width:
        number += " " * (min_width - len(number))

    return number