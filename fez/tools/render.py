import inspect, json, os, sys
import build
def render(tables, out):
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_template.py')).read()
    cells_src = '\n\n'.join(inspect.getsource(f) for f in (build.walk_parts, build.walk_keys, build.cells))
    lit = json.dumps(tables, sort_keys=True, separators=(',', ':'))
    # wrap long literal lines a bit for readability
    lit = lit.replace('},"', '},\n"').replace('{"cell"', '{\n"cell"')
    src = src.replace('__CELLS__', cells_src).replace('__TABLES__', lit)
    open(out, 'w').write(src)
if __name__ == '__main__':
    from load2 import load_all
    t = build.build_tables(load_all())
    render(t, sys.argv[1])
    print('wrote', sys.argv[1])
