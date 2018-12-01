def create_wire(x1, y1, x2, y2, w, layer):
    s = '<wire x1="' + str(x1)
    s += '" y1="' + str(y1)
    s += '" x2="' + str(x2)
    s += '" y2="' + str(y2)
    s += '" width="' + str(w)
    s += '" layer="' + str(layer) + '"/>\n'
    return s


def create_wires(x_neg, x_pos, y_neg, y_pos, lw, layer):
    s = create_wire(x_neg, y_pos, x_pos, y_pos, lw, layer)
    s += create_wire(x_pos, y_pos, x_pos, y_neg, lw, layer)
    s += create_wire(x_pos, y_neg, x_neg, y_neg, lw, layer)
    s += create_wire(x_neg, y_neg, x_neg, y_pos, lw, layer)
    return s


def create_pin(nm, x, y, side):
    s = '<pin name="' + str(nm)
    s += '" x="' + str(x)
    s += '" y="' + str(y)
    if side == "right":
        s += '" length="middle"/>\n'
    else:
        s += '" length="middle" rot="R180"/>\n'
    return s


def create_connect(nm, pins):
    s = '<connect gate="A" pin="' + str(nm)
    s += '" pad="' + " ".join(pins)
    s += '"/>\n'
    return s


def create_xml(l_grp, r_grp, left, right, name, template, pin_map):
    max_pins = max(left, right)

    # TODO:: use max_pins to find height / width values
    height = 100.0
    width = 45.0
    lw = 0.41
    layer = 94

    l_spacing = height / (left + 1)
    r_spacing = height / (right + 1)

    x_neg = width / 2.
    x_pos = -width / 2.
    y_pos = height / 2.
    y_neg = - height / 2.

    symbol_ind = template.find("<symbols>")
    xml = template[: symbol_ind + len("<symbols>")]
    xml += '<symbol name="' + name + '">\n'
    xml += create_wires(x_neg, x_pos, y_neg, y_pos, lw, layer)

    connections = "\n"
    y = y_pos - l_spacing
    for g in l_grp:
        xml += create_pin(g.name, x_neg, y, g.side)
        connections += create_connect(g.name, pin_map[g.name])
        y -= l_spacing

    y = y_pos - r_spacing
    for g in r_grp:
        xml += create_pin(g.name, x_pos, y, g.side)
        connections += create_connect(g.name, pin_map[g.name])
        y -= r_spacing

    xml += '</symbol>\n'
    xml += '</symbols>\n'
    xml += '<devicesets>\n'
    xml += '<deviceset name="' + name + '" prefix="U">\n'
    xml += '<description>MCU</description>\n'
    xml += '<gates>\n'
    xml += '<gate name="A" symbol="' + name + '" x="0" y="0"/>\n'
    xml += '</gates>\n'
    xml += '<devices>\n'
    xml += '<device name="" package="QFP80P1600X1600X120-64N">\n'
    xml += '<connects>\n'
    # xml += connections

    end_connects = template.index("</connects>")
    xml += template[end_connects:]

    return xml
