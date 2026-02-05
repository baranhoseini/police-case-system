import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "../components/ProtectedRoute";

import HomePage from "./HomePage";
import AuthPage from "./AuthPage";
import DashboardPage from "./DashboardPage";
import DetectiveBoardPage from "./DetectiveBoardPage";
import MostWantedPage from "./MostWantedPage";
import CaseComplaintsStatusPage from "./CaseComplaintsStatusPage";
import ReportsPage from "./ReportsPage";
import EvidencePage from "./EvidencePage";
import NotFoundPage from "./NotFoundPage";
import CasesPage from "./CasesPage";
import CaseDetailsPage from "./CaseDetailsPage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/auth" element={<AuthPage />} />
      <Route path="/most-wanted" element={<MostWantedPage />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/detective-board"
        element={
          <ProtectedRoute>
            <DetectiveBoardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/case-status"
        element={
          <ProtectedRoute>
            <CaseComplaintsStatusPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <ReportsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/evidence"
        element={
          <ProtectedRoute>
            <EvidencePage />
          </ProtectedRoute>
        }
      />

      <Route path="/login" element={<Navigate to="/auth" replace />} />
      <Route path="*" element={<NotFoundPage />} />

      <Route
        path="/cases"
        element={
          <ProtectedRoute>
            <CasesPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/cases/:caseId"
        element={
          <ProtectedRoute>
            <CaseDetailsPage />
          </ProtectedRoute>
        }
      />

    </Routes>
  );
}
