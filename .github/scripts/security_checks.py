"""Repository security checks. Python standard library only; no application imports."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

TOOLS = {'gitleaks/gitleaks': {'version': 'v8.30.1', 'url': 'https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz', 'sha256': '551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb', 'release': 'https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1', 'license': 'MIT', 'license_url': 'https://github.com/gitleaks/gitleaks/blob/master/LICENSE'}, 'google/osv-scanner': {'version': 'v2.7.0', 'url': 'https://github.com/google/osv-scanner/releases/download/v2.7.0/osv-scanner_linux_amd64', 'sha256': '160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b', 'release': 'https://github.com/google/osv-scanner/releases/tag/v2.7.0', 'license': 'Apache-2.0', 'license_url': 'https://github.com/google/osv-scanner/blob/main/LICENSE'}}

def command(args, cwd=None):
    return subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def git(*args):
    p = command(['git', *args])
    if p.returncode: raise RuntimeError('Git operation failed')
    return p.stdout.decode('utf-8')

def base_ref():
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text('utf-8'))
    value = event.get('pull_request', {}).get('base', {}).get('sha') or event.get('before')
    if value and re.fullmatch(r'[a-f0-9]{40}', value) and set(value) != {'0'}:
        git('cat-file', '-e', value + '^{commit}')
        return value
    return None

def install(name, folder):
    meta = TOOLS[name]
    with urllib.request.urlopen(meta['url'], timeout=90) as response: raw = response.read()
    if hashlib.sha256(raw).hexdigest() != meta['sha256']:
        raise RuntimeError('Scanner SHA-256 mismatch')
    archive = folder / 'download'
    archive.write_bytes(raw)
    executable = folder / ('gitleaks' if name == 'gitleaks/gitleaks' else 'osv-scanner')
    if name == 'gitleaks/gitleaks':
        with tarfile.open(archive, 'r:gz') as source:
            stream = source.extractfile('gitleaks')
            if stream is None: raise RuntimeError('Scanner executable missing')
            executable.write_bytes(stream.read())
    else: executable.write_bytes(raw)
    executable.chmod(0o700)
    return executable

def summary(text):
    print(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as out: out.write(text + '\n\n')

def secret_scan(full=False):
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp); exe = install('gitleaks/gitleaks', folder)
        config = folder / 'scanner.toml'; config.write_text('[extend]\nuseDefault = true\n', 'utf-8')
        ignore = folder / 'ignore'; ignore.write_text('', 'utf-8')
        report = folder / 'results.json'
        base = None if full else base_ref()
        args = [str(exe), 'git', '.', '--config', str(config), '--gitleaks-ignore-path', str(ignore),
                '--ignore-gitleaks-allow', '--redact=100', '--no-banner', '--report-format=json', '--report-path', str(report)]
        args += ['--log-opts=' + (base + '..HEAD' if base else '--all')]
        result = command(args)
        if result.returncode not in (0, 1) or not report.exists(): raise RuntimeError('Secret scanner failed')
        findings = json.loads(report.read_text('utf-8')) or []
        # Never publish scanner logs, matched lines, commit messages, or raw reports.
        summary(f'Secret scan ({"full history" if full else "incoming commits"}): {len(findings)} findings. Values are withheld.')
        if findings: raise RuntimeError('Potential secrets detected; inspect locally and rotate exposed credentials')

def tracked(root):
    p=command(['git','ls-files','-z'],cwd=root)
    if p.returncode: raise RuntimeError('Cannot enumerate tracked files')
    return [x for x in p.stdout.decode('utf-8').split('\0') if x]

def inventory(root, destination):
    """Add exact Gradle coordinates and recorded runtime inventories to lockfile scanning."""
    packages = set()
    for name in tracked(root):
        path = root / name
        if path.is_symlink() or not path.is_file(): continue
        if name.endswith(('.gradle','.gradle.kts')):
            for line in path.read_text('utf-8').splitlines():
                if line.lstrip().startswith('//'): continue
                for group, artifact, version in re.findall(r'''["']([\w.-]+):([\w.-]+):([\w.-]+)["']''',line):
                    if re.match(r'^\d',version): packages.add(('Maven',group+':'+artifact,version))
        if path.name in ('dependency-inventory.json','dependencies-inspected.json','runtime-components.json'):
            data=json.loads(path.read_text('utf-8-sig'))
            values=data if isinstance(data,list) else data.get('components',data.get('dependencies',[]))
            for item in values:
                if not isinstance(item,dict): continue
                if isinstance(item.get('module'),str) and len(item['module'].split(':'))==3:
                    group,artifact,version=item['module'].split(':'); packages.add(('Maven',group+':'+artifact,version))
                elif all(k in item for k in ('group','name','version')):
                    packages.add(('Maven',item['group']+':'+item['name'],str(item['version'])))
                elif all(k in item for k in ('name','version')):
                    packages.add(('PyPI',item['name'],str(item['version'])))
    data={'results':[{'packages':[{'package':{'ecosystem':e,'name':n,'version':v}} for e,n,v in sorted(packages)]}]}
    destination.write_text(json.dumps(data),'utf-8')
    return len(packages)

def osv_scan(exe, root, folder, label):
    custom = folder / (label+'-inventory.json'); count = inventory(root,custom)
    report = folder / (label+'-results.json')
    args=[str(exe),'scan','source','--recursive','--no-call-analysis=all','--format=json','--output-file',str(report)]
    if count: args+=['--lockfile','osv-scanner:'+str(custom)]
    for name in tracked(root):
        p=Path(name)
        if p.suffix=='.txt' and 'requirements' in p.name and p.name!='requirements.txt':
            args+=['--lockfile','requirements.txt:'+str(root/name)]
    args+=[str(root)]
    result=command(args,cwd=root)
    if result.returncode not in (0,1,128): raise RuntimeError('Dependency scanner failed')
    if result.returncode==128:
        summary('No supported exact package versions found; dependency coverage is limited.')
        return set()
    if not report.exists(): raise RuntimeError('Dependency scanner report missing')
    data=json.loads(report.read_text('utf-8')); findings=set(); total=0
    for source in data.get('results',[]):
        for entry in source.get('packages',[]):
            total+=1; package=entry.get('package',{})
            for advisory in entry.get('vulnerabilities',[]):
                findings.add((package.get('ecosystem',''),package.get('name',''),package.get('version',''),advisory['id']))
    summary(f'Dependency scan ({label}): {total} package entries, {len(findings)} affected package/version/advisory combinations.')
    return findings

def dependency_scan(full=False):
    with tempfile.TemporaryDirectory() as temp:
        folder=Path(temp); exe=install('google/osv-scanner',folder)
        current=osv_scan(exe,Path.cwd(),folder,'current')
        base=None if full else base_ref()
        previous=set()
        if base:
            old=folder/'base'
            git('worktree','add','--detach',str(old),base)
            try: previous=osv_scan(exe,old,folder,'base')
            finally: git('worktree','remove',str(old))
        added=current-previous
        summary(f'{len(current & previous)} existing findings retained for full-audit follow-up; {len(added)} findings in this check scope.')
        if added: raise RuntimeError('Vulnerable dependencies detected; review the full audit and Dependabot alerts')

def validate():
    base=base_ref()
    names=git('diff','--name-only','--diff-filter=ACMR',base,'HEAD').splitlines() if base else tracked(Path.cwd())
    checked=0
    for name in names:
        path=Path(name)
        if not path.is_file() or path.is_symlink(): continue
        if path.suffix=='.py': ast.parse(path.read_text('utf-8-sig'),filename=name); checked+=1
        elif path.suffix=='.json': json.loads(path.read_text('utf-8-sig')); checked+=1
        elif path.suffix=='.xml': ET.fromstring(path.read_bytes()); checked+=1
    summary(f'Changed-source syntax validation: {checked} Python, JSON and XML files. Application behavior/builds are outside this check.')

if __name__=='__main__':
    try:
        mode=sys.argv[1]
        if mode=='secrets': secret_scan()
        elif mode=='dependencies': dependency_scan()
        elif mode=='validate': validate()
        elif mode=='audit':
            failed=False
            for scan in (secret_scan,dependency_scan):
                try: scan(full=True)
                except RuntimeError as error: summary(str(error)); failed=True
            if failed: sys.exit(1)
        else: raise RuntimeError('Unknown check mode')
    except Exception as error:
        # Do not print tracebacks or tool output that might contain matched credentials.
        summary('Security check failed: '+(str(error) if isinstance(error,RuntimeError) else type(error).__name__))
        sys.exit(1)
