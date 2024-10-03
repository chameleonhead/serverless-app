import { useState } from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import MuiCard from '@mui/material/Card';
import { styled } from '@mui/material/styles';
import { Navigate, useNavigation } from 'react-router-dom';
import ForgotPassword from './ForgotPassword';
import { GoogleIcon, LogoIcon } from './CustomIcons';
import Layout from '../components/Layout';
import { useAuth } from '../auth';
import { useColorMode } from '../theme/ColorModeProvider';
import ToggleColorMode from '../theme/ToggleColorMode';
import LoginForm, { LoginFormValue } from '../components/LoginForm';

const Card = styled(MuiCard)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignSelf: 'center',
  width: '100%',
  padding: theme.spacing(2),
  gap: theme.spacing(2),
  margin: 'auto',
  [theme.breakpoints.up('sm')]: {
    maxWidth: '450px',
    padding: theme.spacing(4),
    gap: theme.spacing(2),
  },
  boxShadow:
    'hsla(220, 30%, 5%, 0.05) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.05) 0px 15px 35px -5px',
  ...theme.applyStyles('dark', {
    boxShadow:
      'hsla(220, 30%, 5%, 0.5) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.08) 0px 15px 35px -5px',
  }),
}));

const SignInContainer = styled(Stack)(({ theme }) => ({
  padding: theme.spacing(1),
  backgroundColor: 'hsl(0, 0%, 100%))',
  ...theme.applyStyles('dark', {
    backgroundColor: 'hsl(220, 30%, 5%))',
  }),
  [theme.breakpoints.up('sm')]: {
    padding: theme.spacing(4),
  },
}));

export default function SignIn() {
  const [open, setOpen] = useState(false);
  const { isAuthenticated, login } = useAuth();
  const { mode, changeColorMode } = useColorMode();
  const navigation = useNavigation();

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleSubmit = async (value: LoginFormValue) => {
    await login(value);
  };

  if (isAuthenticated) {
    return <Navigate to={navigation.location?.state || '/'} replace />;
  }

  return (
    <Layout>
      <SignInContainer direction="column" justifyContent="space-between">
        <Card variant="outlined">
          <Box
            sx={{
              pb: 1,
              display: 'flex',
              justifyContent: 'space-between',
              justifyItems: 'flex-start',
            }}
          >
            <LogoIcon />
            <ToggleColorMode
              mode={mode}
              toggleColorMode={() =>
                changeColorMode(mode == 'dark' ? 'light' : 'dark')
              }
            />
          </Box>
          <Typography
            component="h1"
            variant="h4"
            sx={{ width: '100%', fontSize: 'clamp(2rem, 10vw, 2.15rem)' }}
          >
            ログイン
          </Typography>
          <LoginForm
            onSubmit={handleSubmit}
            onForgotPasswordClick={handleClickOpen}
          />
          <ForgotPassword open={open} onClose={handleClose} />
          <Divider>or</Divider>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Button
              type="submit"
              fullWidth
              variant="outlined"
              onClick={() => alert('Sign in with Google')}
              startIcon={<GoogleIcon />}
            >
              Sign in with Google
            </Button>
          </Box>
        </Card>
      </SignInContainer>
    </Layout>
  );
}
