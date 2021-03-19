import sys
import io
import gzip
import copy


def main():

    # Command line arguments
    file_path = sys.argv[1]
    pr_lambda = float(sys.argv[2])
    pr_tau = float(sys.argv[3])

    # Load data structures
    data = load(file_path)

    page_index = data[0]
    adj_list = data[1]

    # Do pagerank
    pr = pagerank(page_index, adj_list, pr_lambda, pr_tau)

    # Write outputs
    top_k_links(50, file_path)
    top_k_pageranks(50, pr, page_index)


"""
@params - page_index - indexed dictionary of unique pages
@params - adj_list - adjacency list of pages -> links
@params - pr_lambda - lambda value for pagerank algorithm
@params - pr_tau - tau value for pagerank algorithm

Calculation of pagerank values for the set of pages
"""
def pagerank(page_index, adj_list, pr_lambda, pr_tau):

    num_pages = len(page_index)

    i = [float(0)] * num_pages
    r = [float(0)] * num_pages

    # Populate i with equally shared pagerank
    for n in range(num_pages):
        i[n] = (1.0 / float(num_pages))

    # Main loop
    while(1):

        # Random selection values
        for n in range(num_pages):
            r[n] = pr_lambda / float(num_pages)

        # Accumulator to improve complexity
        accumulated = 0.0

        # Loop through pages
        for n in range(num_pages):
            q_list = adj_list[n]

            # Loop through links in a page
            if(len(q_list) > 0):
                for link in q_list:
                    r[link] = (r[link] + (((1.0 - pr_lambda) * (i[n])) / len(q_list)))
            else:
                accumulated += (((1.0 - pr_lambda) * (i[n])) / num_pages)

        # Account for rank sinks
        for n in range(num_pages):
            r[n] = r[n] + (accumulated)

        # Convergence check
        if(pr_tau > calculate_l1_norm(i, r)):
            break
        else:
            i = copy.deepcopy(r)

    return r


"""
@params - l1, l2 - the two lists to calculate the norm of
"""
def calculate_l1_norm(list1, list2):

    difference = []
    total = 0
    if(len(list1) == len(list2)):
        for n in range(len(list1)):
            difference.append(abs(list1[n] - list2[n]))
        total = sum(difference)
    return total


"""
@params - file path of gzipped file to parse into data structures

Takes in input file as string, genereates indexed list of unique pages
and adjacency list
"""
def load(file_path):

    page_index = {}
    pageset = set(())

    # Make page index(set used on the side for faster contains() checks)
    with gzip.open(file_path, 'rt') as gz:
        for line in gz:
            lines = format_lines(line)

            for page in lines:
                if page not in pageset:
                    page_index[page] = len(page_index)
                pageset.add(page)

    # Construct List of empty lists for adjacency list
    adj_list = []
    for i in range(len(page_index)):
        adj_list.append([])

    # Populate adj list
    with gzip.open(file_path, 'rt') as gz2:
        for line in gz2:
            lines = format_lines(line)

            source = lines[0]
            target = lines[1]

            adj_list[page_index[source]].append(page_index[target])

    return [page_index, adj_list]


"""
@param - k - number of top links to print
@param - file_path - file path of gzipped file to get info from

Generates list of top k most common inlinks. In English, generates a frequency
list of files that are most linked to

Generates and returns a file 'inlinks.txt'
"""
def top_k_links(k, file_path):
    inlinks = {}

    with gzip.open(file_path, 'rt') as gz:
        for line in gz:
            lines = format_lines(line)

            source = lines[0]
            target = lines[1]

            if(inlinks.get(target) is None):
                inlinks[target] = 1
            else:
                inlinks[target] = inlinks[target] + 1

    values = inlinks.items()
    sorted_list = sorted(values, key=lambda freq: freq[1], reverse=True)

    top_k = sorted_list[:k]

    file_print(top_k, 'inlinks.txt')


"""
@params - k - number of lines to output
@params - pr - list of pagerank values (unsorted)
"""
def top_k_pageranks(k, pr, pr_index):

    # Create mapping of indices to pagerank values
    pagerank_map = {}
    for page in pr_index:
        pagerank_map[page] = pr[pr_index.get(page)]

    values = pagerank_map.items()
    sorted_list = sorted(values, key=lambda freq: freq[1], reverse=True)

    top_k = sorted_list[:k]

    file_print(top_k, 'pagerank.txt')


"""
@params - Input line (string)
@return - List of pages on inputted line (list)

Takes in a line (one line of links.srt.gz file), removes the newline
character from the end, and splits it on tab
"""
def format_lines(line):
    line = line.removesuffix('\n')
    lines = line.split('\t')

    return lines


"""
@params - list - list to print
@params - filename - file name to print to

Prints the inputted list to the inputted file, formatted
according to the project specifications
"""
def file_print(list, filename):

    with open(filename, 'w') as fp:
        count = 1
        for key in list:
            fp.write(f"{key[0]:<35}{count:<4}{key[1]:>4}\n")
            count += 1

if __name__ == '__main__':
    main()
