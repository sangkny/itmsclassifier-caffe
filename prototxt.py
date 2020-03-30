# 2017.12.16 by xiaohang
from collections import OrderedDict
import caffe.proto.caffe_pb2 as caffe_pb2

def parse_caffemodel(caffemodel):
    model = caffe_pb2.NetParameter()
    print('Loading caffemodel:{}'.format(caffemodel))

    with open(caffemodel, 'rb') as fp:
        model.ParseFromString(fp.read())

    return model


def parse_prototxt(protofile):
    def line_type(line):
        if line.find(':') >= 0:
            return 0
        elif line.find('{') >= 0:
            return 1
        return -1

    def parse_block(fp):
        block = OrderedDict()
        line = fp.readline().strip()
        while line != '}':
            ltype = line_type(line)
            if ltype == 0: # key: value
                #print line
                line = line.split('#')[0]
                key, value = line.split(':')
                key = key.strip()
                value = value.strip().strip('"')
                # if block.has_key(key):    # python 2.x
                if key in block:            # python version 3.x
                    if type(block[key]) == list:
                        block[key].append(value)
                    else:
                        block[key] = [block[key], value]
                else:
                    block[key] = value
            elif ltype == 1: # blockname {
                key = line.split('{')[0].strip()
                sub_block = parse_block(fp)
                block[key] = sub_block
            line = fp.readline().strip()
            line = line.split('#')[0]
        return block

    fp = open(protofile, 'r')
    props = OrderedDict()
    layers = []
    line = fp.readline()
    while line != '':
        line = line.strip().split('#')[0]
        if line == '':
            line = fp.readline()
            continue
        ltype = line_type(line)
        if ltype == 0: # key: value
            key, value = line.split(':')
            key = key.strip()
            value = value.strip().strip('"')
            #if props.has_key(key): # python version 2.x
            if key in props:        # python version 3.x by sangkny 2019. 11. 15
               if type(props[key]) == list:
                   props[key].append(value)
               else:
                   props[key] = [props[key], value]
            else:
                props[key] = value
        elif ltype == 1: # blockname {
            key = line.split('{')[0].strip()
            if key == 'layer':
                layer = parse_block(fp)
                layers.append(layer)
            else:
                props[key] = parse_block(fp)
        line = fp.readline()

    if len(layers) > 0:
        net_info = OrderedDict()
        net_info['props'] = props
        net_info['layers'] = layers
        return net_info
    else:
        return props

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def print_prototxt(net_info):
    # whether add double quote
    def format_value(value):
        #str = u'%s' % value
        #if str.isnumeric():
        if is_number(value):
            return value
        elif value in ['true', 'false', 'MAX', 'SUM', 'AVE', 'TRAIN', 'TEST', 'WARP', 'LINEAR', 'AREA', 'NEAREST', 'CUBIC', 'LANCZOS4', 'CENTER', 'LMDB']:
            return value
        else:
            return '\"%s\"' % value

    def print_block(block_info, prefix, indent):
        blanks = ''.join([' ']*indent)
        print('%s%s {' % (blanks, prefix))
        for key,value in block_info.items():
            if type(value) == OrderedDict:
                print_block(value, key, indent+4)
            elif type(value) == list:
                for v in value:
                    print('%s    %s: %s' % (blanks, key, format_value(v)))
            else:
                print('%s    %s: %s' % (blanks, key, format_value(value)))
        print('%s}' % blanks)
        
    props = net_info['props']
    layers = net_info['layers']
    print('name: \"%s\"' % props['name'])
    print('input: \"%s\"' % props['input'])
    print('input_dim: %s' % props['input_dim'][0])
    print('input_dim: %s' % props['input_dim'][1])
    print('input_dim: %s' % props['input_dim'][2])
    print('input_dim: %s' % props['input_dim'][3])
    print('')
    for layer in layers:
        print_block(layer, 'layer', 0)

def save_prototxt(net_info, protofile, region=True):
    fp = open(protofile, 'w')
    # whether add double quote
    def format_value(value):
        #str = u'%s' % value
        #if str.isnumeric():
        if is_number(value):
            return value
        elif value in ['true', 'false', 'MAX', 'SUM', 'AVE', 'TRAIN', 'TEST', 'WARP', 'LINEAR', 'AREA', 'NEAREST', 'CUBIC', 'LANCZOS4', 'CENTER', 'LMDB']:
            return value
        else:
            return '\"%s\"' % value

    def print_block(block_info, prefix, indent):
        blanks = ''.join([' ']*indent)
        #print >>fp, '%s%s {' % (blanks, prefix)
        print('%s%s {' % (blanks, prefix), file=fp)
        for key,value in block_info.items():
            if type(value) == OrderedDict:
                print_block(value, key, indent+4)
            elif type(value) == list:
                for v in value:
                    #print >> fp, '%s    %s: %s' % (blanks, key, format_value(v))
                    print('%s    %s: %s' % (blanks, key, format_value(v)), file=fp)
            else:
                print('%s    %s: %s' % (blanks, key, format_value(value)), file=fp)
        #print >> fp, '%s}' % blanks
        print('%s}' % blanks, file=fp)
        
    props = net_info['props']
    #print >> fp, 'name: \"%s\"' % props['name']        # python 2.x
    print('name: \"%s\"' % props['name'], file=fp)      # python 3.x by sangkny 2019. 11. 15
    #if props.has_key('input'):
    if 'input' in protofile:
        #print >> fp, 'input: \"%s\"' % props['input']  # python 2.x
        print('input: \"%s\"' % props['input'], file=fp)
    #if props.has_key('input_dim'):
    if 'input_dim' in props:
        # print >> fp, 'input_dim: %s' % props['input_dim'][0]
        # print >> fp, 'input_dim: %s' % props['input_dim'][1]
        # print >> fp, 'input_dim: %s' % props['input_dim'][2]
        # print >> fp, 'input_dim: %s' % props['input_dim'][3]
        print('input_dim: %s' % props['input_dim'][0], file=fp)
        print('input_dim: %s' % props['input_dim'][1], file=fp)
        print('input_dim: %s' % props['input_dim'][2], file=fp)
        print('input_dim: %s' % props['input_dim'][3], file=fp)
    #print >> fp, ''
    print('', file=fp)
    layers = net_info['layers']
    for layer in layers:
        if layer['type'] != 'Region' or region == True:
            print_block(layer, 'layer', 0)
    fp.close()

def parse_solver(solverfile):
    solver = OrderedDict()
    lines = open(solverfile).readlines()
    for line in lines:
        line = line.strip()
        if line[0] == '#':
            continue
        if line.find('#') >= 0:
            line = line.split('#')[0]
        items = line.split(':')
        key = items[0].strip()
        value = items[1].strip().strip('"')
        #if not solver.has_key(key):        # python 2.x
        if not key in solver:
            solver[key] = value
        elif not type(solver[key]) == list:
            solver[key] = [solver[key], value]
        else:
            solver[key].append(value)
    return solver


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: python prototxt.py model.prototxt')
        exit()

    import os
    filenameonly, extonly = os.path.splitext(os.path.abspath(sys.argv[1]))
    if 'prototxt' in extonly:
        net_info = parse_prototxt(sys.argv[1])
        print_prototxt(net_info)
        save_prototxt(net_info, filenameonly + '_tmp' + extonly)

    elif 'model' in extonly:
        net_info = parse_caffemodel(sys.argv[1])
        print(' printing the net_infomation\n')
        print(net_info)
    else:
        print('input file is not correct! please check this out again\n')
        exit(-1)
