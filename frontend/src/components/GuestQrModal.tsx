import { QRCodeSVG } from 'qrcode.react'
import type { WaitlistGuest } from '../types'

export function GuestQrModal({ guest, onClose }: { guest: WaitlistGuest; onClose: () => void }) {
  const link = `${window.location.origin}/guest/${guest.token}`

  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-lg p-6 max-w-sm w-full text-center space-y-3"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="text-lg font-semibold text-gray-800">{guest.name}'s QR code</h3>
        <p className="text-sm text-gray-500">Scan to check waitlist status</p>

        <div className="flex justify-center py-2">
          <QRCodeSVG value={link} size={180} />
        </div>

        <p className="text-xs text-gray-400 break-all">{link}</p>

        <button
          onClick={onClose}
          className="w-full rounded-lg bg-gray-100 text-gray-700 text-sm font-medium py-2 hover:bg-gray-200"
        >
          Close
        </button>
      </div>
    </div>
  )
}
