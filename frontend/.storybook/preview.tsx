import type { Preview } from '@storybook/react';
import { initialize, mswLoader } from 'msw-storybook-addon';
import ColorModeProvider from '../src/theme/ColorModeProvider';

const preview: Preview = {
  beforeAll: () => {
    initialize();
  },
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
  loaders: [mswLoader],
  decorators: [(story) => <ColorModeProvider>{story()} </ColorModeProvider>],
};

export default preview;
