#!/bin/bash
set -e

echo "🚀 Setting up Attendance Management Frontend..."

cd /Users/ajayifam/Documents/ZitiAcademy/Attendance/frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install @tanstack/react-query zustand axios react-hook-form zod @hookform/resolvers nookies

# Create .env.local
echo "⚙️  Creating environment file..."
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_BASE_URL=http://localhost:5001/api
EOF

# Update next.config
echo "📝 Updating Next.js config..."
cat > next.config.ts << 'EOF'
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
EOF

# Create lib directory and axios client
echo "🔧 Creating API client..."
mkdir -p src/lib/api
cat > src/lib/axios.ts << 'EOF'
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = document.cookie
      .split("; ")
      .find((row) => row.startsWith("access_token="))
      ?.split("=")[1];
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export default api;
EOF

# Create store directory and auth store
echo "🗄️  Creating Zustand store..."
mkdir -p src/store
cat > src/store/auth.ts << 'EOF'
import { create } from "zustand";

type Role = "admin" | "teacher" | "student";
type User = {
  id: number;
  email: string;
  username: string;
  role: Role;
};

type AuthState = {
  token?: string;
  user?: User;
  login: (token: string, user: User) => void;
  logout: () => void;
};

export const useAuth = create<AuthState>((set) => ({
  token: undefined,
  user: undefined,
  login: (token, user) => {
    document.cookie = `access_token=${token}; path=/; max-age=${60 * 60 * 8}`;
    set({ token, user });
  },
  logout: () => {
    document.cookie = "access_token=; path=/; max-age=0";
    set({ token: undefined, user: undefined });
  },
}));
EOF

# Create API client functions
cat > src/lib/api/auth.ts << 'EOF'
import api from "../axios";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  data: {
    access_token: string;
    user: {
      id: number;
      email: string;
      username: string;
      role: string;
    };
  };
}

export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>("/auth/login", data);
  return response.data;
};

export const getProfile = async () => {
  const response = await api.get("/auth/me");
  return response.data;
};

export const logout = async () => {
  return api.post("/auth/logout");
};
EOF

cat > src/lib/api/courses.ts << 'EOF'
import api from "../axios";

export const getCourses = async (page = 1, perPage = 20) => {
  const response = await api.get(`/courses?page=${page}&per_page=${perPage}`);
  return response.data;
};

export const getCourse = async (id: number) => {
  const response = await api.get(`/courses/${id}`);
  return response.data;
};
EOF

# Create providers
echo "🎨 Creating React Query provider..."
cat > src/app/providers.tsx << 'EOF'
"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";

export default function Providers({ children }: { children: ReactNode }) {
  const [client] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
      },
    },
  }));
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
EOF

# Update layout
cat > src/app/layout.tsx << 'EOF'
import type { Metadata } from "next";
import "./globals.css";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "ZitiAcademy Attendance",
  description: "Course attendance management system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
EOF

# Create home page
cat > src/app/page.tsx << 'EOF'
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center space-y-6 p-8">
        <h1 className="text-5xl font-bold text-gray-900">
          ZitiAcademy Attendance
        </h1>
        <p className="text-xl text-gray-600">
          Modern course attendance management system
        </p>
        <div className="flex gap-4 justify-center mt-8">
          <Link
            href="/login"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Login
          </Link>
          <Link
            href="/dashboard"
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
          >
            Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
EOF

# Create login page
mkdir -p src/app/login
cat > src/app/login/page.tsx << 'EOF'
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../store/auth";
import { login as loginApi } from "../../lib/api/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const loginStore = useAuth((s) => s.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await loginApi({ email, password });
      loginStore(response.data.access_token, response.data.user);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="text-3xl font-bold text-center text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="admin@zitiacademy.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </div>

          <div className="text-sm text-gray-600 text-center">
            <p>Demo credentials:</p>
            <p className="mt-1">Admin: admin@zitiacademy.com / admin123</p>
            <p>Teacher: teacher@zitiacademy.com / teacher123</p>
            <p>Student: student1@zitiacademy.com / student123</p>
          </div>
        </form>
      </div>
    </div>
  );
}
EOF

# Create dashboard
mkdir -p src/app/dashboard
cat > src/app/dashboard/page.tsx << 'EOF'
"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../store/auth";
import { getCourses } from "../../lib/api/courses";
import { useQuery } from "@tanstack/react-query";

export default function DashboardPage() {
  const user = useAuth((s) => s.user);
  const logout = useAuth((s) => s.logout);
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  const { data: coursesData, isLoading } = useQuery({
    queryKey: ["courses"],
    queryFn: () => getCourses(),
    enabled: !!user,
  });

  useEffect(() => {
    setMounted(true);
    if (!user) {
      router.push("/login");
    }
  }, [user, router]);

  if (!mounted || !user) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">ZitiAcademy Attendance</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700">
                {user.username} ({user.role})
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
            <p className="mt-1 text-sm text-gray-600">
              Welcome back, {user.username}!
            </p>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Your Courses
            </h3>
            {isLoading ? (
              <p className="text-gray-500">Loading courses...</p>
            ) : coursesData?.data?.items?.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {coursesData.data.items.map((course: any) => (
                  <div
                    key={course.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
                  >
                    <h4 className="font-semibold text-gray-900">{course.name}</h4>
                    <p className="text-sm text-gray-600 mt-1">{course.code}</p>
                    <p className="text-xs text-gray-500 mt-2">
                      {course.semester} {course.year}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No courses found</p>
            )}
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-blue-900">Role</h3>
              <p className="text-3xl font-bold text-blue-600 mt-2 uppercase">
                {user.role}
              </p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-green-900">Status</h3>
              <p className="text-3xl font-bold text-green-600 mt-2">Active</p>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-purple-900">Courses</h3>
              <p className="text-3xl font-bold text-purple-600 mt-2">
                {coursesData?.data?.items?.length || 0}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
EOF

# Create middleware
cat > src/middleware.ts << 'EOF'
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(req: NextRequest) {
  const token = req.cookies.get("access_token")?.value;
  const isLoginPage = req.nextUrl.pathname === "/login";
  const isDashboard = req.nextUrl.pathname.startsWith("/dashboard");

  if (!token && isDashboard) {
    return NextResponse.redirect(new URL("/login", req.url));
  }

  if (token && isLoginPage) {
    return NextResponse.redirect(new URL("/dashboard", req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login"],
};
EOF

# Create Dockerfile
echo "🐳 Creating Dockerfile..."
cat > Dockerfile << 'EOF'
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:5001/api
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
EOF

# Create .dockerignore
cat > .dockerignore << 'EOF'
node_modules
.next
.git
.gitignore
.env.local
README.md
.DS_Store
EOF

echo "✅ Frontend setup complete!"
echo ""
echo "To start development:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Backend should be running on http://localhost:5001"
echo "Frontend will run on http://localhost:3000"
