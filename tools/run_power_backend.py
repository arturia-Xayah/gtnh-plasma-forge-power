#!/usr/bin/env python3
"""Run a power-control test fixture in a new disposable dedicated GTNH server."""
import argparse,json,shutil,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,required=True);p.add_argument('--java',type=Path,required=True);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--run-dir',type=Path,required=True);p.add_argument('--suite',choices=['fusion','forge'],required=True);a=p.parse_args()
source=a.pack.resolve();target=a.run_dir.resolve()
if target.exists() or source==target or source in target.parents:p.error('Use a new directory outside the source pack')
target.mkdir(parents=True);(target/'mods').mkdir()
for q in (source/'mods').iterdir():
 if any(n in q.name.lower() for n in ['plasmaforgepower','structureterminal','aeoptimizer','aeorderoptimizer','aeorderbench']):continue
 (target/'mods'/q.name).symlink_to(q,target_is_directory=q.is_dir())
for n in ['config','scripts','serverutilities','blueprints']:
 if (source/n).is_dir():shutil.copytree(source/n,target/n)
for n in ['libraries','nestedmods']:
 if (source/n).is_dir():(target/n).symlink_to(source/n,target_is_directory=True)
for q in source.iterdir():
 if q.is_file() and (q.suffix=='.jar' or q.name=='java9args.txt'):shutil.copy2(q,target/q.name)
shutil.copy2(a.fixture,target/'mods/plasmaforgepower-tests.jar')
(target/'eula.txt').write_text('eula=true\n');(target/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=0\nonline-mode=false\nlevel-name=forge-power-validation\nlevel-type=FLAT\ngenerator-settings=2;7,2x3,2;1;\ngenerate-structures=false\nspawn-protection=0\nview-distance=3\nallow-nether=false\nspawn-monsters=false\nspawn-animals=false\nmax-tick-time=120000\n')
flag='-Dplasmaforgepower.fusionTests=true' if a.suite=='fusion' else '-Dplasmaforgepower.tests=true'
cmd=[str(a.java.resolve()),'-Xms1G','-Xmx6G','-XX:+UseG1GC',flag,'-Djava.awt.headless=true','-Duser.language=en','@java9args.txt','-jar','lwjgl3ify-forgePatches.jar','nogui']
with (target/'test-server.log').open('w') as out:
 proc=subprocess.Popen(cmd,cwd=target,stdout=out,stderr=subprocess.STDOUT);deadline=time.monotonic()+1200
 while proc.poll() is None:
  time.sleep(5)
  if time.monotonic()>deadline:proc.terminate();proc.wait(timeout=30);raise SystemExit('Server exceeded 20 minute limit')
report=target/('fusion-power-tests.json' if a.suite=='fusion' else 'forge-power-tests.json')
if not report.exists():raise SystemExit('Missing report: '+str(target/'test-server.log'))
d=json.loads(report.read_text());print(json.dumps({'exit':proc.returncode,'passed':d.get('passed'),'cases':len(d.get('tests',[])),'report':str(report)}))
if proc.returncode or not d.get('passed'):raise SystemExit(1)
