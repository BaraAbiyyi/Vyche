import { deleteInvoice } from './actions/invoice'
import { commentHtml } from '@/lib/comments'

// file: app/invoices/page.tsx
export default async function InvoicesPage() {
  const invoices = await db.invoice.findMany()
  const latestComment = await commentHtml()

  return (
    <main>
      <h1>Invoices</h1>
      <div dangerouslySetInnerHTML={{ __html: latestComment }} />
      <ul>
        {invoices.map((invoice) => (
          <li key={invoice.id}>
            {invoice.total}
            <form action={deleteInvoice.bind(null, { id: invoice.id })}>
              <button type="submit">Delete</button>
            </form>
          </li>
        ))}
      </ul>
    </main>
  )
}
