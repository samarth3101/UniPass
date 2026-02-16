"use client";

import { useEffect, useState, useRef } from "react";
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
  const redirecting = useRef(false);

  useEffect(() => {
    // Prevent multiple redirects
    if (redirecting.current) return;
    
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
        // Don't redirect if already on login page
        if (pathname !== "/login") {
          redirecting.current = true;
          router.replace("/login");
        }
        setIsChecking(false);
        return;
      }

      // Check if user has permission to access current route
      const hasAccess = canAccessRoute(pathname);

      if (!hasAccess) {
        const redirectPath = getRedirectForRole(pathname);
        if (pathname !== redirectPath) {
          redirecting.current = true;
          router.replace(redirectPath);
        }
        setIsChecking(false);
        return;
      }

      // User is authenticated and has access
      setIsAuthorized(true);
      setIsChecking(false);
    }

    checkAccess();
  }, [pathname, router]);

  // Show loading state while checking
  if (isChecking) {
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

  // If not authorized, show nothing (redirect is in progress)
  if (!isAuthorized) {
    return null;
  }

  return <>{children}</>;
}
