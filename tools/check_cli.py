from pathlib import Path
import json,subprocess,os,sys
root=Path(__file__).resolve().parents[1]
workspace=root.parent
(root/'validation').mkdir(parents=True,exist_ok=True)
catalog=json.loads((root/'artifact-catalog/catalog.json').read_text())
original=root
mapping=json.loads((root/'documentation/migration/module-mapping.json').read_text())
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['CUDA_VISIBLE_DEVICES']=''
env['PYTHONPATH']=os.pathsep.join(str(p/'src') for p in workspace.glob('LLM-*') if p.name!='LLM-From-Scratch')
results=[]
for name,module in mapping['entry_points'].items():
 python=original/('.venv-specialist' if module.startswith('llm_specialist') else '.venv')/'bin/python'
 result=subprocess.run([str(python),'-m',module,'--help'],cwd='/tmp',env=env,capture_output=True,text=True,timeout=30)
 assert result.returncode==0,(module,result.stderr)
 results.append({'module':module,'help_passed':True})
(root/'validation/cli-help.json').write_text(json.dumps(results,indent=2)+'\n')
print(f'{len(results)} packaged CLI help commands passed outside repository roots.')
