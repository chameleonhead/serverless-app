import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';

import SignIn from './SignIn';

const meta = {
    component: SignIn,
    parameters: {
        layout: 'fullscreen',
    },
    args: {
        onLogin: fn(),
    },
} satisfies Meta<typeof SignIn>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
};
