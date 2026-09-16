import { useState } from 'react'
import { addGuest } from '../api/mockApi'

export function AddGuestForm() {
  const [name, setName] = useState('')
  const [partySize, setPartySize] = useState(2)
  const [phone, setPhone] = useState('')
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim() || !phone.trim()) return

    setSubmitting(true)
    await addGuest({ name: name.trim(), partySize, phone: phone.trim(), notes: notes.trim() })
    setSubmitting(false)
    setName('')
    setPartySize(2)
    setPhone('')
    setNotes('')
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 space-y-3">
      <h2 className="text-lg font-semibold text-gray-800">Add guest to waitlist</h2>

      <div className="grid grid-cols-2 gap-3">
        <label className="text-sm text-gray-600 col-span-2">
          Name
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            placeholder="Jane Doe"
          />
        </label>

        <label className="text-sm text-gray-600">
          Party size
          <input
            required
            type="number"
            min={1}
            max={20}
            value={partySize}
            onChange={(e) => setPartySize(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />
        </label>

        <label className="text-sm text-gray-600">
          Phone
          <input
            required
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            placeholder="+1 555 0100"
          />
        </label>

        <label className="text-sm text-gray-600 col-span-2">
          Notes (allergies, seating preference…)
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            rows={2}
          />
        </label>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-lg bg-violet-600 text-white text-sm font-medium py-2 hover:bg-violet-700 disabled:opacity-50"
      >
        {submitting ? 'Adding…' : 'Add to waitlist'}
      </button>
    </form>
  )
}
