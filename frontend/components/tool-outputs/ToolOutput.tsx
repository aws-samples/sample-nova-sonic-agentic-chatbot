import { ToolOutput as ToolOutputType, AppToolOutput, BankingAppToolOutput } from './types';
import { TextOutput } from './TextOutput';
import { CardOutput } from './CardOutput';
import { ImageOutput } from './ImageOutput';
import { VideoOutput } from './VideoOutput';
import { PdfOutput } from './PdfOutput';
import { ButtonOutput } from './ButtonOutput';
import { BargeinOutput } from './BargeinOutput';
import { EchoApp } from '../apps/EchoApp';
import { BankingApp } from '../apps/BankingApp';

interface ToolOutputProps {
  output: ToolOutputType;
  websocket?: WebSocket | null;
}

const ToolOutput: React.FC<ToolOutputProps> = ({ output, websocket }) => {
  return (
    <div className="mb-4">
      {output.type === 'text' && output.content && (
        <TextOutput output={output} key="text" />
      )}
      {output.type === 'barge_in' && (
        <BargeinOutput key="barge_in" />
      )}
      {output.type === 'app' && (output as AppToolOutput).appName === 'banking' && (
        <BankingApp
          key="banking-app"
          action={(output as BankingAppToolOutput).props?.action}
          state={(output as BankingAppToolOutput).props?.state}
          transaction={(output as BankingAppToolOutput).props?.transaction}
        />
      )}
      {output.type === 'app' && (output as AppToolOutput).appName !== 'banking' && (
        <EchoApp key="app" {...((output as AppToolOutput).props || {})} />
      )}
      {output.type === 'card' && output.content && (
        <CardOutput output={output} key="card" />
      )}
      {output.type === 'image' && output.content && (
        <ImageOutput output={output} key="image" />
      )}
      {output.type === 'video' && output.content && (
        <VideoOutput output={output} key="video" />
      )}
      {output.type === 'pdf' && output.content && (
        <PdfOutput output={output} key="pdf" />
      )}
      {output.type === 'button' && output.content && (
        <ButtonOutput output={output} websocket={websocket} key="button" />
      )}
      {['barge_in', 'app', 'card', 'text', 'image', 'video', 'pdf', 'button'].indexOf(output.type) === -1 && (
        <div className="text-gray-500 italic">Unknown output type: {output.type}</div>
      )}
    </div>
  );
};

export { ToolOutput }; 