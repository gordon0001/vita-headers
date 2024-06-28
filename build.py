import os
import glob


DEFAULT_BUILD_OUTDIR = 'build'
CURR_DIR = os.path.dirname(os.path.realpath(__file__))

def execute(cmd, force_print=False):
    with os.popen(cmd) as r:
        for line in iter(r.readline, ""):
            if os.environ.get('VERBOSE') or force_print:
                print(line)
        return r.close()

# usage: usage: vita-libs-gen-2 -yml=<nids_db.yml|nids_db_yml_dir> -output=<output_dir> [-cmake=<true|false>] [-ignore-stubname=<true|false>]
def vita_libs_gen(yml, out):
    cmd = os.environ.get('VITA_LIBS_GEN', 'vita-libs-gen')
    if execute('{} {} {}'.format(cmd, yml, out)):
        raise SystemExit(10)

def vita_libs_gen_2(yml, out):
    cmd = os.environ.get('VITA_LIBS_GEN_2', 'vita-libs-gen-2')
    if execute('{} -yml={} -output={} -cmake=false'.format(cmd, yml, out)):
        raise SystemExit(10)
        
def make(target):
    curr = os.getcwd()
    os.chdir(target)
    arch = os.environ.get('ARCH', '')
    if arch:
        arch = 'ARCH={}'.format(arch)
    if execute('make -j {}'.format(arch)):
        raise SystemExit(11)
    os.chdir(curr)

def make_install(target):
    curr = os.getcwd()
    os.chdir(target)
    if execute('make install'):
        raise SystemExit(12)
    os.chdir(curr)

def definition_check():
    return execute('python .travis.d/definition_check.py', force_print=True)

def definition_ordering(yml):
    return execute('bash .travis.d/definition_ordering.sh {}'.format(yml))

if __name__ == '__main__':
    import sys
    import shutil


    outdir = DEFAULT_BUILD_OUTDIR
    if len(sys.argv) >= 2:
        outdir = sys.argv[1]

    if os.environ.get('USE_LINT'):
        if definition_check():
            raise SystemExit(1)

        # Name sort is now handled by vita-nid-check
        # for yml in glob.glob(os.path.join(CURR_DIR, 'db', '**', '*.yml')):
        #     if definition_ordering(yml):
        #         raise SystemExit(2)

    if not os.environ.get('BYPASS_VITA_LIBS_GEN'):
        for yml in glob.glob(os.path.join(CURR_DIR, 'db', '**', '*.yml')):
            dirs, fn = (os.path.split(yml))
            _, ver = os.path.split(dirs)
            build_target = os.path.join(outdir, ver, fn)
            if os.path.exists(build_target):
                shutil.rmtree(build_target)
            os.makedirs(build_target)
            vita_libs_gen_2(yml, build_target)
            make(build_target)
            if not os.environ.get('BYPASS_INSTALL'):
                make_install(build_target)
