import { useEffect, useState } from "react";

export const useResize = <T>(
  resizeHandler?: () => void,
  dependencies?: T[]
) => {
  const [screenWidth, setScreenWidth] = useState<number | null>(null);

  useEffect(() => {
    const handleResize = () => {
      setScreenWidth(window.innerWidth);
      if (resizeHandler) resizeHandler();
    };

    handleResize();

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, dependencies || []);

  const isMobileView = (screenWidth ?? 0) < 768;
  const isLgView = (screenWidth ?? 0) < 1024;
  const isTabletView = (screenWidth ?? 0) < 640;

  return {
    isMobileView,
    isTabletView,
    isLgView,
  };
};
