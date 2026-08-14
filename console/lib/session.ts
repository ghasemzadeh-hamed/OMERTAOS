import { getServerSession } from 'next-auth';
import { authOptions } from './auth';

export async function safeGetServerSession() {
  try {
    return await getServerSession(authOptions);
  } catch (error) {
    console.error('getServerSession failed', error);
    return null;
  }
}
