import { Zap } from "lucide-react";
import { Suspense } from "react";
import { Outlet } from "react-router-dom";

const RootPage = () => {
  return (
    <Suspense
      fallback={
        <div className="h-screen w-full flex items-center justify-center">
          <Zap className="h-6 w-6 text-blue-500 animate-ping" />
        </div>
      }
    >
      <div className="h-screen relative">
        <main className="w-full h-full">
          <Outlet />
        </main>
      </div>
    </Suspense>
  );
};

export default RootPage;
