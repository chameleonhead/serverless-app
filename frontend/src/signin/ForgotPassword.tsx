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
import { useAuth } from '../auth';
import { useEffect, useState } from 'react';

interface ForgotPasswordProps {
  open: boolean;
  handleClose: () => void;
}

export default function ForgotPassword({
  open,
  handleClose,
}: ForgotPasswordProps) {
  const { resetPassword } = useAuth();
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (!open) {
      setSuccessMessage('');
    }
  }, [open]);
  return (
    <Dialog
      open={open}
      onClose={handleClose}
      PaperProps={{
        component: 'form',
        onSubmit: async (event: React.FormEvent<HTMLFormElement>) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          await resetPassword({
            email: data.get('email') as string,
          });
          handleClose();
        },
      }}
    >
      <DialogTitle>パスワードをリセットする</DialogTitle>
      <DialogContent
        sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: '100%' }}
      >
        <DialogContentText>
          ログイン用のメールアドレスを入力してください。後ほどパスワードをリセットするためのリンクを記載してメールを送信します。
          {successMessage ? <Typography>{successMessage}</Typography> : null}
        </DialogContentText>
        <FormControl>
          <FormLabel htmlFor="email">メールアドレス</FormLabel>
          <TextField
            id="email"
            type="email"
            name="email"
            placeholder="ログイン用のメールアドレス"
            autoComplete="email"
            autoFocus
            required
            fullWidth
            variant="outlined"
            color={'primary'}
            sx={{ ariaLabel: 'email' }}
          />
        </FormControl>
      </DialogContent>
      <DialogActions sx={{ pb: 3, px: 3 }}>
        <Button onClick={handleClose}>キャンセル</Button>
        <Button variant="contained" type="submit">
          続ける
        </Button>
      </DialogActions>
    </Dialog>
  );
}
