import { PaletteMode } from '@mui/material/styles';

export default function getDefaultMode(): PaletteMode {
  const savedMode = localStorage.getItem('themeMode');
  if (savedMode) {
    return savedMode as PaletteMode;
  } else {
    const systemPrefersDark = window.matchMedia(
      '(prefers-color-scheme: dark)'
    ).matches;
    return systemPrefersDark ? 'dark' : 'light';
  }
}
