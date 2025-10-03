#!/usr/bin/python3
import sys,os,os.path,argparse,subprocess,json,shutil,collections,re

##########################################################################
##########################################################################

Version=collections.namedtuple('Version','major minor')

INTERESTING_TYPESCRIPT_VERSIONS=[
    Version(major=4,minor=9),
    Version(major=5,minor=0),
    Version(major=5,minor=1),
    Version(major=5,minor=2),
    Version(major=5,minor=3),
    Version(major=5,minor=4),
    Version(major=5,minor=5),
    Version(major=5,minor=6),
    Version(major=5,minor=7),
    Version(major=5,minor=8),
    Version(major=5,minor=9),
]    

##########################################################################
##########################################################################

g_use_shell=False

##########################################################################
##########################################################################

def get_version(lib_name):
    ls_j=json.loads(subprocess.check_output(['npm','ls','--json',lib_name],encoding='utf-8',shell=g_use_shell))

    assert isinstance(ls_j,dict)
    assert 'dependencies' in ls_j
    assert lib_name in ls_j['dependencies']
    assert 'version' in ls_j['dependencies'][lib_name]

    return ls_j['dependencies'][lib_name]['version']

##########################################################################
##########################################################################

def main2(options):
    if os.name=='nt':
        os.putenv('ComSpec',os.path.join(os.getenv('windir'),'system32\\cmd.exe'))
        # os.putenv('NO_COLOR','1') # doesn't seem to have an effect
        global g_use_shell
        g_use_shell=True
    
    node_version=subprocess.check_output(['node','--version'],encoding='utf-8').strip()

    print('Node version: "%s"'%node_version)
    m=re.match(r'''v(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)$''',node_version)
    assert m is not None
    node_version=Version(int(m.group('major')),int(m.group('minor')))

    if not os.path.isdir(options.output_folder):
        os.makedirs(options.output_folder)
    
    for ts_version in INTERESTING_TYPESCRIPT_VERSIONS:
        with open('package.json','rt',encoding='utf-8') as f:
            package_j=json.load(f)

        assert isinstance(package_j,dict)
        assert 'devDependencies' in package_j
        
        assert 'typescript' in package_j['devDependencies']
        package_j['devDependencies']['typescript']='~%d.%d.0'%(ts_version.major,ts_version.minor)

        assert '@types/node' in package_j['devDependencies']
        package_j['devDependencies']['@types/node']='~%d.0.0'%(node_version.major)

        print(80*'=')
        print()
        print('=== Requesting TS version: %s'%package_j['devDependencies']['typescript'])
        print('=== Requesting Node version: %s'%package_j['devDependencies']['@types/node'])

        with open('package.json','wt',encoding='utf-8') as f:
            json.dump(package_j,f,indent=4*' ')

        if os.path.isfile('package-lock.json'): os.unlink('package-lock.json')
        if os.path.isdir('node_modules'): shutil.rmtree('node_modules')
        subprocess.run(['npm','install','--no-color'],check=True,shell=g_use_shell)

        got_ts_version=get_version('typescript')
        print('Got TS version: %s'%got_ts_version)
        print('Got @types/node version: %s'%get_version('@types/node'))

        compile_result=subprocess.run(['npm','run','compile'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=g_use_shell)
        print('=== Compile result: %d'%compile_result.returncode)

        with open(os.path.join(options.output_folder,'%s.txt'%got_ts_version),
                  'wb') as f:
            f.write(compile_result.stdout)

##########################################################################
##########################################################################

def main(argv):
    parser=argparse.ArgumentParser()

    parser.add_argument('-o',dest='output_folder',default='./try_result',metavar='FOLDER',help='''write output files to %(metavar)s, creating if required. Default: %(default)s''')

    main2(parser.parse_args(argv))

##########################################################################
##########################################################################

if __name__=='__main__': main(sys.argv[1:])
