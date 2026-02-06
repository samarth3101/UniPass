import Sidebar from "./sidebar";
import Topbar from "./topbar";
import RoleGuard from "@/components/RoleGuard";
import "./app-layout.scss";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RoleGuard>
      <div className="app-shell">
        <Sidebar />
        <div className="main-area">
          <Topbar />
          <div className="page-content">{children}</div>
        </div>
      </div>
    </RoleGuard>
  );
}