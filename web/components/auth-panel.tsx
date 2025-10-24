'use client'

import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(3)
})

export function AuthPanel() {
  const [message, setMessage] = useState<string | null>(null)
  const { register, handleSubmit, formState } = useForm<{ email: string; password: string }>({
    resolver: zodResolver(schema),
    defaultValues: { email: 'admin@aion.local', password: 'admin123' }
  })

  const onSubmit = handleSubmit(async (values) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8080'}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(values)
    })
    if (!res.ok) {
      setMessage('Authentication failed')
      return
    }
    const data = await res.json()
    window.localStorage.setItem('aion-token', data.token)
    setMessage('Authenticated')
  })

  return (
    <form onSubmit={onSubmit} className="glass-panel p-4 space-y-3">
      <div className="space-y-2">
        <label className="text-xs text-white/60" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          className="w-full rounded-lg bg-white/10 px-3 py-2 text-sm text-white focus:outline-none focus:ring"
          {...register('email')}
        />
      </div>
      <div className="space-y-2">
        <label className="text-xs text-white/60" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          type="password"
          className="w-full rounded-lg bg-white/10 px-3 py-2 text-sm text-white focus:outline-none focus:ring"
          {...register('password')}
        />
      </div>
      <button
        type="submit"
        disabled={formState.isSubmitting}
        className="glass-panel px-4 py-2 text-sm font-semibold text-white hover:bg-white/20 transition"
      >
        Sign In
      </button>
      {message && <p className="text-xs text-white/70">{message}</p>}
    </form>
  )
}
