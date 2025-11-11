import { ViewerProvider } from "@/entities/viewer/model/context/providers";
import { routes } from "@/pages/routes";
import { queryClient } from "@/shared/api/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";
import { ModalProvider as ModalContextProvider } from "@/shared/lib/modal/context";
import { ModalProvider } from "../modal/modalProvider";
import { ChatCollapseProvider } from "../chatCollapse";

export const Providers = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ViewerProvider>
        <ModalContextProvider>
          <ChatCollapseProvider>
            <RouterProvider router={routes} />
            <ModalProvider />
          </ChatCollapseProvider>
        </ModalContextProvider>
      </ViewerProvider>
    </QueryClientProvider>
  );
};
