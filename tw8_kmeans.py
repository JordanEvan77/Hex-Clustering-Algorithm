import pandas as pd
import math
import random

DATA = 'C:/Users/jorda/OneDrive/Desktop/PyCharm Community Edition 2021.2.2/5062/TW8/'


def rgb_distance(color1, color2):
    r1 = color1 >> 16
    g1 = color1 >> 8 & 0xff
    b1 = color1 & 0xff
    r2 = color2 >> 16
    g2 = color2 >> 8 & 0xff
    b2 = color2 & 0xff
    dist1 = math.sqrt(((r1 - r2) ** 2) + ((g1 - g2) ** 2) + ((b1 - b2) ** 2))
    return dist1


def rgb_center(colors):
    r1, b1, g1 = [], [], []
    for col in colors:
        r1.append(col >> 16)
        g1.append(col >> 8 & 0xff)
        b1.append(col & 0xff)
    r1 = sum(r1) // len(r1)
    g1 = sum(g1) // len(g1)
    b1 = sum(b1) // len(b1)
    color = r1 << 16 | g1 << 8 | b1  # why is this giving me an error?
    return color

class Color(object):
    """
    Adpated from Guttag Fig. 23.2, Example class
    This one is all about 24-bit RGB colors.
    Stores an RGB color and and optional name, knows about distance
    and has a static method to compute a centroid.
    """
    def centroid(colors):
        """
        Compute a centroid for a list of Color objects.
        :param colors: list of Colors
        :return:       the average Color of colors
        #>>> Colors.centroid([Color(0), Color(0xffffff)])
        #0x7f7f7f: 0x0x7f7f7f
        """
        rgbs = [color.rgb for color in colors]
        center = rgb_center(rgbs)  # why wont it recognize?
        return Color(center)

    def __init__(self, rgb, name=None):
        if name is None:
            name = '#{:06x}'.format(rgb)
        self.name = name
        self.rgb = rgb


    def distance(self, other):
        return rgb_distance(self.rgb, other.rgb)  # why wont it recognize?

    def __str__(self):
        return '{}: 0x{:06x}'.format(self.name, self.rgb)

    def __repr__(self):
        return "Color(0x{:06x}, '{}')".format(self.rgb, self.name)

def get_data(file_name):
    colors = pd.read_csv(DATA + file_name)  # can use usecols=[1]
    #print(colors)
    list_color = []
    for index, row in colors.iterrows():  # not working
        #print(row)
        #print(row['Name'], int(row['Hex'][1:], 16))
        list_color.append(Color(int(row['Hex'][1:], 16), row['Name']))
    #print('lister', list_color)
    return list_color


class Cluster(object):
    """
    Adapted from Guttag Fig. 23.3, except this one is a Cluster of Colors.
    """

    def __init__(self, colors):
        self.colors = colors
        self.centroid = Color.centroid(self.colors)

    def update(self, colors):
        """Assume examples is a non-empty list of Colors
           Replace examples; return amount centroid has changed"""
        old_centroid = self.centroid
        self.colors = colors
        self.centroid = Color.centroid(self.colors)
        return old_centroid.distance(self.centroid)

    def get_centroid(self):
        return self.centroid

    def to_html(self):
        """Produce an html table with the cluster's colors."""
        color_map = {color.rgb: color for color in self.colors}
        colors = [color_map[color] for color in sorted(color_map)]
        html = ['<table><tbody>']
        for color in self.colors:
            html.append('<tr style="background:#{:06x}">'.format(color.rgb))
            html.append('<td>{}</td><td>0x{:06x}</td>'.format(color.name, color.rgb))
            html.append('</tr>')
        html.append('</tbody></table>')
        return '\n'.join(html)

    def __str__(self):
        color_map = {color.rgb: color for color in self.colors}
        colors = [str(color_map[color]) for color in sorted(color_map)]
        return 'Cluster with centroid {} contains:\n{}'.format(self.centroid, ', '.join(colors))

def kmeans(colors, k, verbose=False):
    """
    Adapted from Guttag, Figure 23.5
    :param colors:   list of colors
    :param k:        number of clusters to gather
    :param verbose:  print out the story as we go if True
    :return:         clusters of colors
    """
    #Then change it such that it uses our Color and Cluster classes correctly
    # to do its job of iteratively refining the clusters of Colors.
    # Get k randomly chosen initial centroids, create cluster for each
    initialCentroids = random.sample(colors, k)
    clusters = []
    for e in initialCentroids:
        clusters.append(Cluster([e]))
        #print('print', clusters)

    # Iterate until centroids do not change
    converged = False
    numIterations = 0
    while not converged:
        numIterations += 1
        # Create a list containing k distinct empty lists
        newClusters = []
        for i in range(k):
            newClusters.append([])

        # Associate each example with closest centroid
        # colors = [Color(0x020202), Color(0x998877), Color(0xbadbad), Color(0xffffff, 'white')]
        # print(Color.centroid(colors))
        # a = Color(0x959989)
        # b = Color(0x020202)
        # c = Color(0x998877)
        # d = Color(0xbadbad)
        # print(a)
        # print(a.distance(b))
        # print(a.distance(c))
        # print(a.distance(d))
        for e in colors:
            #print('loop', Color(0x020202))
            # Find the centroid closest to e
            #smallestDistance = e.distance(clusters[0].getCentroid())
            # centroid1 = Color.centroid(colors)  # was working, not the point though
            centroid1 = (clusters[0].get_centroid())
            smallestDistance = e.distance(centroid1)
            index = 0
            for i in range(1, k):
                # distance = e.distance(colors[i]) # was working, but not the point
                distance = e.distance(clusters[i].get_centroid())
                if distance < smallestDistance:
                    smallestDistance = distance
                    index = i
            # Add e to the list of examples for appropriate cluster
            newClusters[index].append(e)

        for c in newClusters:  # Avoid having empty clusters
            if len(c) == 0:
                raise ValueError('Empty Cluster')

        # Update each cluster; check if a centroid has changed
        converged = True
        for i in range(k):
            if clusters[i].update(newClusters[i]) > 0.0:
                converged = False
        if verbose:
            print('Iteration #' + str(numIterations))
            for c in clusters:
                print(c)
            print('')  # add blank line
    return clusters




def kmeans_to_html(input_data_file, output_html_file, k, verbose=False):
    """
    Process data file of colors via k-means clustering into an html file
    with a table of the various color clusters.
    :param input_data_file:   colors csv file with columns 'Hex' and 'Name'
    :param output_html_file:  output html file of the resulting clusters
    :param k:                 number of clusters to make
    """
    colors = get_data(input_data_file)
    result = kmeans(colors, k, verbose=verbose)
    tables = [cluster.to_html() for cluster in result]
    html_side_by_side_table(output_html_file, tables)


def html_side_by_side_table(html_filename, contents):
    """
    Make an html table of one row whose cells contain given contents.
    :param html_filename:  output filename
    :param contents:       html fragments to put into each cell
    """
    html = ['<table><tbody><tr>']
    for item in contents:
        html.append('<td>{}</td>'.format(item))
    html.append('</tr></tbody></table>')
    file_contents = '\n'.join(html)
    with open(('%s/%s') % (DATA,html_filename), 'w') as f:
        f.write(file_contents)


if __name__ == '__main__':
    kmeans_to_html('X11colors.csv', 'tw8_kmeans.html', k=6, verbose=False)

# if __name__ == '__main__':
#     colors = [Color(0x020202), Color(0x998877), Color(0xbadbad), Color(0xffffff, 'white')]
#     print(Color.centroid(colors))
#     a = Color(0x959989)
#     b = Color(0x020202)
#     c = Color(0x998877)
#     d = Color(0xbadbad)
#     print(a)
#     print(a.distance(b))
#     print(a.distance(c))
#     print(a.distance(d))
#     get_data('X11colors.csv')[21]  # Color(0x00008b, 'Dark Blue') appears to be working
#     cluster1 = Cluster(colors)
#     print(cluster1)
#     print(cluster1.to_html())  # take the given text, and use the "embed" option in the text box
    colors = get_data('X11colors.csv')
    result = kmeans(colors, k=5, verbose=True)
    print(result)
    kmeans_to_html('X11colors.csv', 'tw8_kmeans.html', k=6, verbose=False)  # final statement
    # average iterations, 10


# The iteration count is different each time because the cluster type and load is different each
# time as well. So the centroids are different and must be itterated through to find the best one.