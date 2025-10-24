import { NextResponse } from 'next/server';
import { getServerAuthSession } from '@/server/auth';
import { prisma } from '@/server/db';
import { rateLimit } from '@/lib/rate-limit';

export async function GET() {
  const limit = await rateLimit('tasks:list');
  if (!limit.success) {
    return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 });
  }
  const session = await getServerAuthSession();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  const tasks = await prisma.task.findMany({
    include: { assignee: true, project: true }
  });
  return NextResponse.json(tasks);
}

export async function POST(request: Request) {
  const session = await getServerAuthSession();
  if (!session || session.user.role !== 'admin') {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }
  const limit = await rateLimit(`tasks:create:${session.user.id}`);
  if (!limit.success) {
    return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 });
  }
  const data = await request.json();
  const task = await prisma.task.create({ data });
  return NextResponse.json(task, { status: 201 });
}
