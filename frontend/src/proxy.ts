import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = [
  "/dashboard",
  "/events",
  "/attendance",
  "/scan",
];

export default function proxy(request: NextRequest){
  const token = request.cookies.get("unipass_token")?.value;
  const { pathname } = request.nextUrl;

  // Public routes
  if (pathname === "/" || pathname.startsWith("/_next")) {
    return NextResponse.next();
  }

  const isProtected = protectedRoutes.some(route =>
    pathname.startsWith(route)
  );

  // 🚫 Block protected routes if not logged in
  if (isProtected && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // 🔁 Prevent logged-in users from seeing auth pages
  if (token && (pathname === "/login" || pathname === "/signup")) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/login",
    "/signup",
    "/dashboard/:path*",
    "/events/:path*",
    "/attendance/:path*",
    "/scan/:path*",
  ],
};