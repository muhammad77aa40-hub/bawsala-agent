import '@fontsource/cairo/600.css';
import '@fontsource/cairo/800.css';
import '@fontsource/cairo/900.css';
import {useEffect, useState} from 'react';
import {
	AbsoluteFill,
	Audio,
	Easing,
	Sequence,
	continueRender,
	delayRender,
	interpolate,
	random,
	staticFile,
	useCurrentFrame,
} from 'remotion';
import T from './timeline.json';

// Brand colors taken from aivorastudio.info
const BG = '#07070b';
const LIME = '#CDFC56';
const SKY = '#0ea5e9';
const VIOLET = '#7c3aed';
const WHITE = '#ffffff';
const INK = '#0b0b10';
const FONT = 'Cairo, sans-serif';

export const TOTAL_FRAMES = T.total;
const scene = (k: keyof typeof T.scenes) => ({from: T.scenes[k][0], dur: T.scenes[k][1] - T.scenes[k][0]});

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Strength (1 -> 0) of the most recent event in `list` at `frame`
const envelope = (frame: number, list: number[], decay: number) =>
	list.reduce((m, h) => (frame >= h ? Math.max(m, Math.exp(-(frame - h) / decay)) : m), 0);

// Scale-down "slam" with motion blur, starting at local frame `at`
const slam = (f: number, at: number, from = 2.6, len = 7) => {
	const p = interpolate(f, [at, at + len], [0, 1], {...clamp, easing: Easing.out(Easing.back(2.2))});
	const visible = f >= at;
	return {
		opacity: visible ? interpolate(f, [at, at + 2], [0, 1], clamp) : 0,
		transform: `scale(${from + (1 - from) * p})`,
		filter: `blur(${interpolate(f, [at, at + len], [18, 0], clamp)}px)`,
	};
};

const slideIn = (f: number, at: number, dx: number, len = 8) => {
	const p = interpolate(f, [at, at + len], [0, 1], {...clamp, easing: Easing.out(Easing.exp)});
	return {
		opacity: f >= at ? 1 : 0,
		transform: `translateX(${(1 - p) * dx}px) skewX(${(1 - p) * -20}deg)`,
		filter: `blur(${(1 - p) * 14}px)`,
	};
};

const rgbSplit = (amount: number) =>
	amount > 0.3 ? `${amount}px 0 rgba(255,40,110,0.85), ${-amount}px 0 rgba(0,229,255,0.85)` : 'none';

const useFonts = () => {
	const [handle] = useState(() => delayRender('fonts'));
	useEffect(() => {
		Promise.all(
			[600, 800, 900].map((w) => document.fonts.load(`${w} 40px Cairo`, 'أيفورا 0123 abc')),
		).then(() => continueRender(handle));
	}, [handle]);
};

// ---------- background layers ----------

const Background: React.FC<{frame: number}> = ({frame}) => {
	const t = frame / 30;
	const beat = envelope(frame, T.hits.concat(T.impacts), 6);
	return (
		<AbsoluteFill style={{backgroundColor: BG, overflow: 'hidden'}}>
			<div
				style={{
					position: 'absolute',
					width: 1300,
					height: 1300,
					borderRadius: '50%',
					background: `radial-gradient(circle, ${SKY}66 0%, transparent 62%)`,
					left: -420 + Math.sin(t * 1.3) * 160,
					top: -300 + Math.cos(t * 1.1) * 140,
					opacity: 0.7 + beat * 0.3,
				}}
			/>
			<div
				style={{
					position: 'absolute',
					width: 1400,
					height: 1400,
					borderRadius: '50%',
					background: `radial-gradient(circle, ${VIOLET}66 0%, transparent 62%)`,
					right: -520 + Math.cos(t * 0.9) * 180,
					bottom: -380 + Math.sin(t * 1.2) * 160,
					opacity: 0.7 + beat * 0.3,
				}}
			/>
			<AbsoluteFill
				style={{
					backgroundImage:
						'linear-gradient(rgba(255,255,255,0.05) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,0.05) 2px, transparent 2px)',
					backgroundSize: '120px 120px',
					backgroundPosition: `0 ${frame * 6}px`,
					transform: 'perspective(900px) rotateX(55deg) scale(2.2) translateY(20%)',
					opacity: 0.8,
				}}
			/>
		</AbsoluteFill>
	);
};

const SpeedLines: React.FC<{frame: number; intensity: number; color?: string}> = ({frame, intensity, color = WHITE}) => {
	if (intensity <= 0.01) return null;
	const lines = new Array(46).fill(0).map((_, i) => {
		const angle = random(`a${i}`) * Math.PI * 2;
		const speed = 40 + random(`s${i}`) * 80;
		const len = 120 + random(`l${i}`) * 360;
		const r = ((frame * speed + random(`o${i}`) * 1800) % 1800) + 120;
		const cx = 540;
		const cy = 960;
		return {
			x1: cx + Math.cos(angle) * r,
			y1: cy + Math.sin(angle) * r,
			x2: cx + Math.cos(angle) * (r + len),
			y2: cy + Math.sin(angle) * (r + len),
			w: 2 + random(`w${i}`) * 5,
		};
	});
	return (
		<svg width={1080} height={1920} style={{position: 'absolute', opacity: intensity}}>
			{lines.map((l, i) => (
				<line key={i} x1={l.x1} y1={l.y1} x2={l.x2} y2={l.y2} stroke={color} strokeWidth={l.w} strokeLinecap="round" opacity={0.55} />
			))}
		</svg>
	);
};

const Particles: React.FC<{frame: number}> = ({frame}) => (
	<AbsoluteFill>
		{new Array(40).fill(0).map((_, i) => {
			const x = random(`px${i}`) * 1080;
			const speed = 3 + random(`ps${i}`) * 9;
			const y = 1920 - ((frame * speed + random(`py${i}`) * 1920) % 2000);
			const size = 4 + random(`pz${i}`) * 10;
			return (
				<div
					key={i}
					style={{
						position: 'absolute',
						left: x,
						top: y,
						width: size,
						height: size,
						borderRadius: '50%',
						background: i % 3 === 0 ? LIME : i % 3 === 1 ? SKY : VIOLET,
						boxShadow: `0 0 ${size * 2}px ${i % 3 === 0 ? LIME : SKY}`,
						opacity: 0.7,
					}}
				/>
			);
		})}
	</AbsoluteFill>
);

const Shockwaves: React.FC<{frame: number}> = ({frame}) => (
	<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', pointerEvents: 'none'}}>
		{T.impacts.map((h) => {
			const d = frame - h;
			if (d < 0 || d > 24) return null;
			const p = d / 24;
			return [0, 5].map((lag) => {
				const q = Math.max(0, (d - lag) / 24);
				return (
					<div
						key={`${h}-${lag}`}
						style={{
							position: 'absolute',
							width: 200 + q * 2200,
							height: 200 + q * 2200,
							borderRadius: '50%',
							border: `${lag ? 6 : 18}px solid ${lag ? SKY : LIME}`,
							opacity: (1 - p) * (lag ? 0.6 : 0.9),
						}}
					/>
				);
			});
		})}
	</AbsoluteFill>
);

// Diagonal color panels sweeping across the screen on transitions
const Wipes: React.FC<{frame: number}> = ({frame}) => (
	<AbsoluteFill style={{pointerEvents: 'none', overflow: 'hidden'}}>
		{T.whooshes.map((w) => {
			const start = w - 4;
			const d = frame - start;
			if (d < 0 || d > 18) return null;
			return [LIME, INK].map((c, i) => {
				const x = interpolate(d - i * 3, [0, 15], [1500, -2600], {...clamp, easing: Easing.inOut(Easing.cubic)});
				return (
					<div
						key={`${w}-${i}`}
						style={{
							position: 'absolute',
							top: -400,
							left: x,
							width: 1500,
							height: 2800,
							background: c,
							transform: 'skewX(-18deg)',
						}}
					/>
				);
			});
		})}
	</AbsoluteFill>
);

// Horizontal glitch slices of the content when `amount` > 0
const Glitch: React.FC<{amount: number; seed: number; children: React.ReactNode}> = ({amount, seed, children}) => {
	if (amount <= 0.02) return <AbsoluteFill>{children}</AbsoluteFill>;
	const slices = 7;
	return (
		<AbsoluteFill>
			{new Array(slices).fill(0).map((_, i) => {
				const top = (i / slices) * 100;
				const bottom = 100 - ((i + 1) / slices) * 100;
				const off = (random(`g${seed}-${i}`) - 0.5) * 160 * amount;
				return (
					<AbsoluteFill key={i} style={{clipPath: `inset(${top}% 0 ${bottom}% 0)`, transform: `translateX(${off}px)`}}>
						{children}
					</AbsoluteFill>
				);
			})}
		</AbsoluteFill>
	);
};

// The "A" mark from the site's favicon
const Logo: React.FC<{size: number; glow?: number}> = ({size, glow = 0}) => (
	<svg width={size} height={size} viewBox="0 0 256 256" style={{filter: `drop-shadow(0 0 ${20 + glow * 60}px ${SKY})`}}>
		<defs>
			<linearGradient id="mark" x1="64" y1="48" x2="200" y2="208" gradientUnits="userSpaceOnUse">
				<stop offset="0%" stopColor={SKY} />
				<stop offset="100%" stopColor={VIOLET} />
			</linearGradient>
		</defs>
		<rect width="256" height="256" rx="56" fill="#06091e" />
		<rect x="3" y="3" width="250" height="250" rx="54" fill="none" stroke="url(#mark)" strokeWidth="5" />
		<path d="M 128 56 L 64 200" stroke="url(#mark)" strokeWidth="24" strokeLinecap="round" />
		<path d="M 128 56 L 192 200" stroke="url(#mark)" strokeWidth="24" strokeLinecap="round" />
		<path d="M 92 152 L 164 152" stroke={LIME} strokeWidth="14" strokeLinecap="round" />
		<circle cx="128" cy="56" r="11" fill="#fff" />
	</svg>
);

const Center: React.FC<{children: React.ReactNode; gap?: number; style?: React.CSSProperties}> = ({children, gap = 0, style}) => (
	<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', direction: 'rtl', gap, ...style}}>{children}</AbsoluteFill>
);

// ---------- scenes (local frame f) ----------

const Intro: React.FC<{f: number}> = ({f}) => {
	const build = f < 30;
	const out = interpolate(f, [100, 120], [1, 3.2], {...clamp, easing: Easing.in(Easing.cubic)});
	const outBlur = interpolate(f, [104, 120], [0, 30], clamp);
	if (build) {
		const letters = 'AIVORA'.split('');
		return (
			<Center>
				<div style={{display: 'flex', gap: 30, direction: 'ltr'}}>
					{letters.map((l, i) => {
						const on = random(`fl${i}-${Math.floor(f / 2)}`) < f / 30;
						return (
							<span
								key={i}
								style={{
									fontSize: 150,
									fontWeight: 900,
									color: 'transparent',
									WebkitTextStroke: `3px ${i % 2 ? SKY : LIME}`,
									opacity: on ? 1 : 0.1,
									transform: `translateY(${(random(`fy${i}-${f}`) - 0.5) * 30 * (f / 30)}px)`,
								}}
							>
								{l}
							</span>
						);
					})}
				</div>
			</Center>
		);
	}
	return (
		<Center gap={40} style={{transform: `scale(${out})`, filter: `blur(${outBlur}px)`}}>
			<div style={{...slam(f, 30, 5, 9), transform: `${slam(f, 30, 5, 9).transform} rotate(${interpolate(f, [30, 39], [-25, 0], clamp)}deg)`}}>
				<Logo size={360} glow={envelope(f, [30], 8)} />
			</div>
			<div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1.05}}>
				<span style={{...slam(f, 45), fontSize: 200, fontWeight: 900, color: WHITE, textShadow: rgbSplit(envelope(f, [45], 4) * 16)}}>
					أيفورا
				</span>
				<span style={{...slam(f, 60), fontSize: 200, fontWeight: 900, color: LIME, textShadow: rgbSplit(envelope(f, [60], 4) * 16)}}>
					ستوديو
				</span>
			</div>
			<div
				style={{
					clipPath: `inset(0 0 0 ${interpolate(f, [75, 83], [100, 0], {...clamp, easing: Easing.out(Easing.exp)})}%)`,
					background: LIME,
					color: INK,
					fontSize: 58,
					fontWeight: 900,
					padding: '8px 44px',
					transform: 'skewX(-10deg)',
				}}
			>
				شركة برمجيات عراقية 🇮🇶
			</div>
		</Center>
	);
};

const Headline: React.FC<{f: number}> = ({f}) => {
	const lines = [
		{text: 'نطوّر', at: 0},
		{text: 'البرمجيات', at: 15},
		{text: 'اللي', at: 30},
		{text: 'تدير', at: 45},
		{text: 'شغلك', at: 60},
	];
	const build = interpolate(f, [75, 118], [0, 1], clamp);
	const shakeX = (random(`hx${f}`) - 0.5) * 40 * build;
	const glitch = f > 75 ? build * (random(`hg${Math.floor(f / 2)}`) > 0.4 ? 1 : 0.2) : 0;
	return (
		<Glitch amount={glitch} seed={Math.floor(f / 2)}>
			<Center style={{transform: `translateX(${shakeX}px) scale(${1 + build * 0.25})`}}>
				<div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1.05}}>
					{lines.map((l, i) => {
						const current = f >= l.at && (i === lines.length - 1 || f < lines[i + 1].at);
						const big = i >= 3;
						return (
							<span
								key={l.text}
								style={{
									...slam(f, l.at, 3),
									fontSize: big ? 250 : 190,
									fontWeight: 900,
									color: big ? LIME : WHITE,
									textShadow: rgbSplit(envelope(f, [l.at], 4) * 20),
									opacity: f >= l.at ? (current ? 1 : 0.85) : 0,
								}}
							>
								{l.text}
							</span>
						);
					})}
				</div>
			</Center>
		</Glitch>
	);
};

const SERVICES = [
	{icon: '🖥️', title: 'مواقع ويب', sub: 'سريعة • متجاوبة • تبيع'},
	{icon: '📱', title: 'تطبيقات موبايل', sub: 'iOS + Android'},
	{icon: '🛒', title: 'متاجر إلكترونية', sub: 'دفع إلكتروني • طلبات • مخزون'},
	{icon: '🏦', title: 'أنظمة مصرفية', sub: 'صرافة • محاسبة • ERP'},
	{icon: '📊', title: 'لوحات تحكم', sub: 'تحليلات لحظية • CRM'},
	{icon: '🎬', title: 'هوية وموشن', sub: 'تصميم • فيديو • براند'},
];

const Services: React.FC<{f: number}> = ({f}) => {
	const i = Math.min(SERVICES.length - 1, Math.floor(f / 30));
	const lf = f - i * 30;
	const s = SERVICES[i];
	const inverted = i % 2 === 1;
	const fg = inverted ? INK : WHITE;
	const dir = i % 2 ? -1 : 1;
	return (
		<AbsoluteFill style={{background: inverted ? LIME : 'transparent'}}>
			{/* giant outlined index number behind */}
			<Center>
				<div
					style={{
						fontSize: 900,
						fontWeight: 900,
						color: 'transparent',
						WebkitTextStroke: `6px ${inverted ? 'rgba(0,0,0,0.15)' : 'rgba(205,252,86,0.18)'}`,
						transform: `translateX(${dir * (lf * 8 - 120)}px)`,
						direction: 'ltr',
					}}
				>
					0{i + 1}
				</div>
			</Center>
			<Center gap={46}>
				<div
					style={{
						...slam(lf, 0, 0.2, 8),
						width: 300,
						height: 300,
						borderRadius: 80,
						background: inverted ? INK : `linear-gradient(135deg, ${SKY}, ${VIOLET})`,
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'center',
						fontSize: 170,
						boxShadow: `0 0 90px ${inverted ? 'rgba(0,0,0,0.4)' : SKY}`,
						rotate: `${interpolate(lf, [0, 10], [dir * 40, 0], clamp)}deg`,
					}}
				>
					{s.icon}
				</div>
				<div style={{...slideIn(lf, 3, dir * 1200), fontSize: 130, fontWeight: 900, color: fg, textAlign: 'center', lineHeight: 1.1, maxWidth: 980}}>
					{s.title}
				</div>
				<div style={{...slideIn(lf, 7, dir * -1200), fontSize: 56, fontWeight: 800, color: inverted ? INK : LIME}}>{s.sub}</div>
			</Center>
			{/* progress segments */}
			<div style={{position: 'absolute', bottom: 150, left: 140, right: 140, display: 'flex', gap: 14, direction: 'rtl'}}>
				{SERVICES.map((_, k) => (
					<div key={k} style={{flex: 1, height: 12, borderRadius: 6, background: k <= i ? fg : inverted ? 'rgba(0,0,0,0.2)' : 'rgba(255,255,255,0.2)'}} />
				))}
			</div>
		</AbsoluteFill>
	);
};

const MONTAGE = ['أتمتة', 'CRM', 'ERP', 'SEO', 'تسويق', 'أمان', 'سرعة', 'ذكاء اصطناعي'];
const MONTAGE_BG = [INK, LIME, SKY, INK, VIOLET, LIME, INK, SKY];

const Montage: React.FC<{f: number; abs: number}> = ({abs}) => {
	const idx = T.montageHits.reduce((acc, h, k) => (abs >= h ? k : acc), 0);
	const at = T.montageHits[idx];
	const lf = abs - at;
	const bg = MONTAGE_BG[idx];
	const fg = bg === LIME ? INK : WHITE;
	const word = MONTAGE[idx];
	return (
		<AbsoluteFill style={{background: bg}}>
			<Center>
				<div
					style={{
						...slam(lf, 0, 1.8, 4),
						fontSize: word.length > 6 ? 170 : 280,
						fontWeight: 900,
						color: fg,
						rotate: `${(random(`mr${idx}`) - 0.5) * 14}deg`,
						textShadow: rgbSplit(envelope(lf, [0], 3) * 18),
						textAlign: 'center',
						lineHeight: 1.1,
					}}
				>
					{word}
				</div>
			</Center>
		</AbsoluteFill>
	);
};

const AiScene: React.FC<{f: number}> = ({f}) => {
	const build = interpolate(f, [75, 118], [0, 1], clamp);
	const glitchIn = interpolate(f, [0, 10], [1, 0], clamp);
	const glitch = Math.max(glitchIn, f > 75 ? build * (random(`ag${Math.floor(f / 2)}`) > 0.5 ? 1 : 0.2) : 0);
	const typing = f >= 45 && f < 60;
	const bubble = (at: number, mine: boolean, text: string) => (
		<div
			style={{
				...slam(f, at, 0.3, 6),
				alignSelf: mine ? 'flex-start' : 'flex-end',
				padding: '30px 46px',
				borderRadius: 46,
				fontSize: 54,
				fontWeight: 800,
				background: mine ? 'rgba(255,255,255,0.12)' : LIME,
				color: mine ? WHITE : INK,
				border: mine ? '2px solid rgba(255,255,255,0.2)' : 'none',
			}}
		>
			{text}
		</div>
	);
	return (
		<Glitch amount={glitch} seed={Math.floor(f / 2)}>
			<Center gap={40} style={{transform: `scale(${1 + build * 0.3})`}}>
				<div style={{fontSize: 60, fontWeight: 900, color: SKY, letterSpacing: 4, direction: 'ltr', opacity: f % 10 < 7 || f > 10 ? 1 : 0}}>
					{'< AI AGENT />'}
				</div>
				<div style={{...slam(f, 0, 2.4), fontSize: 170, fontWeight: 900, color: WHITE, textShadow: rgbSplit(12 * envelope(f, [0], 5))}}>
					وكيل ذكي
				</div>
				<div
					style={{
						...slam(f, 45, 4, 8),
						fontSize: 330,
						fontWeight: 900,
						color: LIME,
						direction: 'ltr',
						lineHeight: 1,
						textShadow: `0 0 60px ${LIME}88, ${rgbSplit(20 * envelope(f, [45], 5))}`,
					}}
				>
					24/7
				</div>
				<div style={{display: 'flex', flexDirection: 'column', gap: 26, width: 900}}>
					{bubble(30, true, 'عندكم موعد باچر؟ 🤔')}
					{typing ? (
						<div style={{alignSelf: 'flex-end', display: 'flex', gap: 14, padding: '34px 46px', borderRadius: 46, background: LIME}}>
							{[0, 1, 2].map((k) => (
								<div key={k} style={{width: 22, height: 22, borderRadius: 11, background: INK, transform: `translateY(${Math.sin((f + k * 4) / 2.5) * 10}px)`}} />
							))}
						</div>
					) : (
						bubble(60, false, 'أكيد! ١٠ الصبح أو ٢ الظهر ✅')
					)}
				</div>
			</Center>
		</Glitch>
	);
};

const Cta: React.FC<{f: number}> = ({f}) => {
	const pulse = 1 + envelope(f % 15, [0], 4) * 0.06 * (f >= 30 ? 1 : 0);
	const finalHit = envelope(f, [120], 10);
	const contacts = [
		{icon: '💬', text: '+964 750 999 9380', at: 45},
		{icon: '📸', text: '@aivoraastudio', at: 60},
		{icon: '🌐', text: 'aivorastudio.info', at: 75},
	];
	return (
		<Center gap={44}>
			<div style={slam(f, 0, 4, 8)}>
				<Logo size={230} glow={envelope(f, [0, 120], 8)} />
			</div>
			<div style={{...slam(f, 4, 2.5), fontSize: 120, fontWeight: 900, color: WHITE, textAlign: 'center', lineHeight: 1.15, textShadow: rgbSplit(envelope(f, [4, 120], 4) * 14)}}>
				جاهز تبني
				<br />
				<span style={{color: LIME}}>شي استثنائي؟</span>
			</div>
			<div
				style={{
					...slam(f, 30, 0.2, 7),
					transform: `${slam(f, 30, 0.2, 7).transform} scale(${pulse + finalHit * 0.1}) skewX(-8deg)`,
					background: LIME,
					color: INK,
					fontSize: 64,
					fontWeight: 900,
					padding: '30px 80px',
					borderRadius: 24,
					boxShadow: `0 0 ${60 + finalHit * 120}px ${LIME}aa`,
				}}
			>
				جلسة استكشاف مجانية ⚡
			</div>
			<div style={{display: 'flex', flexDirection: 'column', gap: 24, marginTop: 20}}>
				{contacts.map((c, i) => (
					<div
						key={c.text}
						style={{
							...slideIn(f, c.at, i % 2 ? -900 : 900),
							display: 'flex',
							alignItems: 'center',
							gap: 26,
							fontSize: 58,
							fontWeight: 800,
							color: WHITE,
							background: 'rgba(255,255,255,0.08)',
							border: '2px solid rgba(255,255,255,0.15)',
							borderRadius: 30,
							padding: '16px 40px',
						}}
					>
						<span>{c.icon}</span>
						<span style={{direction: 'ltr'}}>{c.text}</span>
					</div>
				))}
			</div>
		</Center>
	);
};

// ---------- composition ----------

export const AivoraPromo: React.FC = () => {
	useFonts();
	const frame = useCurrentFrame();

	const impact = envelope(frame, T.impacts, 7);
	const hitE = envelope(frame, T.hits.concat(T.montageHits), 4);
	const shakeAmp = impact * 55 + hitE * 16;
	const sx = (random(`sx${frame}`) - 0.5) * 2 * shakeAmp;
	const sy = (random(`sy${frame}`) - 0.5) * 2 * shakeAmp;
	const zoom = 1 + impact * 0.12 + hitE * 0.04;
	const flash = Math.max(envelope(frame, T.impacts, 3) * 0.95, envelope(frame, T.hits, 2) * 0.25);

	const riser = T.risers.reduce((m, [a, b]) => (frame >= a && frame < b ? Math.max(m, (frame - a) / (b - a)) : m), 0);
	const speed = Math.max(riser, impact * 0.9, envelope(frame, T.montageHits, 5) * 0.6);

	const s = {
		intro: scene('intro'),
		headline: scene('headline'),
		services: scene('services'),
		montage: scene('montage'),
		ai: scene('ai'),
		cta: scene('cta'),
	};
	const local = (k: keyof typeof s) => frame - s[k].from;

	return (
		<AbsoluteFill style={{fontFamily: FONT, overflow: 'hidden'}}>
			<Audio src={staticFile('soundtrack.wav')} />
			<AbsoluteFill style={{transform: `translate(${sx}px, ${sy}px) scale(${zoom})`}}>
				<Background frame={frame} />
				<Particles frame={frame} />
				<SpeedLines frame={frame} intensity={speed} color={riser > 0 ? LIME : WHITE} />
				<Sequence from={s.intro.from} durationInFrames={s.intro.dur}>
					<Intro f={local('intro')} />
				</Sequence>
				<Sequence from={s.headline.from} durationInFrames={s.headline.dur}>
					<Headline f={local('headline')} />
				</Sequence>
				<Sequence from={s.services.from} durationInFrames={s.services.dur}>
					<Services f={local('services')} />
				</Sequence>
				<Sequence from={s.montage.from} durationInFrames={s.montage.dur}>
					<Montage f={local('montage')} abs={frame} />
				</Sequence>
				<Sequence from={s.ai.from} durationInFrames={s.ai.dur}>
					<AiScene f={local('ai')} />
				</Sequence>
				<Sequence from={s.cta.from} durationInFrames={s.cta.dur}>
					<Cta f={local('cta')} />
				</Sequence>
				<Shockwaves frame={frame} />
			</AbsoluteFill>
			<Wipes frame={frame} />
			<AbsoluteFill style={{background: WHITE, opacity: flash, pointerEvents: 'none'}} />
			{/* vignette */}
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.65) 100%)', pointerEvents: 'none'}} />
		</AbsoluteFill>
	);
};
