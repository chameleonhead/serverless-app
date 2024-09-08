import { createContext, PropsWithChildren, useContext, useState } from 'react';

export class LoginFailedError extends Error {}

const hashPayload = async (payload: string) => {
  const encoder = new TextEncoder().encode(payload);
  const hash = await crypto.subtle.digest('SHA-256', encoder);
  const hashArray = Array.from(new Uint8Array(hash));
  return hashArray.map((bytes) => bytes.toString(16).padStart(2, '0')).join('');
};

type LoginParam = {
  username: string;
  password: string;
};

type ResetPasswordParam = {
  email: string;
};

async function login({ username, password }: LoginParam) {
  const requestBody = JSON.stringify({ username, password });
  const sha256hash = await hashPayload(requestBody);

  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-amz-content-sha256': sha256hash,
    },
    body: requestBody,
  });

  if (!response.ok) {
    switch (response.status) {
      case 403:
        throw new LoginFailedError('Wrong username or password.');
      default:
        throw new Error('Login failed.');
    }
  }
}

async function logout() {
  const response = await fetch('/auth/logout', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    switch (response.status) {
      default:
        throw new Error('Logout failed.');
    }
  }
}

async function resetPassword({ email }: ResetPasswordParam) {
  const requestBody = JSON.stringify({ email });
  const sha256hash = await hashPayload(requestBody);

  const response = await fetch('/auth/resetPassword', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-amz-content-sha256': sha256hash,
    },
    body: requestBody,
  });

  if (!response.ok) {
    switch (response.status) {
      default:
        throw new Error('Reset password failed.');
    }
  }
}

type AuthContextValue = {
  isAuthenticated: boolean;
  login: (request: LoginParam) => Promise<void>;
  logout: () => Promise<void>;
  resetPassword: (request: ResetPasswordParam) => Promise<void>;
};

const AuthContext = createContext({} as AuthContextValue);

export const AuthContextProvider = ({ children }: PropsWithChildren) => {
  const [isAuthenticated, setAuthenticated] = useState<boolean>(false);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        login: async (req) => {
          await login(req);
          setAuthenticated(true);
        },
        logout: async () => {
          await logout();
          setAuthenticated(false);
        },
        resetPassword: resetPassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);
