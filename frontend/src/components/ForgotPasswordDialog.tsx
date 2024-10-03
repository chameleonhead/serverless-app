import { FormEvent, useState } from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

export type ForgotPasswordDialogValue = {
  email: string;
};

export type ForgotPasswordDialogProps = {
  open: boolean;
  errorMessage?: string;
  successMessage?: string;
  onSubmit: (value: ForgotPasswordDialogValue) => void;
  onClose: () => void;
};

function ForgotPassword({
  open,
  successMessage,
  errorMessage,
  onSubmit,
  onClose,
}: ForgotPasswordDialogProps) {
  const [emailError, setEmailError] = useState(false);
  const [emailErrorMessage, setEmailErrorMessage] = useState('');

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!validateInputs()) {
      return false;
    }
    const data = new FormData(event.currentTarget);
    await onSubmit({
      email: data.get('email') as string,
    });
  };

  const validateInputs = () => {
    const email = document.getElementById('email') as HTMLInputElement;

    let isValid = true;

    if (!email.value || !/\S+@\S+/.test(email.value)) {
      setEmailError(true);
      setEmailErrorMessage('メールアドレスを入力してください。');
      isValid = false;
    } else {
      setEmailError(false);
      setEmailErrorMessage('');
    }

    return isValid;
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      PaperProps={{
        component: 'form',
        noValidate: true,
        onSubmit: handleSubmit,
      }}
    >
      <DialogTitle>パスワードをリセットする</DialogTitle>
      <DialogContent
        sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: '100%' }}
      >
        <DialogContentText>
          ログイン用のメールアドレスを入力してください。後ほどパスワードをリセットするためのリンクを記載してメールを送信します。
          {successMessage ? (
            <Typography color="success">{successMessage}</Typography>
          ) : null}
          {errorMessage ? (
            <Typography color="error">{errorMessage}</Typography>
          ) : null}
        </DialogContentText>
        <FormControl>
          <FormLabel htmlFor="email">メールアドレス</FormLabel>
          <TextField
            error={emailError}
            helperText={emailErrorMessage}
            id="email"
            type="email"
            name="email"
            placeholder="ログイン用のメールアドレス"
            autoComplete="email"
            autoFocus
            required
            fullWidth
            variant="outlined"
            color={emailError ? 'error' : 'primary'}
            sx={{ ariaLabel: 'email' }}
          />
        </FormControl>
      </DialogContent>
      <DialogActions sx={{ pb: 3, px: 3 }}>
        <Button onClick={onClose}>キャンセル</Button>
        <Button variant="contained" type="submit">
          続ける
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default ForgotPassword;
