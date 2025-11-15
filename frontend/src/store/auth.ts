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
