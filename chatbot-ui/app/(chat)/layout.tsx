import { cookies } from "next/headers";

import { AppSidebar } from "@/components/app-sidebar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { User } from "next-auth";

export const experimental_ppr = true;

export default async function Layout({
  children,
}: {
  children: React.ReactNode;
}) {
  const cookieStore = await cookies();
  const isCollapsed = cookieStore.get("sidebar:state")?.value !== "true";
  const dummyUser: User = {
    id: "dc421967-25ff-45b8-9c1a-fbc69e441af7",
    name: "AI Chatbot",
    email: "ai-chatbot@example.com"
  }

  return (
    <SidebarProvider defaultOpen={!isCollapsed}>
      <AppSidebar user={dummyUser} />
      <SidebarInset>{children}</SidebarInset>
    </SidebarProvider>
  );
}
