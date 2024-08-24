import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import App from './App';

describe('render', () => {
  it('renders the main page', () => {
    render(<App />);
    expect(true).toBeTruthy();
  });
});
