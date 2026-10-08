from pathlib import Path
import subprocess,os,json,zipfile,tomllib
root=Path(__file__).resolve().parents[1]
workspace=root
output=root/'validation/wheels';output.mkdir(exist_ok=True)
original=root
python=original/'.venv/bin/python'
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
results=[]
for repo in sorted(workspace.glob('LLM-*')):
 if not (repo/'pyproject.toml').is_file():continue
 spec=tomllib.loads((repo/'pyproject.toml').read_text())
 result=subprocess.run([str(python),'-c',f'import setuptools.build_meta as b; b.build_wheel({str(output)!r})'],cwd=repo,env=env,capture_output=True,text=True)
 (root/'validation'/f'{repo.name}-build.log').write_text(result.stdout+result.stderr)
 assert result.returncode==0,(repo,result.stderr)
 wheel=next(output.glob(spec['project']['name'].replace('-','_')+'-*.whl'))
 with zipfile.ZipFile(wheel) as archive:
  names=archive.namelist()
  assert not any(n.startswith(('src/','tests/','data/','checkpoints/','exports/')) for n in names),repo
  metadata=archive.read(next(n for n in names if n.endswith('/METADATA'))).decode()
  assert 'Version: 0.1.0' in metadata
  if spec['project'].get('scripts'):
   entries=archive.read(next(n for n in names if n.endswith('/entry_points.txt'))).decode()
   for name in spec['project']['scripts']:assert name in entries
 results.append({'repository':repo.name,'wheel':wheel.name,'success':True,'installed':False})
(root/'validation/package-builds.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
