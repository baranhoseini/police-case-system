import { Navigate, Route, Routes } from "react-router-dom";

import HomePage from "./HomePage";
import AuthPage from "./AuthPage";
import DashboardPage from "./DashboardPage";
import DetectiveBoardPage from "./DetectiveBoardPage";
import MostWantedPage from "./MostWantedPage";
import CaseComplaintsStatusPage from "./CaseComplaintsStatusPage";
import ReportsPage from "./ReportsPage";
import EvidencePage from "./EvidencePage";
import NotFoundPage from "./NotFoundPage";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<HomePage />} />
      <Route path="/auth" element={<AuthPage />} />
      <Route path="/most-wanted" element={<MostWantedPage />} />

      {/* App (will become protected later) */}
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/detective-board" element={<DetectiveBoardPage />} />
      <Route path="/case-status" element={<CaseComplaintsStatusPage />} />
      <Route path="/reports" element={<ReportsPage />} />
      <Route path="/evidence" element={<EvidencePage />} />

      {/* Redirect example */}
      <Route path="/login" element={<Navigate to="/auth" replace />} />

      {/* 404 */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
