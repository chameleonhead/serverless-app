import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import ForgotPasswordDialog from './ForgotPasswordDialog';

const meta = {
  component: ForgotPasswordDialog,
  args: {
    onSubmit: fn(),
    onClose: fn(),
  },
} satisfies Meta<typeof ForgotPasswordDialog>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    open: true,
  },
};

export const Success: Story = {
  args: {
    open: true,
    successMessage: 'Success Message',
  },
};

export const Error: Story = {
  args: {
    open: true,
    errorMessage: 'Error Message',
  },
};
