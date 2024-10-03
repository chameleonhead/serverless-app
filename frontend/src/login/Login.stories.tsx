import type { Meta, StoryObj } from '@storybook/react';
import {
  createMemoryRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
} from 'react-router-dom';
import { http, HttpResponse } from 'msw';
import Login from './Login';
import { AuthContextProvider, useAuth } from '../auth';
import Guard from '../routes/guard';
import Button from '@mui/material/Button';
import Layout from '../components/Layout';

function LggedIn() {
  const { logout } = useAuth();
  return (
    <Layout>
      <Button onClick={logout}>Logout</Button>
    </Layout>
  );
}

const meta = {
  component: Login,
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (story) => (
      <AuthContextProvider>
        <RouterProvider
          router={createMemoryRouter(
            createRoutesFromElements(
              <Route>
                <Route element={<Guard />}>
                  <Route path="*" element={<LggedIn />} />
                </Route>
                <Route path="/login" element={story()} />
              </Route>
            )
          )}
        />
      </AuthContextProvider>
    ),
  ],
} satisfies Meta<typeof Login>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  parameters: {
    msw: {
      handlers: [
        http.post('/auth/login', () => {
          return HttpResponse.json({});
        }),
        http.post('/auth/logout', () => {
          return HttpResponse.json({});
        }),
      ],
    },
  },
};

export const LoggedIn: Story = {
  parameters: {
    msw: {
      handlers: [
        http.post('/auth/login', () => {
          return HttpResponse.json({});
        }),
        http.get('/auth/session', () => {
          return HttpResponse.json({});
        }),
        http.post('/auth/logout', () => {
          return HttpResponse.json({});
        }),
      ],
    },
  },
};
