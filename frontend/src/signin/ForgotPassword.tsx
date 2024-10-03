import { useAuth } from '../auth';
import { useEffect, useState } from 'react';
import ForgotPasswordDialog, {
  ForgotPasswordDialogValue,
} from '../components/ForgotPasswordDialog';

interface ForgotPasswordProps {
  open: boolean;
  onClose: () => void;
}

export default function ForgotPassword({ open, onClose }: ForgotPasswordProps) {
  const { resetPassword } = useAuth();
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (!open) {
      setSuccessMessage('');
    }
  }, [open]);

  const handleSubmit = async (value: ForgotPasswordDialogValue) => {
    await resetPassword(value);
    setSuccessMessage('リセット用のメールを送信しました。');
    onClose();
  };
  return (
    <ForgotPasswordDialog
      open={open}
      successMessage={successMessage}
      onSubmit={handleSubmit}
      onClose={onClose}
    />
  );
}
