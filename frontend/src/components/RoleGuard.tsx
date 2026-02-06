"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { isAuthenticated, getUser } from "@/lib/auth";
import { canAccessRoute, getRedirectForRole, isPublicRoute } from "@/lib/roleGuard";

interface RoleGuardProps {
  children: React.ReactNode;
}

/**
 * RoleGuard Component
 * Protects routes based on user authentication and role permissions
 * Redirects unauthorized users to appropriate pages
 */
export default function RoleGuard({ children }: RoleGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    async function checkAccess() {
      // Check if route is public (no auth required)
      if (isPublicRoute(pathname)) {
        setIsAuthorized(true);
        setIsChecking(false);
        return;
      }

      // Check if user is authenticated
      const authenticated = isAuthenticated();
      const user = getUser();

      if (!authenticated) {
        setIsChecking(false);
        router.push("/login");
        return;
      }

      // Check if user has permission to access current route
      const hasAccess = canAccessRoute(pathname);

      if (!hasAccess) {
        setIsChecking(false);
        const redirectPath = getRedirectForRole(pathname);
        router.push(redirectPath);
        return;
      }

      // User is authenticated and has access
      setIsAuthorized(true);
      setIsChecking(false);
    }

    checkAccess();
  }, [pathname, router]);

  // Show loading state while checking
  if (isChecking || !isAuthorized) {
    return (
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        fontSize: "1.2rem",
        color: "#64748b"
      }}>
        Checking permissions...
      </div>
    );
  }

  return <>{children}</>;
}
