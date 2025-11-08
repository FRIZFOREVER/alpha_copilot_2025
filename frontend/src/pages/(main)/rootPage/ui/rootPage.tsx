import { Image } from "@/shared/ui/image/image";
import { Suspense } from "react";
import { Outlet } from "react-router-dom";

const RootPage = () => {
  return (
    <Suspense
      fallback={
        <div className="h-screen w-full flex items-center justify-center">
          <Image
            alt="logo-suspense"
            src="/images/logo.jpg"
            className="w-6 h-6 rounded-sm animate-ping"
          />
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
