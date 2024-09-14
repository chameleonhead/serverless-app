import { ReactNode } from 'react';
import { styled } from '@mui/material/styles';
import MuiAppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import ToggleColorMode from './ToggleColorMode';
import { useColorMode } from './ThemeProvider';

const StyledAppBar = styled(MuiAppBar)(({ theme }) => ({
  position: 'relative',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  flexShrink: 0,
  borderBottom: '1px solid',
  borderColor: theme.palette.divider,
  backgroundColor: theme.palette.background.paper,
  boxShadow: 'none',
  backgroundImage: 'none',
  zIndex: theme.zIndex.drawer + 1,
  flex: '0 0 auto',
}));

interface AppBarProps {
  children: ReactNode;
}

export default function AppBar({}: AppBarProps) {
  const { mode, changeColorMode } = useColorMode();

  const toggleColorMode = () => {
    const newMode = mode === 'dark' ? 'light' : 'dark';
    changeColorMode(newMode);
  };

  return (
    <StyledAppBar>
      <Toolbar
        variant="dense"
        disableGutters
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          width: '100%',
          p: '8px 12px',
        }}
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          <ToggleColorMode
            data-screenshot="toggle-mode"
            mode={mode}
            toggleColorMode={toggleColorMode}
          />
        </Box>
      </Toolbar>
    </StyledAppBar>
  );
}
