"""Sorts a list of Color objects using a quick and dirty nearest
neighbor type of sort.   Works by converting to CIElab colorspace
and the Delta E method of calculating linear distance between colors
in the 3d colorspace.
"""
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

colors = list()


def _take_out(item, item_list):
    """the first argument is a list member, second is the list.
    function will remove the selected item from the list without
    needing to know its index"""
    for i, x in enumerate(item_list):
        if x == item:
            item_list.pop(i)
            break
    return item_list


def _sc(lab, labs):
    """given a lab color and a list of lab colors:
    attempts to sort colors in 'order' starting with the color given
    in the first argument -- not perfect"""
    size = len(labs)
    sorted_colors = []
    sorted_colors.insert(0, lab)
    for j in range(size - 1):
        labs = _take_out(sorted_colors[j], labs)
        sorted_colors.insert(j + 1, closest_color(sorted_colors[j], labs))
    return sorted_colors


def closest_color(lab, labs, d=False):
    """given a lab color and a list of lab colors:
    returns the color from the list closest to the color
    provided in the first argument.  unless d=True, in which
    case it returns the list of Delta E differences"""
    color_diffs = []
    for x in labs:
        color_diff = delta_e_cie2000(lab, x)
        if color_diff != 0:
            color_diffs.append((color_diff, x))
    if d:
        return color_diffs
    return min(color_diffs)[1]


def nearest_neighbor(labs):
    """given a list of lab colors, returns a dictionary
    containing each color and its nearest neighbor as
    key => value pairs"""
    neighbors = {}
    for lab in labs:
        neighbors.update({lab: closest_color(lab, labs)})
    return neighbors


def sanity_check(lab, theoretical):
    # sourcery skip: merge-list-append, move-assign
    """Before joining the neighborhood, I'll check to see if I'm closer to
    any member who's already in than another who's already in in front
    of me"""
    only_me = [lab]
    indices = []
    for neighbor in theoretical:
        diffs = closest_color(neighbor, theoretical, d=True)
        my_diff = closest_color(neighbor, only_me, d=True)
        my_diff, some_trash = my_diff.pop()
        for diff, member in diffs:
            master_index = theoretical.index(neighbor)
            if diff > my_diff and theoretical.index(member) > master_index:
                member_index = theoretical.index(member)
                indices.append(member_index)
        if indices:
            return min(indices)
        return 0


def check_and_sort(table):  # sourcery skip: hoist-statement-from-loop
    """handles the sorting of all the colors in the 'neighborhood'
    which is the dict created by the nearest_neighbor function"""
    global colors
    new_neighbors = []
    tick = 0
    for key, val in table.items():
        """If this isn't the first iteration, and neither myself nor my
         neighbor are in, I need to make sure someone else isn't closer
         before I go in"""
        if key not in new_neighbors and val not in new_neighbors and tick != 0:
            last_in = new_neighbors[-1]
            remaining = [tempvar for tempvar in colors if
                         tempvar not in new_neighbors]
            next_in = closest_color(last_in, remaining)

            if next_in not in new_neighbors:
                new_neighbors.append(next_in)
            """if my neighbor is already in, I should be in somewhere closeby
            but I need to make sure no one else is closer before I move in
            """
        elif val in new_neighbors and key not in new_neighbors:
            diffs = closest_color(val, colors, d=True)
            my_diff = 0
            for diff, lab in diffs:
                if lab == key:
                    my_diff = diff
            closer = []
            neighbor_index = new_neighbors.index(val)
            for diff, lab in diffs:
                if diff < my_diff:
                    offset = new_neighbors.index(lab)
                    if offset > neighbor_index:
                        closer = [lab]
            if closer:
                for member in closer:
                    offset = new_neighbors.index(member)
                    offset = offset - (offset - neighbor_index)
                    neighbor_index += 1
                    new_neighbors.remove(member)
                    new_index = sanity_check(member, new_neighbors)
                    if new_index:
                        new_neighbors.insert(new_index, member)
                    else:
                        new_neighbors.insert(offset, member)
                    closer.remove(member)
                if not closer:
                    new_index = sanity_check(key, new_neighbors)
                    if new_index:
                        new_neighbors.insert(new_index, key)
                    else:
                        new_neighbors.insert(neighbor_index + 1, key)
            else:
                new_index = sanity_check(key, new_neighbors)
                if new_index:
                    new_neighbors.insert(new_index, key)
                else:
                    new_neighbors.append(key)
            """If I'm not in by now, it's my turn to go in"""
        elif key not in new_neighbors:
            new_index = sanity_check(key, new_neighbors)
            if new_index:
                new_neighbors.insert(new_index, key)
            else:
                new_neighbors.append(key)
            """Next after me will always be my neighbor, unless he's already
             in, which means he's a closer neighbor to someone else than he
              is to me"""
        elif val not in new_neighbors:
            new_index = sanity_check(val, new_neighbors)
            if new_index:
                new_neighbors.insert(new_index, val)
            else:
                new_neighbors.append(val)
        tick += 1

    new_neighborhood = {}
    for data in new_neighbors:
        new_neighborhood.update({data: table.get(data)})
    return new_neighborhood


def sort_colors(input_colors):
    """takes a list of color objects as input and returns
    a sorted list of colors in hex-string format"""
    global colors
    for input_color in input_colors:
        red, green, blue = input_color.rgb()
        srgb = sRGBColor(red, green, blue, is_upscaled=True)
        color = convert_color(srgb, LabColor)
        colors.append(color)

    black = sRGBColor(0, 0, 0)
    black = convert_color(black, LabColor)

    bg_color = closest_color(black, colors)
    colors = _sc(bg_color, colors)
    neighborhood = nearest_neighbor(colors)
    next_neighborhood = check_and_sort(neighborhood)

    return_array = []

    for key1, value1 in next_neighborhood.items():
        key1 = convert_color(key1, sRGBColor)
        r, g, b = key1.get_upscaled_value_tuple()
        rhex, ghex, bhex = ["{:02x}".format(x) for x in (r, g, b)]
        return_array.append('#' + rhex + ghex + bhex)

    return return_array
