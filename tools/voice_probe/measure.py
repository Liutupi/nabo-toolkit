"""C3 compile and exact-baseline link-only sizing; never build/flash a release.

Reads the existing F3 Ninja link description and original objects. Produces
separate baseline/probe ELF/MAP/bin under build/voice-probe. It does not rewrite
F3 outputs, run Ninja, update dependencies, touch NVS or open any device port.
The baseline must reproduce the accepted application before any delta is used.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(args, cwd, log):
    result = subprocess.run(args, cwd=cwd, capture_output=True,
                            text=True, encoding='utf-8', errors='replace')
    log.write_text(result.stdout+result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'Probe command failed; inspect {log}')
    return result.stdout


def ninja_link(build):
    lines = (build/'build.ninja').read_text(encoding='utf-8').splitlines()
    i = next(i for i,line in enumerate(lines) if line.startswith('build nabo-toolkit.elf:'))
    explicit = lines[i].split(' | ')[0].split(' ',3)[3]
    variables = {}
    for line in lines[i+1:]:
        if not line.startswith('  '):
            break
        key, value = line.strip().split(' = ',1)
        variables[key] = value.replace('$:', ':').replace('$ ', ' ')
    return explicit, variables, lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-dir',type=Path,default=ROOT/'build/f3')
    parser.add_argument('--output',type=Path,default=ROOT/'build/voice-probe')
    parser.add_argument('--baseline',type=Path,
        default=ROOT/'build/release/v0.3.1-remote-dev2/nabo-toolkit-app.bin')
    args = parser.parse_args()
    build, output = args.build_dir.resolve(),args.output.resolve()
    if not output.is_relative_to(ROOT/'build') or output == build or build.is_relative_to(output):
        raise ValueError('Probe output must be a separate directory under this checkout/build')
    description = json.loads((build/'project_description.json').read_text(encoding='utf-8'))
    assert description['target'] == 'esp32c3'
    idf = Path(description['idf_path'])
    version = (idf/'components/esp_common/include/esp_idf_version.h').read_text(encoding='utf-8')
    assert all(f'#define ESP_IDF_VERSION_{key}   {value}' in version or
               re.search(rf'#define\s+ESP_IDF_VERSION_{key}\s+{value}\b',version)
               for key,value in [('MAJOR',6),('MINOR',0),('PATCH',2)])
    commands = json.loads((build/'compile_commands.json').read_text(encoding='utf-8'))
    first = commands[0]['command']
    compiler = Path(first.split(' -',1)[0].strip('"'))
    assert compiler.name in ('riscv32-esp-elf-gcc.exe','riscv32-esp-elf-gcc')
    linker = compiler.with_name(compiler.name.replace('-gcc','-g++'))
    size_tool = compiler.with_name(compiler.name.replace('-gcc','-size'))
    nm_tool = compiler.with_name(compiler.name.replace('-gcc','-nm'))
    explicit,variables,lines = ninja_link(build)
    image_command = next(line for line in lines if ' -m esptool ' in line and 'elf2image' in line)
    # Keep the current build's silicon-revision/MMU/image flags, not new defaults.
    image_args = shlex.split(image_command.split(' -m esptool ',1)[1].split(' -o ',1)[0])
    python_match = re.search(r'([A-Za-z]:[^\n]*?python\.exe) -m esptool ',image_command)
    if not python_match:
        raise ValueError('Pass through a supported Windows ESP-IDF build description')
    # The generated command may contain preceding cmd.exe/cd syntax; use its final token.
    python = python_match.group(1).split(' && ')[-1].strip('"')
    output.mkdir(parents=True,exist_ok=True)
    sources = ['features.c','matcher.c','link_probe.c']
    cflags = shlex.split((build/'toolchain/cflags').read_text(encoding='utf-8'))
    objects = []
    for name in sources:
        obj = output/(name+'.o')
        execute([str(compiler),*cflags,'-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
                 '-fdata-sections','-ffunction-sections','-fstack-usage','-fno-common',
                 '-c',str(HERE/name),'-o',str(obj)],build,output/(name+'.compile.log'))
        objects.append(obj)
    reports = {}
    for name,extras in [('baseline',[]),('probe',objects)]:
        elf, binary, map_file = [output/(name+suffix) for suffix in ('.elf','.bin','.map')]
        response = output/(name+'.rsp')
        response.write_text(explicit+' '+
            ' '.join('"'+p.as_posix()+'"' for p in extras)+' '+
            variables['LINK_PATH']+' '+variables['LINK_LIBRARIES'],encoding='utf-8')
        flags = variables['FLAGS']+' '+variables['LINK_FLAGS']
        flags = re.sub(r'"-Wl,--Map=[^"]+"','"-Wl,--Map='+map_file.as_posix()+'"',flags)
        if extras:
            flags += ' -Wl,--undefined=vp_link_probe_step'
        # Response files preserve Windows paths/spaces without invoking a shell.
        flag_file = output/(name+'.flags')
        flag_file.write_text(flags,encoding='utf-8')
        execute([str(linker),'@'+str(flag_file),'@'+str(response),'-o',str(elf)],
                build,output/(name+'.link.log'))
        execute([python,'-m','esptool',*image_args,'-o',str(binary),str(elf)],
                build,output/(name+'.image.log'))
        sizes = execute([str(size_tool),'-A',str(elf)],build,output/(name+'.size.txt'))
        sections = {}
        for line in sizes.splitlines():
            parts = line.split()
            if len(parts)==3 and parts[0].startswith('.'):
                sections[parts[0]]=int(parts[1])
        symbols = execute([str(nm_tool),'-S','--size-sort',str(elf)],build,output/(name+'.nm.txt'))
        fp_helpers = [line for line in symbols.splitlines() if re.search(
            r' __(?:add|sub|mul|div)(?:sf|df)3$| __(?:float|fix)',line)]
        reports[name] = {'app_bytes':binary.stat().st_size,'app_sha256':digest(binary),
                         'elf_sha256':digest(elf),'sections':sections,
                         'floating_point_helpers':fp_helpers}
        if name=='baseline' and binary.read_bytes()!=args.baseline.read_bytes():
            raise RuntimeError('Link-only baseline did not reproduce the accepted app; do not use delta')
    baseline,probe = reports['baseline'],reports['probe']
    bss = lambda r:sum(v for k,v in r['sections'].items() if k.endswith('.bss'))
    stack = []
    for path in output.glob('*.su'):
        for line in path.read_text(encoding='utf-8').splitlines():
            location,bytes_,kind = line.split('\t')
            stack.append({'function':location.split(':')[-1],'bytes':int(bytes_),'kind':kind})
    reports.update({'mode':'Exact accepted-object baseline plus force-retained algorithm/buffer link-only probe',
        'sdk':'6.0.2','target':'esp32c3','production_sources_changed':False,
        'probe_called_by_firmware':False,'device_tested':False,'is_installable_feature':False,
        'baseline_byte_equal_to_accepted':True,
        'flash_delta_bytes':probe['app_bytes']-baseline['app_bytes'],
        'legacy_factory_capacity':0x1f0000,
        'legacy_remaining_after_probe_bytes':0x1f0000-probe['app_bytes'],
        'bss_delta_bytes':bss(probe)-bss(baseline),
        'max_single_function_stack_bytes':max(x['bytes'] for x in stack),
        'function_stack_usage':stack,
        'sources_sha256':{name:digest(HERE/name) for name in sources},
        'limits':['Not a clean complete firmware build or hardware execution.',
                  'No microphone, task/queue/lifecycle, NVS, UI or HID integration.',
                  'No real command recordings, accuracy, realtime or power validation.',
                  'Heap subtraction is an estimate; future task stacks/driver peaks are additional.']})
    dest = output/'measurement.json'
    dest.write_text(json.dumps(reports,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:reports[k] for k in ['baseline_byte_equal_to_accepted','flash_delta_bytes',
         'legacy_remaining_after_probe_bytes','bss_delta_bytes','max_single_function_stack_bytes']}))


if __name__=='__main__':
    main()
