import type { Meta, StoryObj } from '@storybook/react';
import {
  createMemoryRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
} from 'react-router-dom';
import { http, HttpResponse } from 'msw';
import SignIn from './SignIn';
import { AuthContextProvider, useAuth } from '../auth';
import Guard from '../routes/guard';
import Button from '@mui/material/Button';

function LggedIn() {
  const { logout } = useAuth()
  return (
    <Button onClick={logout}>Logout</Button>
  )
}

const meta = {
  component: SignIn,
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (story: any) => (
      <AuthContextProvider>
        <RouterProvider
          router={createMemoryRouter(
            createRoutesFromElements(
              <Route>
                <Route element={<Guard />}>
                  <Route path="*" element={<LggedIn />} />
                </Route>
                <Route path="/login" element={story()} />
              </Route>)
          )}
        />
      </AuthContextProvider>
    ),
  ],
} satisfies Meta<typeof SignIn>;

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


export const SignedIn: Story = {
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
