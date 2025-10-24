import { SignInForm } from '@/components/sign-in-form';

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="glass-card glass-border w-full max-w-md p-10">
        <h1 className="text-3xl font-semibold tracking-tight text-white">Welcome to AION</h1>
        <p className="mt-2 text-sm text-slate-300">Authenticate to access mission control.</p>
        <div className="mt-8">
          <SignInForm />
        </div>
      </div>
    </div>
  );
}
