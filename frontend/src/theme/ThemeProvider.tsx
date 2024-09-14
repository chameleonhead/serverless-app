import { createContext, PropsWithChildren, useContext, useState } from 'react';
import {
  createTheme,
  PaletteMode,
  ThemeProvider as MuiThemeProvider,
} from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import getDefaultMode from './getDefaultMode';

type ColorModeValue = {
  mode: PaletteMode;
  changeColorMode: (mode: PaletteMode) => void;
};

const ColorModeContext = createContext({} as ColorModeValue);

export const useColorMode = () => useContext(ColorModeContext);

export default function ThemeProvider({
  children,
}: PropsWithChildren<{ mode?: PaletteMode }>) {
  const [mode, setMode] = useState<PaletteMode>(
    getDefaultMode() as PaletteMode
  );
  const defaultTheme = createTheme({
    palette: { mode },
  });

  const changeColorMode = (newMode: PaletteMode) => {
    setMode(newMode);
    localStorage.setItem('themeMode', newMode);
  };

  return (
    <ColorModeContext.Provider value={{ mode, changeColorMode }}>
      <MuiThemeProvider theme={defaultTheme}>
        <CssBaseline enableColorScheme />
        {children}
      </MuiThemeProvider>
    </ColorModeContext.Provider>
  );
}
