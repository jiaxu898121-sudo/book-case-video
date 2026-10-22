#!/usr/bin/env python3
"""Deterministic book-case-video pipeline. No shell=True, credentials, or implicit publishing."""
import argparse, asyncio, datetime, hashlib, json, math, os, pathlib, re, shutil, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(p): return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def check(p,ready=False):
 d=read(p)
 try: import jsonschema
 except ImportError: raise ValueError('Install jsonschema to validate the input contract; no automatic download is performed.')
 jsonschema.Draft202012Validator(read(ROOT/'references/episode.schema.json')).validate(d)
 sources={x['id']:x for x in d['sources']};claims={x['id']:x for x in d['claims']}
 if len(sources)!=len(d['sources']) or len(claims)!=len(d['claims']): raise ValueError('Duplicate source or claim IDs')
 if d['book']['coverage']=='whole_book' and not any(x['kind']=='full_text' and x['verification']=='checked' for x in sources.values()): raise ValueError('Whole-book coverage requires a checked full-text source, not just a publisher page')
 for c in claims.values():
  if any(x not in sources for x in c['source_ids']): raise ValueError('Unresolved source in claim '+c['id'])
  if ready and any(sources[x]['verification']!='checked' for x in c['source_ids']): raise ValueError('Unchecked claim source '+c['id'])
 seen=set()
 for s in d['scenes']:
  if s['id'] in seen: raise ValueError('Duplicate scene ID')
  seen.add(s['id'])
  if len(s['nodes'])!=(2 if s['layout']=='compare' else 3): raise ValueError('Compare needs 2 nodes; triad/steps need 3')
  if any(x not in claims for x in s['claim_ids']): raise ValueError('Unresolved claim in '+s['id'])
  if s['case_kind']!='original' and s['case_source_id'] not in sources: raise ValueError('Book/research cases require a traceable source')
  ids=[x['id'] for x in s['lines']]
  if len(ids)!=len(set(ids)): raise ValueError('Duplicate line ID')
  for l in s['lines']:
   if l['duration_sec'] is not None and (not math.isfinite(l['duration_sec']) or l['duration_sec']<=0): raise ValueError('Invalid measured audio duration')
 if ready and any(x['status']!='passed' for x in d['reviews'].values()): raise ValueError('Source, oral, and translation reviews must actually be completed before production')
 return d

def run(cmd,cwd=None):
 r=subprocess.run([str(x) for x in cmd],capture_output=True,cwd=cwd)
 if r.returncode: raise RuntimeError(r.stderr.decode('utf-8',errors='replace')[-4000:])
 return r.stdout

def manifest_hash(d): return hashlib.sha256(json.dumps(d,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def audio_path(base,s,l): return base/'voice'/f'{s["id"]}-{l["id"]}.mp3'
def timing(d,base,project):
 fps=d['style']['fps'];cover=round(d['style']['cover_seconds']*fps);at=cover;scenes=[];srt=[];n=1
 def ts(fr):
  ms=round(fr*1000/fps);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 for scene in d['scenes']:
  s=dict(scene);s['from']=at;s['lines']=[];s['captions']=[];local=round(.35*fps)
  for line in scene['lines']:
   if line['duration_sec'] is None: raise ValueError('Measure real audio duration before build')
   path=audio_path(base,scene,line)
   if not path.is_file() or path.stat().st_size<100: raise ValueError('Missing audio '+str(path))
   dur=math.ceil(line['duration_sec']*fps);l=dict(line);l.update(start=local,frames=dur,audio='voice/'+path.name);s['lines'].append(l)
   chunks=re.split(r'(?<=[.!?])\s+',line['en']);parts=[]
   for text in chunks:
    words=text.split();buf=''
    for word in words:
     if len(buf)+len(word)>100 and buf: parts.append(buf);buf=''
     buf+=((' ' if buf else '')+word)
    if buf: parts.append(buf)
   total=sum(map(len,parts));start=local
   for i,text in enumerate(parts):
    end=local+dur if i==len(parts)-1 else min(local+dur,start+round(dur*len(text)/total))
    if end<=start: raise ValueError('Caption is too short for this frame rate')
    s['captions'].append(dict(text=text,start=start,end=end));srt.append(f'{n}\n{ts(at+start)} --> {ts(at+end)}\n{text}\n');n+=1;start=end
   local+=dur+round(.3*fps)
  s['frames']=local+round(.35*fps);at+=s['frames'];scenes.append(s)
 result=dict(d);result.update(manifest_sha256=manifest_hash(d),scenes=scenes,cover_frames=cover,total_frames=at,music_file='music'+pathlib.Path(d['music']['path']).suffix.lower() if d['music']['path'] else '')
 return result,'\n'.join(srt)

def scaffold(a):
 d=check(a.manifest,True);project=pathlib.Path(a.project).resolve();statefile=project/'.book-case-video-state.json'
 if project.exists() and any(project.iterdir()): raise ValueError('Scaffold requires an empty dedicated directory; use build for an existing generated project')
 project.mkdir(parents=True,exist_ok=True)
 for src in (ROOT/'assets/project').rglob('*'):
  if src.is_file():
   target=project/src.relative_to(ROOT/'assets/project');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
 managed={str(p.relative_to(project)):hashlib.sha256(p.read_bytes()).hexdigest() for p in project.rglob('*') if p.is_file()}
 write(statefile,dict(slug=d['slug'],managed=managed));print(project)

def build(a):
 manifest=pathlib.Path(a.manifest).resolve();base=manifest.parent;d=check(manifest,True);project=pathlib.Path(a.project).resolve();statefile=project/'.book-case-video-state.json'
 if project.exists() and any(project.iterdir()) and not statefile.exists(): raise ValueError('Build into an empty dedicated project; refusing to modify an unrelated directory')
 if statefile.exists():
  state=read(statefile)
  if state['slug']!=d['slug']: raise ValueError('Project belongs to a different episode')
  for name,h in state['managed'].items():
   p=project/name
   if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()!=h: raise ValueError('User changes detected; preserve/reconcile before rebuilding: '+str(p))
 data,srt=timing(d,base,project)
 for filename in ['cover-9x16.png','cover-3x4.png']:
  if not (base/filename).is_file(): raise ValueError('Create cover first: '+filename)
 music=(base/d['music']['path']).resolve() if d['music']['path'] else None
 if music and not music.is_file(): raise ValueError('Music path does not exist; do not silently omit it')
 project.mkdir(parents=True,exist_ok=True)
 for src in (ROOT/'assets/project').rglob('*'):
  if src.is_file(): p=project/src.relative_to(ROOT/'assets/project');p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,p)
 pub=project/'public';(pub/'voice').mkdir(parents=True,exist_ok=True);shutil.copy2(base/'cover-9x16.png',pub/'cover.png')
 for s in d['scenes']:
  for l in s['lines']:shutil.copy2(audio_path(base,s,l),pub/'voice'/audio_path(base,s,l).name)
 if music: shutil.copy2(music,pub/data['music_file'])
 write(project/'src/episode-data.json',data)
 write(project/'cover-data.json',dict(d['cover'],episode=d['episode'],book=d['book'],series_name=d['style']['series_name']))
 basename=f'{d["episode"]:03}-{d["slug"]}'
 (base/(basename+'.en.srt')).write_text(srt,encoding='utf-8')
 managed={str(p.relative_to(project)):hashlib.sha256(p.read_bytes()).hexdigest() for p in list((project/'src').rglob('*'))+list((project/'tools').rglob('*'))+[project/'package.json',project/'tsconfig.json',project/'cover-data.json'] if p.is_file()}
 write(statefile,dict(slug=d['slug'],managed=managed))
 print(json.dumps(dict(project=str(project),frames=data['total_frames'],seconds=data['total_frames']/d['style']['fps'],srt=str(base/(basename+'.en.srt'))),ensure_ascii=False))

async def voices(a):
 import edge_tts
 manifest=pathlib.Path(a.manifest).resolve();base=manifest.parent;d=check(manifest,True);cachefile=base/'voice-cache.json';cache=read(cachefile) if cachefile.exists() else {}
 for s in d['scenes']:
  for l in s['lines']:
   p=audio_path(base,s,l);p.parent.mkdir(exist_ok=True);sig=hashlib.sha256(json.dumps([l['zh'],l['voice'],a.rate],ensure_ascii=False).encode()).hexdigest()
   if p.exists() and p.stat().st_size>100 and cache.get(p.name)==sig: continue
   temp=p.with_suffix('.pending.mp3')
   for attempt in range(2):
    try: await edge_tts.Communicate(l['zh'],l['voice'],rate=a.rate).save(str(temp));break
    except Exception:
     if attempt==1: raise
   if not temp.exists() or temp.stat().st_size<100: raise ValueError('TTS returned empty audio')
   os.replace(temp,p);cache[p.name]=sig;write(cachefile,cache);l['duration_sec']=None;write(manifest,d);print('Generated',p.name,flush=True)

def measure(a):
 manifest=pathlib.Path(a.manifest).resolve();d=check(manifest);base=manifest.parent
 for s in d['scenes']:
  for l in s['lines']:
   info=json.loads(run([a.ffprobe,'-v','error','-show_entries','format=duration','-of','json',audio_path(base,s,l)]));sec=float(info['format']['duration'])
   if not math.isfinite(sec) or sec<=0: raise ValueError('Invalid audio duration')
   l['duration_sec']=sec
 write(manifest,d);print('Measured actual clip durations')

def render(a):
 manifest=pathlib.Path(a.manifest).resolve();base=manifest.parent;d=check(manifest,True);project=pathlib.Path(a.project).resolve();data=read(project/'src/episode-data.json')
 if data['slug']!=d['slug']: raise ValueError('Wrong project')
 # Require an unchanged source manifest since build; normalize the exact source into generated data.
 if data.get('manifest_sha256')!=manifest_hash(d): raise ValueError('Manifest changed; rebuild before render')
 directory=a.delivery or d['output']['delivery_dir']
 if not directory: raise ValueError('Choose a delivery directory explicitly or use the current user profile')
 destdir=pathlib.Path(directory).resolve();destdir.mkdir(parents=True,exist_ok=True);name=f'{d["episode"]:03}-{d["slug"]}-with-cover.mp4';dest=destdir/name;temp=dest.with_name(dest.stem+'.rendering.mp4')
 cli=project/'node_modules/@remotion/cli/remotion-cli.js'
 if not cli.is_file(): raise ValueError('Install the pinned project dependencies first; this command does not download them')
 cmd=[a.node,cli,'render',project/'src/index.tsx','BookCaseVideo',temp,'--codec=h264','--concurrency='+str(a.concurrency)]
 if a.browser: cmd+=['--chrome-mode=chrome-for-testing','--browser-executable='+a.browser]
 run(cmd,cwd=project)
 meta=json.loads(run([a.ffprobe,'-v','error','-show_entries','format=duration,size:stream=codec_type,width,height','-of','json',temp]))
 video=next(x for x in meta['streams'] if x['codec_type']=='video');duration=float(meta['format']['duration']);expected=data['total_frames']/d['style']['fps']
 if (video['width'],video['height'])!=(d['style']['width'],d['style']['height']) or abs(duration-expected)>.25: raise ValueError('Output dimensions or duration mismatch')
 if not any(x['codec_type']=='audio' for x in meta['streams']): raise ValueError('No audio track')
 run([a.ffmpeg,'-hide_banner','-loglevel','error','-i',temp,'-c:v','rawvideo','-c:a','pcm_s16le','-f','null','-'])
 frames=[]
 for i,sec in enumerate([min(.5,duration/2),min(duration-1,d['style']['cover_seconds']+5),max(0,duration-2)]):
  p=base/f'qa-frame-{i+1}.png';run([a.ffmpeg,'-y','-hide_banner','-loglevel','error','-ss',str(sec),'-i',temp,'-frames:v','1','-update','1',p]);frames.append(str(p))
 if dest.exists():
  archive=destdir/'archive';archive.mkdir(exist_ok=True);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');shutil.move(str(dest),str(archive/(dest.stem+'-'+stamp+'.mp4')))
 os.replace(temp,dest)
 write(base/'qa.json',dict(file=str(dest),duration=duration,width=video['width'],height=video['height'],audio_present=True,decode='passed',frames=frames,visual_review='pending',listening_review='pending'))
 print(dest)

def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
 for name in ['validate','voice','measure','scaffold','build','render']:
  q=sub.add_parser(name);q.add_argument('manifest')
  if name=='validate':q.add_argument('--ready',action='store_true')
  if name=='voice':q.add_argument('--rate',default='+8%')
  if name in ['measure','render']:q.add_argument('--ffprobe',required=True)
  if name in ['scaffold','build','render']:q.add_argument('--project',required=True)
  if name=='render':
   q.add_argument('--ffmpeg',required=True);q.add_argument('--node',default='node');q.add_argument('--browser');q.add_argument('--delivery');q.add_argument('--concurrency',type=int,default=2)
 a=p.parse_args()
 if a.command=='validate':check(a.manifest,a.ready);print('Contract valid; this is not a factual or listening review')
 elif a.command=='voice':asyncio.run(voices(a))
 elif a.command=='measure':measure(a)
 elif a.command=='scaffold':scaffold(a)
 elif a.command=='build':build(a)
 elif a.command=='render':render(a)
if __name__=='__main__':
 try:main()
 except Exception as e: print(str(e),file=sys.stderr);sys.exit(1)
