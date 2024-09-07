import {
  createContext,
  PropsWithChildren,
  useContext,
  useEffect,
  useState,
} from 'react';

export class LoginFailedError extends Error {}

const hashPayload = async (payload: string) => {
  const encoder = new TextEncoder().encode(payload);
  const hash = await crypto.subtle.digest('SHA-256', encoder);
  const hashArray = Array.from(new Uint8Array(hash));
  return hashArray.map((bytes) => bytes.toString(16).padStart(2, '0')).join('');
};

export async function login({
  username,
  password,
}: {
  username: string;
  password: string;
}) {
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

const AuthContext = createContext({
  isAuthenticated: false,
  login: async (_: Parameters<typeof login>[0]) => {},
});

export const AuthContextProvider = ({ children }: PropsWithChildren) => {
  const [isAuthenticated, setAuthenticated] = useState<boolean>(false);
  useEffect(() => {
    if (!isAuthenticated) {
      login({ username: 'user@example.com', password: 'P@ssw0rd' }).then(() =>
        setAuthenticated(true)
      );
    }
  });
  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        login: async (req) => {
          await login(req);
          setAuthenticated(true);
        },
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
