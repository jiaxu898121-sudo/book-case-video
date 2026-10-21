import React from 'react';
import {AbsoluteFill,Composition,Img,Sequence,interpolate,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import data from './episode-data.json';
const Scene=({index}:{index:number})=>{const s=data.scenes[index],f=useCurrentFrame(),{fps}=useVideoConfig();const st=data.style;const appear=(sec:number)=>interpolate(f,[sec*fps,(sec+.6)*fps],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});const cap=s.captions.find(c=>f>=c.start&&f<c.end);return <AbsoluteFill style={{background:st.background,color:st.cream,fontFamily:'Microsoft YaHei,Arial,sans-serif'}}>
<div style={{position:'absolute',inset:36,border:'1px solid #484535'}}/>
<div style={{position:'absolute',inset:0,opacity:.12,backgroundImage:'linear-gradient(#605d4c 1px,transparent 1px),linear-gradient(90deg,#605d4c 1px,transparent 1px)',backgroundSize:'72px 72px'}}/>
<div style={{position:'absolute',top:65,left:62,right:62,fontSize:14,color:'#b6ae99',display:'flex',justifyContent:'space-between'}}><span>{st.series_name} / {String(data.episode).padStart(3,'0')}</span><span>{index+1} / {data.scenes.length}</span></div>
<div style={{position:'absolute',top:135,left:62,right:62,opacity:appear(0)}}><div style={{fontSize:17,color:st.accent}}>{s.ey_zh} / {s.ey_en}</div><div data-check="title" style={{fontSize:52,fontWeight:900,lineHeight:1.4,whiteSpace:'pre-line',marginTop:26,maxHeight:158,overflow:'visible'}}>{s.title_lines.join('\n')}</div><div style={{height:2,background:st.accent,marginTop:28}}/></div>
<div style={{position:'absolute',top:435,left:62,right:62}}>{s.nodes.map((n,i)=><React.Fragment key={i}><div data-check="node" style={{border:`1px solid ${i===s.nodes.length-1?st.accent:'#5a553f'}`,padding:'25px 22px',fontSize:32,lineHeight:1.5,minHeight:104,color:i===s.nodes.length-1?st.accent:st.cream,opacity:appear(.5+i*.7),display:'flex',gap:20}}>{s.layout!=='compare'&&<span style={{color:st.accent,fontFamily:'Georgia'}}>{String(i+1).padStart(2,'0')}</span>}{n}</div>{i<s.nodes.length-1&&<div style={{height:s.layout==='compare'?82:43,textAlign:'center',fontSize:30,color:st.accent,opacity:appear(.8+i*.7)}}>↓</div>}</React.Fragment>)}{s.summary&&<div style={{marginTop:22,fontSize:18,color:'#b6ae99',textAlign:'center'}}>{s.summary}</div>}</div>
<div data-check="caption" style={{position:'absolute',bottom:130,left:62,right:62,fontSize:26,lineHeight:1.65,minHeight:112,background:st.background+'ee',textAlign:'center',padding:10,display:'grid',placeItems:'center'}}>{cap?.text}</div>
<div style={{position:'absolute',bottom:72,left:62,right:62,fontSize:12,color:'#b6ae99',display:'flex',justifyContent:'space-between'}}><span>{data.book.title}</span><span>核心解读 · 原创案例</span></div><div style={{position:'absolute',bottom:36,left:36,height:3,width:648*f/s.frames,background:st.accent}}/>
{s.lines.map(l=><Sequence key={l.id} from={l.start} durationInFrames={l.frames}><Audio src={staticFile(l.audio)}/></Sequence>)}
</AbsoluteFill>};
const Video=()=>{const frame=useCurrentFrame();return <>
<Sequence durationInFrames={data.cover_frames}><Img src={staticFile('cover.png')} style={{width:data.style.width,height:data.style.height}}/></Sequence>
{data.scenes.map((s,i)=><Sequence key={s.id} name={s.title_lines.join('')} from={s.from} durationInFrames={s.frames}><Scene index={i}/></Sequence>)}
{data.music_file&&<Audio src={staticFile(data.music_file)} loop volume={interpolate(frame,[0,45,data.total_frames-60,data.total_frames],[0,data.music.volume,data.music.volume,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}/>}
</>};
export const Root=()=> <Composition id="BookCaseVideo" component={Video} durationInFrames={data.total_frames} fps={data.style.fps} width={data.style.width} height={data.style.height}/>;
