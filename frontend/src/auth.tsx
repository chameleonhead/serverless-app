import {
  createContext,
  PropsWithChildren,
  useContext,
  useEffect,
  useState,
} from 'react';

export class LoginFailedError extends Error {}
export class UnauthorizedError extends Error {}

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

type Tokens = {
  id_token: string;
  access_token: string;
};

type SessionResponse = {
  session: Tokens;
};

async function login({
  username,
  password,
}: LoginParam): Promise<SessionResponse> {
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

  return await response.json();
}

async function session(): Promise<SessionResponse> {
  const response = await fetch('/auth/session');

  if (!response.ok) {
    switch (response.status) {
      case 401:
        throw new UnauthorizedError();
      default:
        throw new Error('Session failed.');
    }
  }

  return await response.json();
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
  session: () => Promise<void>;
  logout: () => Promise<void>;
  resetPassword: (request: ResetPasswordParam) => Promise<void>;
};

const AuthContext = createContext({} as AuthContextValue);

export const AuthContextProvider = ({ children }: PropsWithChildren) => {
  const [sessionResponse, setSessionResponse] =
    useState<SessionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (loading) {
      session()
        .then((session) => {
          setSessionResponse(session);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [loading]);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!sessionResponse,
        login: async (req) => {
          const response = await login(req);
          setSessionResponse(response);
        },
        session: async () => {
          const response = await session();
          setSessionResponse(response);
        },
        logout: async () => {
          await logout();
          setSessionResponse(null);
        },
        resetPassword: resetPassword,
      }}
    >
      {loading ? null : children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);
