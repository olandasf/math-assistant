import { Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { NotFound } from '@/pages/NotFound'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        {/* TODO: Pridėti daugiau routes */}
        {/* <Route path="classes" element={<ClassesPage />} /> */}
        {/* <Route path="students" element={<StudentsPage />} /> */}
        {/* <Route path="tests" element={<TestsPage />} /> */}
        {/* <Route path="tests/:id" element={<TestDetailPage />} /> */}
        {/* <Route path="submissions" element={<SubmissionsPage />} /> */}
        {/* <Route path="statistics" element={<StatisticsPage />} /> */}
        {/* <Route path="settings" element={<SettingsPage />} /> */}
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

export default App
