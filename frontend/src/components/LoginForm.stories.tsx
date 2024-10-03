import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import LoginForm from './LoginForm';

const meta = {
  component: LoginForm,
  args: {
    onSubmit: fn(),
    onForgotPasswordClick: fn(),
  },
} satisfies Meta<typeof LoginForm>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
