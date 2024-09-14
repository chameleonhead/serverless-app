export default function getDefaultMode() {
  const savedMode = localStorage.getItem('themeMode');
  if (savedMode) {
    return savedMode;
  } else {
    const systemPrefersDark = window.matchMedia(
      '(prefers-color-scheme: dark)'
    ).matches;
    return systemPrefersDark ? 'dark' : 'light';
  }
}
