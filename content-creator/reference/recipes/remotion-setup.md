# Remotion Setup & Component Library

Remotion is a React framework for programmatic video. It renders motion graphics, animated code, diagrams, transitions, counters, and kinetic text as real video files — things VideoDB's timeline editor cannot do natively (it places pre-rendered clips, no animation primitives).

**Remotion is NOT optional for Fireship-style videos.** Without it you get a slideshow of static images with voiceover. With it you get animated code typing, diagrams that build themselves, bars that race, text that flies in, and smooth graphic transitions between topics.

## Phase 0: Bootstrap

Run this during Phase 0 pre-flight. It takes ~60 seconds.

### Step 1: Check Node.js

```bash
node --version && npm --version
```

If Node.js is not installed, Remotion is unavailable. Set `REMOTION_AVAILABLE = False` and move on.

### Step 2: Scaffold Project

```bash
REMOTION_DIR="{WORK_DIR}/remotion"
mkdir -p "$REMOTION_DIR" && cd "$REMOTION_DIR"

# Initialize a minimal Remotion project
npm init -y
npm install --save-exact remotion @remotion/cli @remotion/bundler react react-dom
npm install --save-dev typescript @types/react
```

### Step 3: Create Minimal Config

```bash
cat > "$REMOTION_DIR/remotion.config.ts" << 'EOF'
import {Config} from '@remotion/cli/config';
Config.setVideoImageFormat('png');
EOF

cat > "$REMOTION_DIR/tsconfig.json" << 'EOF'
{
  "compilerOptions": {
    "target": "ES2018",
    "module": "commonjs",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "outDir": "./dist"
  },
  "include": ["src/**/*"]
}
EOF

mkdir -p "$REMOTION_DIR/src"
```

### Step 4: Create Root Entry Point

```bash
cat > "$REMOTION_DIR/src/Root.tsx" << 'EOF'
import {Composition} from 'remotion';
import {CodeEditor} from './CodeEditor';
import {KineticText} from './KineticText';
import {DiagramFlow} from './DiagramFlow';
import {BarChart} from './BarChart';
import {SplitCompare} from './SplitCompare';
import {WhipTransition} from './WhipTransition';
import {CounterReveal} from './CounterReveal';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="CodeEditor" component={CodeEditor}
        durationInFrames={180} fps={30} width={1280} height={720}
        defaultProps={{code: '', language: 'javascript', theme: 'github-dark'}} />
      <Composition id="KineticText" component={KineticText}
        durationInFrames={150} fps={30} width={1280} height={720}
        defaultProps={{lines: ['Hello World'], animation: 'scale-in'}} />
      <Composition id="DiagramFlow" component={DiagramFlow}
        durationInFrames={210} fps={30} width={1280} height={720}
        defaultProps={{nodes: [], edges: []}} />
      <Composition id="BarChart" component={BarChart}
        durationInFrames={180} fps={30} width={1280} height={720}
        defaultProps={{bars: [], animationStyle: 'grow'}} />
      <Composition id="SplitCompare" component={SplitCompare}
        durationInFrames={180} fps={30} width={1280} height={720}
        defaultProps={{leftPanel: {label:'Before',content:'',contentType:'code',accentColor:'#f85149'}, rightPanel: {label:'After',content:'',contentType:'code',accentColor:'#3fb950'}, revealStyle: 'left-first'}} />
      <Composition id="WhipTransition" component={WhipTransition}
        durationInFrames={15} fps={30} width={1280} height={720}
        defaultProps={{direction: 'right', color: '#3498DB'}} />
      <Composition id="CounterReveal" component={CounterReveal}
        durationInFrames={120} fps={30} width={1280} height={720}
        defaultProps={{targetValue: 100, suffix: '%'}} />
    </>
  );
};
EOF
```

### Step 5: Write Components

Write each component file into `$REMOTION_DIR/src/`. The components are defined in the sections below.

### Step 6: Test Render

```bash
cd "$REMOTION_DIR"
npx remotion still src/Root.tsx CodeEditor "$REMOTION_DIR/test_render.png" \
  --props='{"code":"const x = 1;","language":"javascript","theme":"github-dark"}' \
  --frame=0 2>&1
```

If this produces `test_render.png` → `REMOTION_AVAILABLE = True`.
If it fails → run `npm install` again, retry once. If still fails → `REMOTION_AVAILABLE = False`.

---

## Component: CodeEditor

Animated code with syntax highlighting, typing effect, line-by-line reveals. See [code-slide.md](code-slide.md) for full details.

```tsx
// src/CodeEditor.tsx
import {useCurrentFrame, interpolate, spring, useVideoConfig} from 'remotion';

interface CodeEditorProps {
  code: string;
  language: string;
  theme?: string;
  typingSpeed?: number;     // characters revealed per frame
  highlightLines?: number[];
  fileName?: string;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code, language, typingSpeed = 3, highlightLines = [], fileName
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const charsVisible = Math.min(code.length, frame * typingSpeed);
  const visibleCode = code.slice(0, charsVisible);
  const cursorOpacity = Math.sin(frame * 0.3) > 0 ? 1 : 0;

  return (
    <div style={{
      width: '100%', height: '100%', background: '#0d1117',
      display: 'flex', flexDirection: 'column', padding: '30px 40px',
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    }}>
      {fileName && (
        <div style={{display:'flex', gap:8, alignItems:'center', marginBottom:16}}>
          <div style={{width:12,height:12,borderRadius:'50%',background:'#ff5f57'}} />
          <div style={{width:12,height:12,borderRadius:'50%',background:'#febc2e'}} />
          <div style={{width:12,height:12,borderRadius:'50%',background:'#28c840'}} />
          <span style={{color:'#8b949e',fontSize:13,marginLeft:12}}>{fileName}</span>
        </div>
      )}
      <pre style={{
        background: '#161b22', borderRadius: 12, padding: '24px 30px',
        flex: 1, overflow: 'hidden', boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
      }}>
        <code style={{fontSize: 18, lineHeight: 1.6, color: '#e6edf3'}}>
          {visibleCode}
          <span style={{opacity: cursorOpacity, color: '#58a6ff'}}>▌</span>
        </code>
      </pre>
    </div>
  );
};
```

**Render:** `npx remotion render src/Root.tsx CodeEditor output.mp4 --props='...'`

Note: For full syntax highlighting in Remotion, install `prism-react-renderer` or `shiki` and integrate with the component. The base version above shows typing animation with monospace styling.

---

## Component: KineticText

Text that animates in — scale, slide, spring, word-by-word reveal. Replaces static `TextAsset` for hero moments.

```tsx
// src/KineticText.tsx
import {useCurrentFrame, spring, useVideoConfig, interpolate} from 'remotion';

interface KineticTextProps {
  lines: string[];
  fontSize?: number;
  animation: 'scale-in' | 'slide-up' | 'spring' | 'word-by-word';
  accentColor?: string;
  bgColor?: string;
}

export const KineticText: React.FC<KineticTextProps> = ({
  lines, fontSize = 60, animation = 'scale-in', accentColor = '#FFD700', bgColor = '#0d1117'
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <div style={{
      width: '100%', height: '100%', background: bgColor,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: 16,
    }}>
      {lines.map((line, i) => {
        const delay = i * 8;
        const s = spring({frame: frame - delay, fps, config: {damping: 12, stiffness: 120}});
        const scale = animation === 'scale-in' ? s : 1;
        const translateY = animation === 'slide-up'
          ? interpolate(s, [0, 1], [80, 0]) : 0;
        const opacity = interpolate(s, [0, 0.3, 1], [0, 1, 1]);
        return (
          <div key={i} style={{
            fontSize, fontWeight: 900, color: i === 0 ? accentColor : '#FFFFFF',
            fontFamily: "'Impact', 'Montserrat', sans-serif",
            textShadow: '3px 3px 6px rgba(0,0,0,0.8)',
            transform: `scale(${scale}) translateY(${translateY}px)`,
            opacity,
          }}>
            {line}
          </div>
        );
      })}
    </div>
  );
};
```

**Render:** `npx remotion render src/Root.tsx KineticText output.mp4 --props='{"lines":["5 JS Features","You Don'\''t Know"],"animation":"spring"}'`

---

## Component: WhipTransition

A fast directional wipe (0.3-0.5s) used between topics. Pre-render as a short clip and insert between segments on the timeline.

```tsx
// src/WhipTransition.tsx
import {useCurrentFrame, interpolate, useVideoConfig} from 'remotion';

interface WhipTransitionProps {
  direction: 'left' | 'right' | 'up' | 'down';
  color?: string;
}

export const WhipTransition: React.FC<WhipTransitionProps> = ({
  direction = 'right', color = '#3498DB'
}) => {
  const frame = useCurrentFrame();
  const {width, height, durationInFrames} = useVideoConfig();

  const progress = interpolate(frame, [0, durationInFrames], [0, 1]);
  const isHorizontal = direction === 'left' || direction === 'right';
  const size = isHorizontal ? width : height;
  const bandWidth = size * 0.15;

  const pos = interpolate(progress, [0, 1],
    direction === 'right' || direction === 'down'
      ? [-bandWidth, size + bandWidth]
      : [size + bandWidth, -bandWidth]
  );

  return (
    <div style={{width: '100%', height: '100%', background: 'transparent', overflow: 'hidden'}}>
      <div style={{
        position: 'absolute',
        ...(isHorizontal
          ? {left: pos, top: 0, width: bandWidth, height: '100%'}
          : {top: pos, left: 0, height: bandWidth, width: '100%'}
        ),
        background: `linear-gradient(${isHorizontal ? '90deg' : '180deg'}, transparent, ${color}, transparent)`,
        filter: 'blur(8px)',
      }} />
    </div>
  );
};
```

**Render:** `npx remotion render src/Root.tsx WhipTransition whip.mp4 --props='{"direction":"right","color":"#3498DB"}' --codec=vp8`

**Timeline usage:** Insert the whip clip as a 0.5s overlay between two segments. Use transparent background so it renders on top.

---

## Component: CounterReveal

Animated number counting up from 0 to target with easing. For stat reveals ("73% of developers...").

```tsx
// src/CounterReveal.tsx
import {useCurrentFrame, interpolate, Easing, useVideoConfig} from 'remotion';

interface CounterRevealProps {
  targetValue: number;
  prefix?: string;
  suffix?: string;
  fontSize?: number;
  color?: string;
  label?: string;
}

export const CounterReveal: React.FC<CounterRevealProps> = ({
  targetValue, prefix = '', suffix = '', fontSize = 96, color = '#61DAFB', label
}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  const countEnd = Math.floor(durationInFrames * 0.6);
  const value = Math.round(
    interpolate(frame, [0, countEnd], [0, targetValue], {
      easing: Easing.out(Easing.cubic),
      extrapolateRight: 'clamp',
    })
  );

  return (
    <div style={{
      width: '100%', height: '100%', background: '#0d1117',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
    }}>
      <div style={{
        fontSize, fontWeight: 900, color,
        fontFamily: "'Montserrat', sans-serif",
        textShadow: '0 0 40px rgba(97,218,251,0.3)',
      }}>
        {prefix}{value.toLocaleString()}{suffix}
      </div>
      {label && (
        <div style={{fontSize: 28, color: '#8b949e', marginTop: 16}}>
          {label}
        </div>
      )}
    </div>
  );
};
```

---

## Component: DiagramFlow

See [diagram-flow.md](diagram-flow.md) for the full interface. The component animates SVG nodes appearing with spring physics and edges drawing as animated paths.

## Component: BarChart

See [data-viz.md](data-viz.md) for the full interface. Bars grow from 0 to their value with staggered spring animations.

## Component: SplitCompare

See [split-compare.md](split-compare.md) for the full interface. Two panels with animated reveal (left-first, wipe, or simultaneous).

---

## Rendering Commands

All renders produce 1280x720 video at 30fps.

```bash
# Animated video (most components)
npx remotion render src/Root.tsx {CompositionId} \
  "{REMOTION_DIR}/output/{segment_id}.mp4" \
  --props='{...}' \
  --width=1280 --height=720

# Static still (when you just need one frame, e.g. code screenshot)
npx remotion still src/Root.tsx {CompositionId} \
  "{REMOTION_DIR}/output/{segment_id}.png" \
  --props='{...}' \
  --frame=60

# Transparent background (for transition overlays)
npx remotion render src/Root.tsx WhipTransition \
  "{REMOTION_DIR}/output/whip.webm" \
  --props='{...}' \
  --codec=vp8
```

Upload the output to VideoDB:
- `.mp4` → `VideoAsset` (mute with `volume=0` on timeline)
- `.png` → `ImageAsset`

## What Remotion Enables (That VideoDB Cannot)

| Capability | Remotion | VideoDB Timeline |
|---|---|---|
| Code typing animation | Yes — character-by-character reveal with cursor blink | No — static image only |
| Diagram build-up | Yes — nodes spring in, edges draw themselves | No — full diagram or nothing |
| Bar chart racing | Yes — bars animate from 0 to value | No — static chart image |
| Counter tick-up | Yes — number counts from 0 to target with easing | No — static number |
| Text fly-in/spring | Yes — word-by-word, scale, slide, spring physics | No — `TextAsset` appears instantly |
| Split-screen wipe reveal | Yes — divider slides revealing right panel | No — both panels visible immediately |
| Whip/graphic transitions | Yes — pre-rendered as clip, inserted between segments | Only `hard_cut` and fade natively |
| Zoom into code line | Yes — camera zoom effect within component | No zoom/pan support |
| SVG path drawing | Yes — stroke-dashoffset animation | No SVG support |
| Spring/bounce physics | Yes — `spring()` primitive | No animation primitives |

## When to Use Remotion vs Alternatives

| Visual Type | Use Remotion When... | Use Playwright When... | Use VideoDB TextAsset When... |
|---|---|---|---|
| `code_editor` | `REMOTION_AVAILABLE` — animated typing | Remotion unavailable — static screenshot | Never for code |
| `kinetic_text` | Hero moments, hooks, topic intros (animated reveal) | Never | Quick callouts, data overlays, lower thirds |
| `diagram_animation` | Always if available — diagrams need build-up | Remotion unavailable — static Mermaid.js | Never |
| `data_viz` | Always if available — charts need animation | Remotion unavailable — static Chart.js | Stat counter text as supplement |
| `split_screen` | Always if available — animated reveal | Remotion unavailable — static dual HTML | Never |
| transitions | `whip` and `graphic` transitions | Never | Never |

## Adding New Components

To add a custom component for a specific video:

1. Write the `.tsx` file into `$REMOTION_DIR/src/`
2. Register it in `Root.tsx` with a `<Composition>` entry
3. Render with `npx remotion render src/Root.tsx {YourId} output.mp4 --props='{...}'`

Remotion components are just React — you can use any npm package (chart libraries, SVG tools, syntax highlighters) inside them.
