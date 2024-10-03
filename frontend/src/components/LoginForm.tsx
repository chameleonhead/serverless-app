import { FormEvent, useState } from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormLabel from '@mui/material/FormLabel';
import FormControl from '@mui/material/FormControl';
import Link from '@mui/material/Link';
import TextField from '@mui/material/TextField';

export type LoginFormValue = {
  username: string;
  password: string;
  remember: boolean;
};

export type LoginFormProps = {
  onSubmit: (value: LoginFormValue) => void;
  onForgotPasswordClick: () => void;
};

function LoginForm({ onSubmit, onForgotPasswordClick }: LoginFormProps) {
  const [emailError, setEmailError] = useState(false);
  const [emailErrorMessage, setEmailErrorMessage] = useState('');
  const [passwordError, setPasswordError] = useState(false);
  const [passwordErrorMessage, setPasswordErrorMessage] = useState('');

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!validateInputs()) {
      return false;
    }
    const data = new FormData(event.currentTarget);
    await onSubmit({
      username: data.get('email') as string,
      password: data.get('password') as string,
      remember: data.get('remember') == '1',
    });
  };

  const validateInputs = () => {
    const email = document.getElementById('email') as HTMLInputElement;
    const password = document.getElementById('password') as HTMLInputElement;

    let isValid = true;

    if (!email.value || !/\S+@\S+/.test(email.value)) {
      setEmailError(true);
      setEmailErrorMessage('メールアドレスを入力してください。');
      isValid = false;
    } else {
      setEmailError(false);
      setEmailErrorMessage('');
    }

    if (!password.value) {
      setPasswordError(true);
      setPasswordErrorMessage('パスワードを入力して下さい。');
      isValid = false;
    } else {
      setPasswordError(false);
      setPasswordErrorMessage('');
    }

    return isValid;
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      noValidate
      sx={(theme) => ({
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        gap: theme.spacing(2),
      })}
    >
      <FormControl>
        <FormLabel htmlFor="email">メールアドレス</FormLabel>
        <TextField
          error={emailError}
          helperText={emailErrorMessage}
          id="email"
          type="email"
          name="email"
          placeholder="your@email.com"
          autoComplete="email"
          autoFocus
          required
          fullWidth
          variant="outlined"
          color={emailError ? 'error' : 'primary'}
          sx={{ ariaLabel: 'email' }}
        />
      </FormControl>
      <FormControl>
        <FormLabel htmlFor="password">パスワード</FormLabel>
        <TextField
          error={passwordError}
          helperText={passwordErrorMessage}
          name="password"
          placeholder="••••••"
          type="password"
          id="password"
          autoComplete="current-password"
          autoFocus
          required
          fullWidth
          variant="outlined"
          color={passwordError ? 'error' : 'primary'}
        />
      </FormControl>
      <FormControlLabel
        control={<Checkbox value="remember" color="primary" />}
        label="ログイン状態を記録する"
      />
      <Button type="submit" fullWidth variant="contained">
        ログイン
      </Button>
      <Link
        component="button"
        type="button"
        onClick={onForgotPasswordClick}
        variant="body2"
        sx={{ alignSelf: 'baseline' }}
        tabIndex={-1}
      >
        パスワードをお忘れですか？
      </Link>
    </Box>
  );
}

export default LoginForm;
