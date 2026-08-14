import { OsChatView } from '../OsChatView';

type ChatThreadPageProps = {
  params: Promise<{ threadId: string }>;
};

export default async function ChatThreadPage({ params }: ChatThreadPageProps) {
  const { threadId } = await params;
  return <OsChatView initialThreadId={threadId} />;
}
