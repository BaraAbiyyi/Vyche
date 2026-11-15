'use server'

// file: app/actions/profile.ts
import { revalidatePath } from 'next/cache'
import { z } from 'zod'

import { auth } from '@/lib/auth'
import { db } from '@/lib/db'

export async function updateDisplayName(raw: unknown) {
  const session = await auth()
  if (!session?.user) throw new Error('unauthorized')

  const { name } = z.object({ name: z.string().min(1).max(60) }).parse(raw)

  await db.user.update({
    where: { id: session.user.id },
    data: { name },
  })

  revalidatePath('/profile')
}
