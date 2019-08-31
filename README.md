Asgan – [As]sembly [G]raphs [An]alyzer – is a tool for analysis of assembly graphs.
The tool takes two assembly graphs in the _GFA_ format as input and finds the minimum set
of homologous sequences (synteny paths) shared between the graphs. As output, Asgan
produces various statistics and a visualization of the found paths in the _gv_ format.

# Installation
```
git clone --recurse-submodules https://github.com/epolevikov/Asgan
make -C Asgan/lib/minimap2
```

# Usage example
The _test_ folder contains two bacterial assembly from the NCTC collections produced by Flye
and Canu assemblers. To run Asgan for these datasets, use the following command:
```
cd Asgan
python asgan.py \
    --input-query=test/flye-nctc9016.gfa \
    --input-target=test/canu-nctc9016.gfa \
    --out-dir=flye-vs-canu
```
After analysis is finished, the output directory will contain:
* <strong>adjacency_graph_{query, target}.gv</strong> – a visualization of synteny paths.
* <strong>synteny_paths.txt</strong> – synteny paths in the format of an alignment.
* <strong>stats.txt</strong> – various statistics based on the found synteny paths.

Here is how the visualization looks like:

<p align="center">
    <img src="https://github.com/epolevikov/Asgan/blob/master/example.png">
</p>

The graph built by Canu consists of two separated sequences. One of them represents a forward (+1, +2, +3, +4) strand,
the other corresponds to a reverse complement (-4, -3, -2, -1) strand of a bacterial chromosome. The graph built by Flye
consists of one connected component, where two complementary strands are merged through common unresolved repeats.
Although the structures of the graphs are different, they share one synteny path that corresponds to a bacterial chromosome.

A file named _synteny_paths.txt_ contains the found synteny paths in the format of an alignment. For the above
datasets, the file looks like this:
```
+1      contig_8+       5'078'954       56'910          389'537         contig_2-       425'024         47'878          378'220     
        contig_8+       5'078'954       389'537         451'517         contig_7+       16'794          0               16'794      
+2      contig_8+       5'078'954       451'517         662'367         contig_6+       209'014         0               209'014     
        contig_8+       5'078'954       662'367         682'556         contig_7-       16'794          0               16'794      
+3      contig_8+       5'078'954       682'556         3'667'386       contig_1+       2'964'866       11              2'964'858   
        contig_8+       5'078'954       3'667'386       3'691'634       contig_5-       24'049          0               24'049      
+4      contig_8+       5'078'954       3'691'634       5'064'579       contig_3+       1'364'661       0               1'364'661
```
The first column contains the titles of alignment blocks. The second column corresponds to the names of the sequences of
the query assembly. The following three columns show the length of a sequence, the starting and the ending positions of
an alignment block accordingly. The remaining columns correspond to the sequences, lengths, and mapping positions of
an alignment block for the target assembly.

A file named _stats.txt_ looks like this:
```
        Query           Target
cc      1               1           
useqs   1               4           

seqs    1               6           
tlen    5'078'954       5'004'408   
N50     5'078'954       2'964'866   
L50     1               1           

blocks  4               4           
tlen    4'901'252       4'868'864   
bcvg    0.965           0.973       
N50     2'984'830       2'964'847   
L50     1               1           

paths   1               1           
tlen    5'007'669       4'926'501   
N50     5'007'669       4'926'501   
L50     1               1
```
There are three columns: the first one contains the titles of various statistics, the remaining two show the values
of these statistics for the _Query_ and the _Target_ assemblies accordingly. Here is the description of the statistics:

* __cc__ – the number of connected components in an assembly graph. Note that even if two complementary strands are
separated from each other, they are assumed to represent one component. Thus, although the graph built by Canu consists
of two separated strands, the number of connected components is equal to 1.
* __useqs__ – the number of unique sequences in an assembly graph. This number is calculated as the difference between
the total number of sequences and the number of sequences that represent repeats.
* __seqs__ – the total number of sequences in an assembly.
* __blocks__ – the total number of alignment blocks between two assemblies.
* __bcvg__ – blocks coverage. Calculated as the blocks total length divided by the sequences total length.
* __paths__ – the number of synteny paths shared between the assemblies.

Each of the three groups (seqs, blocks, paths) contains the statistics named _tlen_ (total length), _N50_, _L50_ that
can be used to estimate the contiguity of the corresponding sequences.

# Tuning alignment parameters

To find an alignment between two assemblies, _Asgan_ utilizes _minimap2_. By default, _minimap2_ is
used with the _asm10_ preset. If two species diverge much (sequence divergence >10%), _minimap2_
will not find any alignments between them. If your datasets diverge much, use either _map-pb_ or _map-ont_ preset
using _--minimap-preset_ argument.

# WABI Supplementary

https://zenodo.org/record/3198701
