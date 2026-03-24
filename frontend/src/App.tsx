import { Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { Dashboard } from "@/pages/Dashboard";
import { NotFound } from "@/pages/NotFound";
import { ClassesPage } from "@/pages/Classes";
import { StudentsPage } from "@/pages/Students";
import { TestsPage, TestDetailPage, TestGeneratorPage } from "@/pages/Tests";
import { UploadPage } from "@/pages/Upload";
import { ReviewPage, WorkReviewPage } from "@/pages/Review";
import { ComparePage } from "@/pages/Compare";
import { StatisticsPage } from "@/pages/Statistics";
import { SettingsPage } from "@/pages/Settings";
import { PrivacyPage } from "@/pages/Privacy";
import { ExportsPage } from "@/pages/Exports";
import { ResultsPage, SubmissionsListPage } from "@/pages/Results";
import { TemplatesPage } from "@/pages/Templates";
import { QuickCheckPage } from "@/pages/QuickCheck";
import { LoginPage } from "@/pages/Login";
import { useAuthStore } from "@/stores/authStore";

function ProtectedRoutes() {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/prisijungti" replace />;
  }

  return (
    <Layout>
      <Routes>
        <Route index element={<Dashboard />} />
        <Route path="klases" element={<ClassesPage />} />
        <Route path="mokiniai" element={<StudentsPage />} />
        <Route path="kontroliniai" element={<TestsPage />} />
        <Route path="kontroliniai/:id" element={<TestDetailPage />} />
        <Route path="kontroliniai/generuoti" element={<TestGeneratorPage />} />
        <Route path="ikelti" element={<UploadPage />} />
        <Route path="perziureti" element={<ReviewPage />} />
        <Route path="perziureti/:fileId" element={<WorkReviewPage />} />
        <Route path="greitas-tikrinimas" element={<QuickCheckPage />} />
        <Route path="palyginti/:submissionId" element={<ComparePage />} />
        <Route path="rezultatai" element={<SubmissionsListPage />} />
        <Route path="rezultatai/:submissionId" element={<ResultsPage />} />
        <Route path="statistika" element={<StatisticsPage />} />
        <Route path="eksportai" element={<ExportsPage />} />
        <Route path="sablonai" element={<TemplatesPage />} />
        <Route path="nustatymai" element={<SettingsPage />} />
        <Route path="privatumas" element={<PrivacyPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/prisijungti" element={<LoginPage />} />
      <Route path="/*" element={<ProtectedRoutes />} />
    </Routes>
  );
}

export default App;
