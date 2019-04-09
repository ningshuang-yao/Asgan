from asgan.stats import calc_path_length


def output_blocks_info(aln_blocks_query, aln_blocks_target, out_dir):
    def _output_blocks_info(file, aln_blocks):
        for seq, blocks in aln_blocks.items():
            blocks.sort(key=lambda block: block.start)

            seq_name = blocks[0].seq_name
            seq_len = pretty_number(blocks[0].seq_length)
            f.write("seq={} len={}\n".format(seq_name, seq_len))

            for block in blocks:
                f.write(str(block) + "\n")

            f.write("\n")

    with open("{}/alignment_blocks.txt".format(out_dir), "w") as f:
        f.write("Query blocks:\n")
        _output_blocks_info(f, aln_blocks_query)

        f.write("\nTarget blocks:\n")
        _output_blocks_info(f, aln_blocks_target)


def assembly_graph_save_dot(graph, outfile, outdir):
    with open("{}/{}".format(outdir, outfile), "w") as f:
        f.write("digraph {\n")
        f.write("  node [shape=point]\n")
        f.write("  edge [penwidth=5, color=green, fontsize=20]\n")

        for (node_from, node_to, data) in graph.edges(data=True):
            color = ["green", "black"][data["is_repeat"]]
            f.write("  {} -> {} [label=\"{}\", color=\"{}\"]\n".format(
                node_from, node_to, data["name"], color))

        f.write("}\n")


def alignment_graph_save_dot(graph, outfile, block_colors, block_styles, outdir):
    def get_edge_color(edge_name):
        edge_color = block_colors.get(edge_name)

        if edge_color is not None:
            return edge_color

        return "black"

    def get_edge_label(edge_name):
        if edge_name.startswith("+") or edge_name.startswith("-"):
            return edge_name

        return ""

    def get_edge_style(edge_name):
        edge_style = block_styles.get(edge_name)

        if edge_style is not None:
            return edge_style

        return "solid"

    with open("{}/{}".format(outdir, outfile), "w") as f:
        f.write("digraph {\n")
        f.write("  node [shape=point, width=0.06]\n")
        f.write("  edge [fontsize=20]\n")
        f.write("  graph[center=true, margin=0.5, ")
        f.write("nodesep=0.45, ranksep=0.35]\n")

        '''
        for node, data in graph.nodes(data=True):
            dist = data.get("distance")
            f.write("  {} [label=\"{}\"]\n".format(node, dist))
        '''

        for node_from, node_to, data in graph.edges(data=True):
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


def breakpoint_graph_save_dot(graph, max_matching, outdir):
    def get_edge_color(node_from, node_to):
        if (node_from, node_to) in max_matching:
            return "green"

        if (node_to, node_from) in max_matching:
            return "green"

        return "black"

    with open("{}/{}.gv".format(outdir, "breakpoint_graph"), "w") as f:
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


def paths_graph_save_dot(paths, unused_edges, out_dir):
    def save(filename, with_unused_edges=False):
        with open("{}/{}.gv".format(out_dir, filename), "w") as f:
            f.write("graph {\n")
            f.write("  node [fontsize=20]\n")
            f.write("  edge [penwidth=5]\n")

            for node, data in paths.nodes(data=True):
                f.write("  {} [label=\"{}\"]\n".format(node, data["label"]))

            for (node_from, node_to) in paths.edges():
                f.write("  {} -- {} [color=green] \n".format(node_from, node_to))

            if with_unused_edges:
                for (node_from, node_to) in unused_edges:
                    f.write("  {} -- {} [style=dashed]\n".format(node_from, node_to))

            f.write("}\n")

    save("paths")
    save("paths_with_unused_edges", with_unused_edges=True)


def save_full_paths(paths_query, paths_target, outdir):
    def write_path(path, f):
        path_length = calc_path_length(path)

        for i in range(len(path)):
            if i % 2 == 0:
                f.write("{} [{}]\n".format(path[i].signed_id(), pretty_number(path[i].length())))
            else:
                for (sequence_name, sequence_length) in path[i]:
                    f.write("  {} [{}]\n".format(sequence_name, pretty_number(sequence_length)))

        f.write("length={}\n\n".format(pretty_number(path_length)))

    with open("{}/paths.txt".format(outdir), "w") as f:
        for i in range(len(paths_query)):
            f.write("query forward:\n")
            write_path(paths_query[i][0], f)
            f.write("target forward:\n")
            write_path(paths_target[i][0], f)

            f.write("query reverse:\n")
            write_path(paths_query[i][1], f)
            f.write("target reverse:\n")
            write_path(paths_target[i][1], f)
            f.write("------------\n\n")


def output_stats(stats, outdir):
    min_length = 12
    with open("{}/stats.txt".format(outdir), "w") as f:
        f.write("\tQuery       \tTarget\n")
        f.write("CC\t{}\t{}\n\n".format(pretty_number(stats["number_wcc_query"], min_length=min_length),
                                        pretty_number(stats["number_wcc_target"], min_length=min_length)))

        f.write("Contigs\t{}\t{}\n".format(pretty_number(stats["number_contigs_query"], min_length=min_length),
                                           pretty_number(stats["number_contigs_target"], min_length=min_length)))
        f.write("tlen\t{}\t{}\n".format(pretty_number(stats["contigs_total_length_query"], min_length=min_length),
                                        pretty_number(stats["contigs_total_length_target"], min_length=min_length)))
        f.write("N50\t{}\t{}\n".format(pretty_number(stats["contigs_n50_query"], min_length=min_length),
                                       pretty_number(stats["contigs_n50_target"], min_length=min_length)))
        f.write("L50\t{}\t{}\n\n".format(pretty_number(stats["contigs_l50_query"], min_length=min_length),
                                         pretty_number(stats["contigs_l50_target"], min_length=min_length)))

        f.write("Blocks\t{}\t{}\n".format(pretty_number(stats["number_alignment_blocks"], min_length=min_length),
                                          pretty_number(stats["number_alignment_blocks"], min_length=min_length)))
        f.write("tlen\t{}\t{}\n".format(pretty_number(stats["alignment_blocks_total_length_query"],
                                                      min_length=min_length),
                                        pretty_number(stats["alignment_blocks_total_length_target"],
                                                      min_length=min_length)))
        f.write("N50\t{}\t{}\n".format(pretty_number(stats["alignment_blocks_n50_query"], min_length=min_length),
                                       pretty_number(stats["alignment_blocks_n50_target"], min_length=min_length)))
        f.write("L50\t{}\t{}\n\n".format(pretty_number(stats["alignment_blocks_l50_query"], min_length=min_length),
                                         pretty_number(stats["alignment_blocks_l50_target"], min_length=min_length)))

        f.write("Paths\t{}\t{}\n".format(pretty_number(stats["number_paths"], min_length=min_length),
                                         pretty_number(stats["number_paths"], min_length=min_length)))
        f.write("tlen\t{}\t{}\n".format(pretty_number(stats["paths_total_length_query"], min_length=min_length),
                                        pretty_number(stats["paths_total_length_target"], min_length=min_length)))
        f.write("N50\t{}\t{}\n".format(pretty_number(stats["paths_n50_query"], min_length=min_length),
                                       pretty_number(stats["paths_n50_target"], min_length=min_length)))
        f.write("L50\t{}\t{}\n".format(pretty_number(stats["paths_l50_query"], min_length=min_length),
                                       pretty_number(stats["paths_l50_target"], min_length=min_length)))

        f.write("Link types: {}".format(stats["link_types"]))


def pretty_number(number, min_length=None, fill=" "):
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

    if min_length is not None and len(number) < min_length:
        number += " " * (min_length - len(number))

    return number
