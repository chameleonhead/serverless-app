import { PaletteMode } from '@mui/material/styles';

export default function getDefaultMode() {
  const savedMode = localStorage.getItem('themeMode') as PaletteMode | null;
  if (savedMode) {
    return savedMode;
  } else {
    const systemPrefersDark = window.matchMedia(
      '(prefers-color-scheme: dark)'
    ).matches;
    return systemPrefersDark ? 'dark' : 'light';
  }
}
