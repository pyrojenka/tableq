import { Route, Routes } from 'react-router-dom'
import { GuestPage } from './pages/GuestPage'
import { HostessPage } from './pages/HostessPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<HostessPage />} />
      <Route path="/guest/:token" element={<GuestPage />} />
    </Routes>
  )
}

export default App
