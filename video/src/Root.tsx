import {Composition} from 'remotion';
import {AivoraPromo, TOTAL_FRAMES} from './AivoraPromo';

export const RemotionRoot: React.FC = () => (
	<Composition
		id="AivoraPromo"
		component={AivoraPromo}
		durationInFrames={TOTAL_FRAMES}
		fps={30}
		width={1080}
		height={1920}
	/>
);
