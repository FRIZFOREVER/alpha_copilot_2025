import { Sidebar } from "@/widgets/sidebar";
import { Outlet } from "react-router-dom";

const DashboardPage = () => {
  return (
    <div className="flex h-full w-full">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden border-l border-sidebar-border">
        <Outlet />
      </div>
    </div>
  );
};

export default DashboardPage;
