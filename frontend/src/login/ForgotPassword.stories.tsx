import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { http, HttpResponse } from 'msw';
import ForgotPassword from './ForgotPassword';
import { AuthContextProvider } from '../auth';

const meta = {
  component: ForgotPassword,
  parameters: {
    layout: 'fullscreen',
  },
  args: {
    onClose: fn(),
  },
  decorators: [(story) => <AuthContextProvider>{story()}</AuthContextProvider>],
} satisfies Meta<typeof ForgotPassword>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    open: true,
  },
  parameters: {
    msw: {
      handlers: [
        http.post('/auth/resetPassword', () => {
          return HttpResponse.json({});
        }),
      ],
    },
  },
};
