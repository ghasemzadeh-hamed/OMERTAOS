import { OsChatView } from '../OsChatView';

type ChatThreadPageProps = {
  params: { threadId: string };
};

export default function ChatThreadPage({ params }: ChatThreadPageProps) {
  return <OsChatView initialThreadId={params.threadId} />;
}
