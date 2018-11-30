import re
import sys
import create_xml as cx


class PortType:
    def __init__(self, name, desc):
        self.desc = desc
        self.name = name
        self.side = None
        self.pin_type = None
        self.size = 1
        if "vector" in desc:
            matches = re.findall(r'(\d+)', desc)
            if len(matches) == 2:
                lrg = max(int(matches[0]), int(matches[1]))
                sm = min(int(matches[0]), int(matches[1]))
                self.size = lrg - sm + 1
        if "inout" in desc:
            self.pin_type = "inout"
        elif "linkage" in desc:
            self.pin_type = "power"
            self.side = "right"
        elif "buffer" in desc:
            self.pin_type = "buffer"
        elif "out" in desc:
            self.pin_type = "out"
            self.side = "right"
        elif "in" in desc:
            self.pin_type = "in"
            self.side = "left"


def get_port_txt(txt, start_regex):
    it = re.finditer(start_regex, s, re.IGNORECASE)
    begin_index = next(it).end()
    end = begin_index + 1
    open_parentheses = 1
    while open_parentheses > 0:
        if txt[end] == "(":
            open_parentheses += 1
        elif txt[end] == ")":
            open_parentheses -= 1
        end += 1
    return txt[begin_index: end]


def get_map(data, start_regex, end_regex):
    first = last = 0
    for i, line in enumerate(data):
        if len(re.findall(start_regex, line)) > 0:
            first = i + 1
            break
    for j, line in enumerate(data[first:]):
        if len(re.findall(end_regex, line)) > 0:
            last = j + first + 1
            break
    return data[first: last]


def sort_ports(groups):
    left_count = right_count = 0
    left_grp = []
    right_grp = []

    for g in groups:
        if g.pin_type == "in":
            left_count += 1
            left_grp.append(g)
        elif g.pin_type == "out":
            right_count += 1
            right_grp.append(g)
        elif g.pin_type == "power":
            right_count += 1
            right_grp.append(g)
        elif g.pin_type == "inout" or g.pin_type == "buffer":
            if left_count >= right_count:
                right_count += 1
                g.side = "right"
                right_grp.append(g)
            else:
                left_count += 1
                g.side = "left"
                left_grp.append(g)

    sorted_right = []
    for g in right_grp:
        if "VCC" in g.name:
            sorted_right.append(g)
    for g in right_grp:
        if "GND" not in g.name and "VCC" not in g.name:
            sorted_right.append(g)
    for g in right_grp:
        if "GND" in g.name:
            sorted_right.append(g)

    return left_grp, sorted_right, left_count, right_count


if __name__ == "__main__":

    # Read the data file from command line argument
    nm = sys.argv[1] if len(sys.argv) > 1 else "bsdl_files/ATMEGA128.bsdl"
    with open(nm, 'r') as f:
        data = f.readlines()
    s = "\n".join(data)
    lbr_template = './TemplateEagleWithPackage.lbr'

    # Get port description
    port_txt = get_port_txt(s, r'(\bport\b\s*\()')
    port_txt = port_txt.split("\n")
    groups = []
    for line in port_txt:
        if "--" not in line and ":" in line:
            k, v = line.split(":")
            k = k.replace('"', "").strip()
            v = v.replace(";", "").strip()
            g = PortType(k, v)
            groups.append(g)

    """
    # Show Port Descriptions
    for g in groups:
        print(g.name, g.desc, g.size, g.pin_type)
    """

    # Get mapping of ports to pin(s)
    map_txt = get_map(data, r'(\bPIN_MAP_STRING\b\ *\:\=)', r'(.*\;)')
    pin_map = dict()
    for line in map_txt:
        if line.strip() != "":
            if ":" in line:
                k, v = line.split(":")
                k = k.replace('"', "").replace("'", "")
                k = k.strip()
                v = v.replace("(", "").replace(")", "").replace(";", "")
                v = v.replace("&", "").replace('"', "").replace("'", "")
                v = v.split(",")
                pin_map[k] = [pin.strip() for pin in v if pin.strip() != ""]
                prev = k
            else:
                values = line.replace('"', "").replace("'", "").replace(";", "")
                values = values.replace("(", "").replace(")", "")
                values = values.replace("&", "").split(",")
                pin_map[prev] += [pin.strip() for pin in values if pin.strip() != ""]

    """
    # Show Port-to-Pin Mappings
    for k in pin_map:
        print(k, pin_map[k])
    """

    with open(lbr_template, 'r') as f:
        t = f.readlines()
    template = "".join(t)

    # Find name of device
    matches = re.findall(r'(\bentity\b\ +\w+\b is\b)', s, re.IGNORECASE)
    device = matches[0][6:-3].strip()

    # Sort and create HTML
    l_grp, r_grp, l_count, r_count = sort_ports(groups)
    lbr = cx.create_xml(l_grp, r_grp, l_count, r_count, device, template, pin_map)

    # Write out to file
    lbr_nm = "bsdl_files/" + device + ".lbr"
    lbr_file = open(lbr_nm, 'w')
    lbr_file.write(lbr)
    lbr_file.close()
