import { Navigate, Outlet, useNavigation } from 'react-router-dom';
import { useAuth } from '../auth';

function Guard() {
  const { isAuthenticated } = useAuth();
  const navigation = useNavigation();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={navigation.location} />;
  }
  return <Outlet />;
}

export default Guard;
