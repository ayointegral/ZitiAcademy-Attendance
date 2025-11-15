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
