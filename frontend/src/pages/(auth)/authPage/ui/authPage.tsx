import { Outlet } from "react-router-dom";

const AuthPage = () => {
  return (
    <div className="h-full w-full flex-col items-center justify-between p-4">
      <div className="h-full flex items-center justify-between">
        <Outlet />
      </div>
    </div>
  );
};

export default AuthPage;
