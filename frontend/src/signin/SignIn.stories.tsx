import type { Meta, StoryObj } from '@storybook/react';
import {
  createMemoryRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
} from 'react-router-dom';
import SignIn from './SignIn';

const meta = {
  component: SignIn,
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (story) => (
      <RouterProvider
        router={createMemoryRouter(
          createRoutesFromElements(<Route path="/" element={story()} />)
        )}
      />
    ),
  ],
} satisfies Meta<typeof SignIn>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
