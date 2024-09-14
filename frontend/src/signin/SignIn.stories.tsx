import type { Meta, StoryObj } from '@storybook/react';
import {
  createMemoryRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
} from 'react-router-dom';
import { http, HttpResponse } from 'msw';
import SignIn from './SignIn';
import { AuthContextProvider } from '../auth';

const meta = {
  component: SignIn,
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (story) => (
      <AuthContextProvider>
        <RouterProvider
          router={createMemoryRouter(
            createRoutesFromElements(<Route path="/" element={story()} />)
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
