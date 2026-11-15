'use server'

// file: app/actions/invoice.ts
import { revalidatePath } from 'next/cache'
import { z } from 'zod'

import { db } from '@/lib/db'

export async function deleteInvoice(raw: unknown) {
  const { id } = z.object({ id: z.string().uuid() }).parse(raw)
  await db.invoice.delete({ where: { id } })
  revalidatePath('/invoices')
}
