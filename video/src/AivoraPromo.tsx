import '@fontsource/cairo/500.css';
import '@fontsource/cairo/700.css';
import '@fontsource/cairo/800.css';
import {useEffect, useState} from 'react';
import {
	AbsoluteFill,
	Easing,
	Sequence,
	continueRender,
	delayRender,
	interpolate,
	spring,
	useCurrentFrame,
	useVideoConfig,
} from 'remotion';

// Brand colors taken from aivorastudio.info
const BG = '#0b0b10';
const LIME = '#CDFC56';
const SKY = '#0ea5e9';
const VIOLET = '#7c3aed';
const WHITE = '#ffffff';
const MUTED = 'rgba(255,255,255,0.62)';
const FONT = 'Cairo, sans-serif';

const SCENES = {intro: 90, headline: 90, services1: 120, services2: 120, ai: 105, cta: 135};
export const TOTAL_FRAMES = Object.values(SCENES).reduce((a, b) => a + b, 0);

const useFonts = () => {
	const [handle] = useState(() => delayRender('fonts'));
	useEffect(() => {
		Promise.all(
			[500, 700, 800].map((w) => document.fonts.load(`${w} 40px Cairo`, 'أيفورا 0123 abc')),
		).then(() => continueRender(handle));
	}, [handle]);
};

const fadeInUp = (frame: number, delay: number, fps: number) => {
	const s = spring({frame: frame - delay, fps, config: {damping: 200}});
	return {opacity: s, transform: `translateY(${(1 - s) * 60}px)`};
};

// Fades a whole scene out over its last frames
const SceneFade: React.FC<{duration: number; children: React.ReactNode}> = ({duration, children}) => {
	const frame = useCurrentFrame();
	const opacity = interpolate(frame, [duration - 12, duration], [1, 0], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	return <AbsoluteFill style={{opacity}}>{children}</AbsoluteFill>;
};

const Background: React.FC = () => {
	const frame = useCurrentFrame();
	const t = frame / 30;
	return (
		<AbsoluteFill style={{backgroundColor: BG, overflow: 'hidden'}}>
			<div
				style={{
					position: 'absolute',
					width: 1100,
					height: 1100,
					borderRadius: '50%',
					background: `radial-gradient(circle, ${SKY}55 0%, transparent 65%)`,
					left: -350 + Math.sin(t * 0.6) * 120,
					top: -250 + Math.cos(t * 0.5) * 100,
				}}
			/>
			<div
				style={{
					position: 'absolute',
					width: 1200,
					height: 1200,
					borderRadius: '50%',
					background: `radial-gradient(circle, ${VIOLET}50 0%, transparent 65%)`,
					right: -450 + Math.cos(t * 0.4) * 140,
					bottom: -300 + Math.sin(t * 0.55) * 120,
				}}
			/>
			<AbsoluteFill
				style={{
					backgroundImage:
						'linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px)',
					backgroundSize: '90px 90px',
					backgroundPosition: `0 ${frame * 0.8}px`,
				}}
			/>
		</AbsoluteFill>
	);
};

// The "A" mark from the site's favicon, drawn on with stroke animation
const Logo: React.FC<{size: number; progress: number}> = ({size, progress}) => {
	const len = 160;
	const dash = len * (1 - progress);
	return (
		<svg width={size} height={size} viewBox="0 0 256 256">
			<defs>
				<linearGradient id="mark" x1="64" y1="48" x2="200" y2="208" gradientUnits="userSpaceOnUse">
					<stop offset="0%" stopColor={SKY} />
					<stop offset="100%" stopColor={VIOLET} />
				</linearGradient>
			</defs>
			<rect width="256" height="256" rx="56" fill="#06091e" />
			<rect x="2" y="2" width="252" height="252" rx="54" fill="none" stroke="url(#mark)" strokeWidth="3" opacity={0.7} />
			<path d="M 128 56 L 64 200" stroke="url(#mark)" strokeWidth="22" strokeLinecap="round" strokeDasharray={len} strokeDashoffset={dash} />
			<path d="M 128 56 L 192 200" stroke="url(#mark)" strokeWidth="22" strokeLinecap="round" strokeDasharray={len} strokeDashoffset={dash} />
			<path d="M 92 152 L 164 152" stroke="url(#mark)" strokeWidth="14" strokeLinecap="round" opacity={progress * 0.6} />
			<circle cx="128" cy="56" r="9" fill="#fff" opacity={progress} />
			<circle cx="128" cy="56" r={16 + (1 - progress) * 30} fill={SKY} opacity={0.35 * progress} />
		</svg>
	);
};

const Intro: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const draw = interpolate(frame, [0, 35], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
	const pop = spring({frame, fps, config: {damping: 12}});
	return (
		<SceneFade duration={SCENES.intro}>
			<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 50}}>
				<div style={{transform: `scale(${0.6 + pop * 0.4})`}}>
					<Logo size={340} progress={draw} />
				</div>
				<div style={{...fadeInUp(frame, 25, fps), fontSize: 130, fontWeight: 800, color: WHITE, letterSpacing: 2}}>
					أيفورا ستوديو
				</div>
				<div style={{...fadeInUp(frame, 38, fps), fontSize: 50, fontWeight: 500, color: LIME}}>
					شركة برمجيات عراقية
				</div>
			</AbsoluteFill>
		</SceneFade>
	);
};

const Headline: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const words = ['نطوّر', 'البرمجيات', 'التي', 'تدير', 'أعمالك.'];
	return (
		<SceneFade duration={SCENES.headline}>
			<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', padding: 90}}>
				<div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '10px 34px', direction: 'rtl'}}>
					{words.map((w, i) => (
						<span
							key={w}
							style={{
								...fadeInUp(frame, i * 6, fps),
								fontSize: 140,
								fontWeight: 800,
								lineHeight: 1.25,
								color: i >= 3 ? LIME : WHITE,
								display: 'inline-block',
							}}
						>
							{w}
						</span>
					))}
				</div>
				<div style={{...fadeInUp(frame, 40, fps), marginTop: 70, fontSize: 46, color: MUTED, textAlign: 'center', direction: 'rtl'}}>
					تطبيقات • منصات • متاجر • أنظمة إدارة
				</div>
			</AbsoluteFill>
		</SceneFade>
	);
};

type Service = {icon: string; title: string; desc: string};

const ServiceCard: React.FC<Service & {delay: number}> = ({icon, title, desc, delay}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const s = spring({frame: frame - delay, fps, config: {damping: 16}});
	return (
		<div
			style={{
				opacity: s,
				transform: `translateX(${(1 - s) * 220}px)`,
				display: 'flex',
				alignItems: 'center',
				gap: 40,
				direction: 'rtl',
				width: 900,
				padding: '44px 50px',
				borderRadius: 44,
				background: 'rgba(255,255,255,0.06)',
				border: '2px solid rgba(255,255,255,0.12)',
			}}
		>
			<div
				style={{
					width: 130,
					height: 130,
					flexShrink: 0,
					borderRadius: 34,
					background: `linear-gradient(135deg, ${SKY}, ${VIOLET})`,
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'center',
					fontSize: 70,
				}}
			>
				{icon}
			</div>
			<div style={{display: 'flex', flexDirection: 'column', gap: 6}}>
				<div style={{fontSize: 60, fontWeight: 800, color: WHITE}}>{title}</div>
				<div style={{fontSize: 36, fontWeight: 500, color: MUTED, lineHeight: 1.4}}>{desc}</div>
			</div>
		</div>
	);
};

const Services: React.FC<{items: Service[]; duration: number; showTitle: boolean}> = ({items, duration, showTitle}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return (
		<SceneFade duration={duration}>
			<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 48}}>
				<div style={{...fadeInUp(frame, 0, fps), fontSize: 70, fontWeight: 800, color: LIME, marginBottom: 20}}>
					{showTitle ? 'ماذا نبني لك؟' : 'وأكثر...'}
				</div>
				{items.map((it, i) => (
					<ServiceCard key={it.title} {...it} delay={10 + i * 12} />
				))}
			</AbsoluteFill>
		</SceneFade>
	);
};

const AiScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const bubbles = [
		{from: 'user', text: 'عندكم موعد بكرة؟'},
		{from: 'bot', text: 'أكيد! الساعة ١٠ أو ٢ متاحة 👌'},
	];
	return (
		<SceneFade duration={SCENES.ai}>
			<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 44, direction: 'rtl'}}>
				<div style={{...fadeInUp(frame, 0, fps), fontSize: 50, fontWeight: 700, color: LIME}}>+ حلول الذكاء الاصطناعي</div>
				<div style={{...fadeInUp(frame, 6, fps), fontSize: 100, fontWeight: 800, color: WHITE, textAlign: 'center', lineHeight: 1.3}}>
					وكيل ذكي
					<br />
					يرد على زبائنك 24/7
				</div>
				<div style={{display: 'flex', flexDirection: 'column', gap: 26, width: 860, marginTop: 20}}>
					{bubbles.map((b, i) => {
						const s = spring({frame: frame - 25 - i * 18, fps, config: {damping: 14}});
						const isUser = b.from === 'user';
						return (
							<div
								key={b.text}
								style={{
									alignSelf: isUser ? 'flex-start' : 'flex-end',
									opacity: s,
									transform: `scale(${0.7 + s * 0.3})`,
									padding: '28px 42px',
									borderRadius: 40,
									fontSize: 46,
									fontWeight: 700,
									background: isUser ? 'rgba(255,255,255,0.1)' : LIME,
									color: isUser ? WHITE : '#141414',
								}}
							>
								{b.text}
							</div>
						);
					})}
				</div>
				<div style={{...fadeInUp(frame, 60, fps), fontSize: 40, color: MUTED}}>حجوزات • طلبات • متابعات — بدون تدخل بشري</div>
			</AbsoluteFill>
		</SceneFade>
	);
};

const Cta: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const pulse = 1 + Math.sin(frame / 6) * 0.025;
	const contacts = [
		{icon: '💬', text: '+964 750 999 9380'},
		{icon: '📸', text: '@aivoraastudio'},
		{icon: '🌐', text: 'aivorastudio.info'},
	];
	return (
		<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 50, direction: 'rtl'}}>
			<div style={fadeInUp(frame, 0, fps)}>
				<Logo size={200} progress={1} />
			</div>
			<div style={{...fadeInUp(frame, 6, fps), fontSize: 96, fontWeight: 800, color: WHITE, textAlign: 'center', lineHeight: 1.3}}>
				جاهز تبني
				<br />
				شي استثنائي؟
			</div>
			<div
				style={{
					...fadeInUp(frame, 14, fps),
					transform: `scale(${pulse})`,
					background: LIME,
					color: '#141414',
					fontSize: 54,
					fontWeight: 800,
					padding: '30px 70px',
					borderRadius: 100,
				}}
			>
				جلسة استكشاف مجانية
			</div>
			<div style={{display: 'flex', flexDirection: 'column', gap: 22, marginTop: 20}}>
				{contacts.map((c, i) => (
					<div
						key={c.text}
						style={{...fadeInUp(frame, 26 + i * 8, fps), display: 'flex', alignItems: 'center', gap: 24, fontSize: 50, fontWeight: 700, color: WHITE}}
					>
						<span>{c.icon}</span>
						<span style={{direction: 'ltr'}}>{c.text}</span>
					</div>
				))}
			</div>
		</AbsoluteFill>
	);
};

export const AivoraPromo: React.FC = () => {
	useFonts();
	let from = 0;
	const at = (d: number) => {
		const start = from;
		from += d;
		return start;
	};
	return (
		<AbsoluteFill style={{fontFamily: FONT}}>
			<Background />
			<Sequence from={at(SCENES.intro)} durationInFrames={SCENES.intro}>
				<Intro />
			</Sequence>
			<Sequence from={at(SCENES.headline)} durationInFrames={SCENES.headline}>
				<Headline />
			</Sequence>
			<Sequence from={at(SCENES.services1)} durationInFrames={SCENES.services1}>
				<Services
					duration={SCENES.services1}
					showTitle
					items={[
						{icon: '🖥️', title: 'تصميم المواقع', desc: 'مواقع سريعة ومتجاوبة مصممة للتحويل'},
						{icon: '📱', title: 'تطبيقات الموبايل', desc: 'iOS و Android — خدمات، حجوزات، توصيل'},
						{icon: '🛒', title: 'المتاجر الإلكترونية', desc: 'سلة، دفع إلكتروني، إدارة طلبات ومخزون'},
					]}
				/>
			</Sequence>
			<Sequence from={at(SCENES.services2)} durationInFrames={SCENES.services2}>
				<Services
					duration={SCENES.services2}
					showTitle={false}
					items={[
						{icon: '🏦', title: 'أنظمة مصرفية وصرافة', desc: 'محاسبة، ERP، وأنظمة CRM للمؤسسات'},
						{icon: '📊', title: 'لوحات التحكم', desc: 'تحليلات آنية ومراكز تحكم متكاملة'},
						{icon: '🎬', title: 'تصميم وموشن', desc: 'هوية بصرية وفيديو لقصة علامتك'},
					]}
				/>
			</Sequence>
			<Sequence from={at(SCENES.ai)} durationInFrames={SCENES.ai}>
				<AiScene />
			</Sequence>
			<Sequence from={at(SCENES.cta)} durationInFrames={SCENES.cta}>
				<Cta />
			</Sequence>
		</AbsoluteFill>
	);
};
